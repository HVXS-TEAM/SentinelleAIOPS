"""Phase 4 : tests des 4 endpoints de simulation (actes de soutenance).

Valide le comportement métier de chaque scénario de démo (brute-force SSH,
stress disque, faille CIS) ainsi que le /reset qui doit purger UNIQUEMENT les
données injectées par la simulation, sans toucher à la télémétrie du scheduler.
"""
import hashlib

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.api.v1.router import api_router
from app.core.database import Base, get_db
from app.core.security import create_access_token, hash_password
from app.core.time_utils import utcnow_naive
from app.models.models import (
    Alerte, AuditReseau, Equipement, EvenementSecurite, Metrique, Prediction,
    SauvegardeConfig, Utilisateur,
)
from app.api.v1.endpoints.simulation import SIMULATION_STATE
from app.services.netdevops_service import netdevops_service

API = "/api/v1"
BAD_CONFIG_ISSUES = 3  # SNMP public/private + password-encryption manquant + banner motd absente
SIM_KEYS = ("evenements_securite_ids", "alertes_ids", "metriques_ids",
            "predictions_ids", "audits_ids", "sauvegardes_ids")


def _clear_sim_state():
    for key in SIM_KEYS:
        SIMULATION_STATE[key].clear()
    SIMULATION_STATE["health_snapshots"].clear()


