"""Phase 4 : tests des endpoints métier inventory & supervision (hors RBAC déjà couvert).

Le volet « qui a le droit d'appeler » est traité par test_etape3_auth.py ; ici
on valide le comportement fonctionnel : lecture filtrée, création, 404 explicite,
recalcul de santé et calcul de TTF avec/sans données.
"""
import pytest
from datetime import timedelta
from fastapi import FastAPI
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.api.v1.router import api_router
from app.core.database import Base, get_db
from app.core.security import create_access_token, hash_password
from app.core.time_utils import utcnow_naive
from app.models.models import AuditReseau, Equipement, Metrique, Utilisateur

API = "/api/v1"


@pytest.fixture()
def env():
    engine = create_engine("sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool)
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    with Session() as s:
        s.add_all([
            Utilisateur(identifiant="tech", hash_mot_de_passe=hash_password("x"), role="Technicien"),
            Utilisateur(identifiant="visiteur", hash_mot_de_passe=hash_password("x"), role="Visiteur"),
        ])
        s.add(Equipement(nom="SRV-APP-01", ip="192.168.20.12", type="Serveur", health_score=100.0))
        s.add(Equipement(nom="SW-CORE-01", ip="192.168.10.1", type="Switch", health_score=100.0))
        s.commit()
        srv = s.query(Equipement).filter_by(nom="SRV-APP-01").first()
        now = utcnow_naive()
        for i in range(3):
            s.add(Metrique(equipement_id=srv.id, type_metrique="disk_percent", valeur=50.0 + i,
                           horodatage=now - timedelta(minutes=10 - i)))
            s.add(Metrique(equipement_id=srv.id, type_metrique="cpu_percent", valeur=10.0,
                           horodatage=now - timedelta(minutes=10 - i)))
        s.commit()

    app = FastAPI()
    app.include_router(api_router, prefix=API)

    def override_get_db():
        db = Session()
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = override_get_db
    yield TestClient(app), Session


def h(identifiant="tech", role="Technicien"):
    return {"Authorization": f"Bearer {create_access_token({'sub': identifiant, 'role': role})}"}


# ----------------------------------------------------------------- inventory

def test_list_and_get_equipements(env):
    client, Session = env
    r = client.get(f"{API}/inventory/equipements", headers=h())
    assert r.status_code == 200
    assert len(r.json()) == 2

    eq_id = r.json()[0]["id"]
    r2 = client.get(f"{API}/inventory/equipements/{eq_id}", headers=h())
    assert r2.status_code == 200
    assert r2.json()["id"] == eq_id

    assert client.get(f"{API}/inventory/equipements/9999", headers=h()).status_code == 404


def test_create_equipement_by_technicien_and_refused_to_visiteur(env):
    client, Session = env
    payload = {"nom": "RTR-NEW-01", "ip": "192.168.30.1", "type": "Routeur", "os": "iOS-XE"}
    r = client.post(f"{API}/inventory/equipements", json=payload, headers=h())
    assert r.status_code == 200
    body = r.json()
    assert body["nom"] == "RTR-NEW-01"
    assert body["health_score"] == 100.0  # valeur par défaut du schéma

    rv = client.post(f"{API}/inventory/equipements", json=payload, headers=h("visiteur", "Visiteur"))
    assert rv.status_code == 403

    with Session() as db:
        assert db.query(Equipement).filter_by(nom="RTR-NEW-01").count() == 1


def test_recalculate_health_applies_open_audit_penalty(env):
    client, Session = env
    with Session() as db:
        sw = db.query(Equipement).filter_by(nom="SW-CORE-01").first()
        db.add(AuditReseau(equipement_id=sw.id, constat="test", regle_cis="CIS-1.1",
                           criticite="elevee", correctif_propose="fix", statut="non_corrige",
                           date_audit=utcnow_naive()))
        db.commit()
        sw_id = sw.id

    r = client.post(f"{API}/inventory/recalculate-health/{sw_id}", headers=h())
    assert r.status_code == 200
    assert r.json() == {"equipement_id": sw_id, "health_score": 85.0}


# --------------------------------------------------------------- supervision

def test_metrics_filters_and_limit(env):
    client, Session = env
    with Session() as db:
        srv = db.query(Equipement).filter_by(nom="SRV-APP-01").first()
        srv_id = srv.id

    r = client.get(f"{API}/supervision/metrics", headers=h())
    assert r.status_code == 200
    assert len(r.json()) == 6  # 3 disk + 3 cpu

    r_disk = client.get(f"{API}/supervision/metrics", params={"type_metrique": "disk_percent"}, headers=h())
    assert r_disk.status_code == 200
    assert len(r_disk.json()) == 3
    assert all(m["type_metrique"] == "disk_percent" for m in r_disk.json())

    r_eq = client.get(f"{API}/supervision/metrics", params={"equipement_id": srv_id, "limit": 2}, headers=h())
    assert r_eq.status_code == 200
    assert len(r_eq.json()) == 2
    # Tri antéchronologique : la métrique la plus récente en tête.
    stamps = [m["horodatage"] for m in r_eq.json()]
    assert stamps == sorted(stamps, reverse=True)


def test_add_metric_by_technicien_and_predictions_listing(env):
    client, Session = env
    with Session() as db:
        srv_id = db.query(Equipement).filter_by(nom="SRV-APP-01").first().id

    payload = {"equipement_id": srv_id, "type_metrique": "ram_percent", "valeur": 55.5}
    r = client.post(f"{API}/supervision/metrics", json=payload, headers=h())
    assert r.status_code == 200
    assert r.json()["valeur"] == 55.5

    rv = client.post(f"{API}/supervision/metrics", json=payload, headers=h("visiteur", "Visiteur"))
    assert rv.status_code == 403

    rp = client.get(f"{API}/supervision/predictions", headers=h())
    assert rp.status_code == 200
    assert rp.json() == []  # aucune prédiction à ce stade


def test_calculate_ttf_endpoint_with_and_without_data(env):
    client, Session = env
    with Session() as db:
        srv_id = db.query(Equipement).filter_by(nom="SRV-APP-01").first().id
        # Equipement sans historique : propre pour la série de référence.
        sw_id = db.query(Equipement).filter_by(nom="SW-CORE-01").first().id

    # Pas assez de points (3 < 20) => réponse explicite, pas d'erreur 500.
    r = client.post(f"{API}/supervision/calculate-ttf/{srv_id}", headers=h())
    assert r.status_code == 200
    assert "Tendance stable" in r.json()["ttf_estime"]

    # Série croissante nette de 24 points => TTF chiffré + alerte préventive.
    now = utcnow_naive()
    with Session() as db:
        for i in range(24):
            db.add(Metrique(equipement_id=sw_id, type_metrique="disk_percent",
                            valeur=round(60.0 + i * (32.0 / 23), 2),
                            horodatage=now - timedelta(minutes=(23 - i) * 5)))
        db.commit()

    r2 = client.post(f"{API}/supervision/calculate-ttf/{sw_id}", headers=h())
    assert r2.status_code == 200
    body = r2.json()
    assert body["metrique"] == "disk_percent"
    assert 0.0 <= body["ttf_estime_heures"] < 48.0

    rp = client.get(f"{API}/supervision/predictions", headers=h())
    assert len(rp.json()) >= 1

