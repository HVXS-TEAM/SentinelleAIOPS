"""Tests de l'étape 3 : authentification obligatoire, rôles, MFA, anti force brute, journal d'audit."""
import pyotp
import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.api.v1.endpoints import auth as auth_module
from app.api.v1.router import api_router
from app.core.database import Base, get_db
from app.core.security import create_access_token, hash_password
from app.models.models import JournalAudit, Utilisateur
from app.services.reporting_service import reporting_service

API = "/api/v1"
MFA_SECRET = pyotp.random_base32()


@pytest.fixture()
def env(tmp_path, monkeypatch):
    engine = create_engine("sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool)
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    with Session() as s:
        s.add_all([
            Utilisateur(identifiant="admin", hash_mot_de_passe=hash_password("AdminPass2026!"),
                        role="Administrateur", mfa_active=True, mfa_secret=MFA_SECRET),
            Utilisateur(identifiant="tech", hash_mot_de_passe=hash_password("TechPass2026!"), role="Technicien"),
            Utilisateur(identifiant="visiteur", hash_mot_de_passe=hash_password("VisitorPass2026!"), role="Visiteur"),
        ])
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
    auth_module._login_failures.clear()

    monkeypatch.setattr(reporting_service, "build_pdf_report", lambda db, generated_by=None, now=None: b"%PDF-1.4 test")

    yield TestClient(app), Session
    auth_module._login_failures.clear()


def token_for(identifiant, role):
    return {"Authorization": f"Bearer {create_access_token({'sub': identifiant, 'role': role})}"}


def login(client, user, pwd, totp=None):
    data = {"username": user, "password": pwd}
    if totp:
        data["totp_code"] = totp
    return client.post(f"{API}/auth/login", data=data)


READ_ROUTES = [
    ("GET", "/inventory/equipements"), ("GET", "/supervision/metrics"), ("GET", "/supervision/predictions"),
    ("GET", "/securite/events"), ("GET", "/netdevops/audits"), ("GET", "/admin/alertes"),
]
OPS_ROUTES = [
    ("POST", "/simulation/reset"), ("POST", "/simulation/inject-bruteforce"), ("POST", "/simulation/stress-disk"),
    ("POST", "/simulation/cis-flaw"), ("POST", "/admin/alertes/1/acquitter"),
    ("POST", "/inventory/recalculate-health/1"), ("POST", "/supervision/calculate-ttf/1"),
    ("GET", "/admin/generate-pdf-report"),
]
ADMIN_ROUTES = [("GET", "/admin/journal-audit")]


def call(client, method, path, headers=None):
    return client.request(method, f"{API}{path}", headers=headers)


def test_every_route_requires_a_token(env):
    client, _ = env
    for method, path in READ_ROUTES + OPS_ROUTES + ADMIN_ROUTES + [("POST", "/assistant/query")]:
        assert call(client, method, path).status_code == 401, (method, path)
    assert client.get(f"{API}/auth/me").status_code == 401


def test_visiteur_reads_but_cannot_operate(env):
    client, _ = env
    h = token_for("visiteur", "Visiteur")
    for method, path in READ_ROUTES:
        assert call(client, method, path, h).status_code == 200, path
    assert client.post(f"{API}/assistant/query", json={"question": "état du parc"}, headers=h).status_code == 200
    for method, path in OPS_ROUTES + ADMIN_ROUTES:
        assert call(client, method, path, h).status_code == 403, path


def test_technicien_operates_but_not_admin_routes(env):
    client, _ = env
    h = token_for("tech", "Technicien")
    assert call(client, "POST", "/simulation/reset", h).status_code == 200
    assert call(client, "GET", "/admin/generate-pdf-report", h).status_code == 200
    assert call(client, "POST", "/admin/alertes/999/acquitter", h).status_code == 404   # autorisé, alerte inexistante
    assert call(client, "GET", "/admin/journal-audit", h).status_code == 403


def test_administrateur_reads_journal(env):
    client, _ = env
    h = token_for("admin", "Administrateur")
    assert call(client, "GET", "/admin/journal-audit", h).status_code == 200
    assert call(client, "POST", "/simulation/reset", h).status_code == 200


def test_role_comes_from_database_not_from_token(env):
    client, _ = env
    h = token_for("visiteur", "Administrateur")        # jeton "menteur"
    assert call(client, "GET", "/admin/journal-audit", h).status_code == 403


def test_invalid_tampered_or_orphan_tokens(env):
    client, _ = env
    good = create_access_token({"sub": "tech", "role": "Technicien"})
    assert call(client, "GET", "/inventory/equipements", {"Authorization": f"Bearer {good}x"}).status_code == 401
    assert call(client, "GET", "/inventory/equipements", {"Authorization": "Bearer nimportequoi"}).status_code == 401
    assert call(client, "GET", "/inventory/equipements", token_for("fantome", "Technicien")).status_code == 401


def test_login_success_and_failure_are_journaled(env):
    client, Session = env
    assert login(client, "tech", "mauvais").status_code == 401
    assert login(client, "inconnu", "x").status_code == 401
    r = login(client, "tech", "TechPass2026!")
    assert r.status_code == 200 and r.json()["role"] == "Technicien" and r.json()["access_token"]
    with Session() as s:
        actions = [(j.action, j.cible) for j in s.query(JournalAudit).order_by(JournalAudit.id)]
    assert ("CONNEXION_ECHEC", "tech") in actions
    assert ("CONNEXION_ECHEC", "inconnu") in actions
    assert ("CONNEXION_REUSSIE", "tech") in actions


def test_mfa_flow_for_admin(env):
    client, Session = env
    r = login(client, "admin", "AdminPass2026!")
    assert r.status_code == 200 and r.json()["mfa_required"] is True and r.json()["access_token"] == ""
    assert login(client, "admin", "AdminPass2026!", "000000").status_code == 401
    r = login(client, "admin", "AdminPass2026!", pyotp.TOTP(MFA_SECRET).now())
    assert r.status_code == 200 and r.json()["access_token"] and r.json()["mfa_required"] is False
    with Session() as s:
        assert s.query(JournalAudit).filter(JournalAudit.action == "MFA_ECHEC").count() == 1


def test_bruteforce_lockout_blocks_even_the_right_password(env):
    client, _ = env
    for _ in range(auth_module.MAX_FAILURES):
        assert login(client, "tech", "faux").status_code == 401
    assert login(client, "tech", "TechPass2026!").status_code == 429
    assert login(client, "visiteur", "VisitorPass2026!").status_code == 200   # autre compte : non bloqué


def test_refused_and_authorized_actions_are_journaled(env):
    client, Session = env
    call(client, "POST", "/simulation/reset", token_for("visiteur", "Visiteur"))
    call(client, "POST", "/simulation/reset", token_for("tech", "Technicien"))
    with Session() as s:
        rows = {(j.action, j.utilisateur_id) for j in s.query(JournalAudit)}
    assert ("ACCES_REFUSE", 3) in rows and ("SIMULATION_RESET", 2) in rows


def test_me_does_not_leak_secrets(env):
    client, _ = env
    body = client.get(f"{API}/auth/me", headers=token_for("admin", "Administrateur")).json()
    assert body["identifiant"] == "admin"
    assert not {"hash_mot_de_passe", "mfa_secret"} & set(body)