@pytest.fixture()
def env(monkeypatch):
    # L'audit CIS interroge Ollama (LLM local) : hors-ligne en test, on court-circuite.
    monkeypatch.setattr(netdevops_service, "query_ollama_audit", lambda config_text: None)

    engine = create_engine("sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool)
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    with Session() as s:
        s.add_all([
            Utilisateur(identifiant="admin", hash_mot_de_passe=hash_password("x"), role="Administrateur"),
            Utilisateur(identifiant="tech", hash_mot_de_passe=hash_password("x"), role="Technicien"),
            Utilisateur(identifiant="visiteur", hash_mot_de_passe=hash_password("x"), role="Visiteur"),
        ])
        # Télémétrie "scheduler" préexistante : ne doit JAMAIS être purgée par /reset.
        s.add(Equipement(nom="SRV-DB-01", ip="192.168.20.13", type="Serveur", health_score=100.0))
        s.commit()
        eq_db = s.query(Equipement).filter_by(nom="SRV-DB-01").first()
        s.add(Metrique(equipement_id=eq_db.id, type_metrique="cpu_percent", valeur=42.0,
                       horodatage=utcnow_naive()))
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

    # État en mémoire isolé entre tests (global partagé par le routeur).
    _clear_sim_state()
    yield TestClient(app), Session
    _clear_sim_state()


def h(identifiant, role):
    return {"Authorization": f"Bearer {create_access_token({'sub': identifiant, 'role': role})}"}


def post(client, path, role="Technicien", identifiant="tech"):
    return client.post(f"{API}/simulation/{path}", headers=h(identifiant, role))


def test_simulation_routes_refuse_visiteur(env):
    """Les 4 actes sont réservés aux rôles opérateur (Visiteur = 403)."""
    client, _ = env
    for path in ("inject-bruteforce", "stress-disk", "cis-flaw", "reset"):
        assert post(client, path, role="Visiteur", identifiant="visiteur").status_code == 403, path


def test_inject_bruteforce_detects_attacker(env):
    client, Session = env
    r = post(client, "inject-bruteforce")
    assert r.status_code == 200
    body = r.json()

    assert body["scenario"].startswith("Acte 3")
    assert body["ip_attaquante"] == "198.51.100.45"
    assert len(body["evenements_detectes"]) >= 1

    with Session() as db:
        attck = db.query(EvenementSecurite).filter_by(source_ip="198.51.100.45").all()
        assert attck, "l'attaquant doit être détecté en base"
        assert all(e.type_evenement == "SSH_BRUTEFORCE" for e in attck)  # 10 tentatives >= 5

    # L'équipement ciblé existe, a été snapshoté et sa santé a chuté sous 100.
    assert "health_score_hote_cible" in body
    assert body["health_score_hote_cible"] < 100.0
    with Session() as db:
        target = db.query(Equipement).filter_by(nom="SRV-AUTH-01").first()
        assert target is not None
        assert target.health_score == body["health_score_hote_cible"]


def test_stress_disk_produces_ttf_prediction_and_alert(env):
    client, Session = env
    r = post(client, "stress-disk")
    assert r.status_code == 200
    body = r.json()

    assert body["equipement"] == "SRV-APP-01"
    assert body["progression_pourcent"] == [60.0, 66.0, 72.0, 78.0, 83.0, 88.0]
    # Pente nette 60 -> 88 % en 40 min : TTF très inférieur à 24 h.
    assert body["ttf_estime_heures"] is not None
    assert body["ttf_estime_heures"] < 24.0

    with Session() as db:
        eq = db.query(Equipement).filter_by(nom="SRV-APP-01").first()
        preds = db.query(Prediction).filter_by(equipement_id=eq.id, metrique="disk_percent").all()
        assert preds, "la régression doit persister une prédiction"
        assert min(p.ttf_estime for p in preds) < 24.0
        alerts = db.query(Alerte).filter(
            Alerte.statut == "active", Alerte.message.endswith("pour disk_percent sur SRV-APP-01", autoescape=True)
        ).all()
        assert alerts, "l'alerte préventive doit être active"
        assert alerts[0].severite == "critique"  # TTF < 24 h

    # Prédiction TTF récente (< 10 min) => pénalité santé -20, disque 88 % <= 90 => pas de -25.
    assert body["health_score_equipement"] <= 80.0


def test_cis_flaw_reports_three_non_conformities_and_backup(env):
    client, Session = env
    r = post(client, "cis-flaw")
    assert r.status_code == 200
    body = r.json()

    assert body["scenario"].startswith("Acte 4")
    assert body["equipement"] == "SW-CORE-01"
    assert len(body["non_conformites"]) == BAD_CONFIG_ISSUES
    rules = {nc["regle_cis"].split(" - ")[0] for nc in body["non_conformites"]}
    assert rules == {"CIS-1.1", "CIS-2.2", "CIS-3.1"}

    with Session() as db:
        eq = db.query(Equipement).filter_by(nom="SW-CORE-01").first()
        backups = db.query(SauvegardeConfig).filter_by(equipement_id=eq.id).all()
        assert len(backups) == 1
        expected = hashlib.sha256(backups[0].contenu.encode("utf-8")).hexdigest()
        assert backups[0].hash_integrite == expected
        audits = db.query(AuditReseau).filter_by(equipement_id=eq.id).all()
        assert len(audits) == BAD_CONFIG_ISSUES
        assert all(a.statut == "non_corrige" for a in audits)

    # Audits ouverts CIS (2x elevee + 1x moyenne) => santé du switch impactée.
    assert body["health_score_equipement"] == 100.0 - (15.0 + 15.0 + 8.0)


def test_reset_purges_simulation_but_keeps_scheduler_data(env):
    client, Session = env

    # 1) Injecter les 3 scénarios.
    for path in ("inject-bruteforce", "stress-disk", "cis-flaw"):
        assert post(client, path).status_code == 200, path

    with Session() as db:
        assert db.query(EvenementSecurite).count() > 0
        assert db.query(Prediction).count() > 0
        assert db.query(AuditReseau).count() > 0

    # 2) Reset.
    r = post(client, "reset")
    assert r.status_code == 200
    purges = r.json()["elements_purges"]
    for key in ("evenements_securite", "alertes", "metriques", "predictions", "audits", "sauvegardes"):
        assert purges[key] > 0, f"{key} aurait dû être purgé"

    # 3) Plus rien de simulé en base, l'état mémoire est vide.
    with Session() as db:
        assert db.query(EvenementSecurite).count() == 0
        assert db.query(Prediction).count() == 0
        assert db.query(AuditReseau).count() == 0
        assert db.query(SauvegardeConfig).count() == 0
        # La métrique préexistante (télémétrie scheduler) survit au reset.
        assert db.query(Metrique).filter_by(type_metrique="cpu_percent").count() == 1

    assert not SIMULATION_STATE["evenements_securite_ids"]
    assert not SIMULATION_STATE["health_snapshots"]

    # 4) Reset idempotent : un second passage ne purge plus rien.
    r2 = post(client, "reset")
    assert r2.status_code == 200
    assert sum(r2.json()["elements_purges"].values()) == 0


