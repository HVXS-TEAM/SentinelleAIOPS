"""Tests de l'étape 4 : rapport PDF réel (en mémoire), rôles, erreurs explicites."""
import builtins
import io
from datetime import datetime, timedelta

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.api.v1.router import api_router
from app.core.database import Base, get_db
from app.core.security import create_access_token, hash_password
from app.models.models import (
    Alerte, AuditReseau, Equipement, EvenementSecurite, JournalAudit, Prediction, SauvegardeConfig, Utilisateur,
)
from app.services import reporting_service as rs
from app.services.reporting_service import ReportUnavailableError, reporting_service

reportlab = pytest.importorskip("reportlab")
API = "/api/v1"
NOW = datetime(2026, 9, 21, 12, 0, 0)


def pdf_text(data: bytes) -> str:
    pypdf = pytest.importorskip("pypdf")
    reader = pypdf.PdfReader(io.BytesIO(data))
    return "\n".join(p.extract_text() for p in reader.pages)


def n_pages(data: bytes) -> int:
    pypdf = pytest.importorskip("pypdf")
    return len(pypdf.PdfReader(io.BytesIO(data)).pages)


@pytest.fixture()
def Session():
    engine = create_engine("sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool)
    Base.metadata.create_all(engine)
    S = sessionmaker(bind=engine)
    with S() as s:
        s.add_all([
            Utilisateur(identifiant="tech", hash_mot_de_passe=hash_password("x"), role="Technicien"),
            Utilisateur(identifiant="visiteur", hash_mot_de_passe=hash_password("x"), role="Visiteur"),
        ])
        s.commit()
    return S


def populate(db, n_alertes=3):
    db.add_all([
        Equipement(nom="SRV-APP-01", ip="192.168.20.12", type="Serveur", os="Ubuntu", health_score=45.0),
        Equipement(nom="SW-CORE-01", ip="192.168.10.1", type="Switch", os="Cisco IOS", health_score=100.0),
    ])
    db.commit()
    for i in range(n_alertes):
        db.add(Alerte(type="RessourceCritique", module_origine="supervision", severite="critique",
                      message=f"Alerte préventive n°{i} : disque presque plein", statut="active",
                      date_creation=NOW - timedelta(minutes=i)))
    db.add(Prediction(equipement_id=1, metrique="disk_percent", ttf_estime=2.5, date_calcul=NOW - timedelta(minutes=5)))
    db.add(EvenementSecurite(source_ip="198.51.100.45", equipement_id=1, type_evenement="SSH_BRUTEFORCE",
                             score_anomalie=-0.72, severite="critique", horodatage=NOW - timedelta(minutes=3)))
    db.add(AuditReseau(equipement_id=2, constat="Mots de passe non chiffrés", regle_cis="CIS-1.1",
                       criticite="elevee", statut="non_corrige", date_audit=NOW - timedelta(minutes=10)))
    db.add(SauvegardeConfig(equipement_id=2, contenu="conf", hash_integrite="a" * 64,
                            date_sauvegarde=NOW - timedelta(hours=1)))
    db.commit()


def test_report_is_a_real_pdf_with_the_actual_data(Session):
    with Session() as db:
        populate(db)
        pdf = reporting_service.build_pdf_report(db, generated_by="tech", now=NOW)
    assert pdf.startswith(b"%PDF-") and pdf.rstrip().endswith(b"%%EOF") and len(pdf) > 5_000
    text = pdf_text(pdf)
    for expected in ("Rapport d'audit et de synthèse", "NIVEAU GLOBAL : CRITIQUE", "par tech", "SRV-APP-01",
                     "SSH_BRUTEFORCE", "198.51.100.45", "CIS-1.1", "Page 1 /"):
        assert expected in text, expected


def test_report_on_empty_database_is_nominal(Session):
    with Session() as db:
        pdf = reporting_service.build_pdf_report(db, now=NOW)
    assert pdf.startswith(b"%PDF-")
    text = pdf_text(pdf)
    assert "NIVEAU GLOBAL : NOMINAL" in text and "Aucune alerte active." in text


def test_report_escapes_markup_in_data(Session):
    with Session() as db:
        db.add(Alerte(type="T", module_origine="<b>x</i>", severite="critique",
                      message='<script>alert("x")</script> & <unclosed', statut="active", date_creation=NOW))
        db.commit()
        pdf = reporting_service.build_pdf_report(db, now=NOW)     # ne doit pas lever d'exception
    assert "<script>" in pdf_text(pdf)


def test_report_truncates_long_lists_and_paginates(Session):
    with Session() as db:
        populate(db, n_alertes=40)
        pdf = reporting_service.build_pdf_report(db, now=NOW)
    text = pdf_text(pdf)
    assert "et 25 autre(s) alerte(s) non affichée(s)" in text
    assert n_pages(pdf) >= 2


def test_missing_reportlab_raises_explicit_error(Session, monkeypatch):
    real_import = builtins.__import__

    def no_reportlab(name, *args, **kwargs):          # simule un environnement sans ReportLab
        if name.split(".")[0] == "reportlab":
            raise ImportError("No module named 'reportlab'")
        return real_import(name, *args, **kwargs)

    monkeypatch.setattr(builtins, "__import__", no_reportlab)
    with Session() as db:
        with pytest.raises(ReportUnavailableError, match="pip install reportlab"):
            reporting_service.build_pdf_report(db, now=NOW)


# ------------------------------------------------------------------------------------------ endpoint
@pytest.fixture()
def client(Session, tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)                       # détecte toute écriture de fichier parasite
    app = FastAPI()
    app.include_router(api_router, prefix=API)

    def override():
        db = Session()
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = override
    return TestClient(app), tmp_path


def bearer(user, role):
    return {"Authorization": f"Bearer {create_access_token({'sub': user, 'role': role})}"}


def test_endpoint_requires_authentication_and_operator_role(client):
    c, _ = client
    assert c.get(f"{API}/admin/generate-pdf-report").status_code == 401
    assert c.get(f"{API}/admin/generate-pdf-report", headers=bearer("visiteur", "Visiteur")).status_code == 403


def test_endpoint_returns_pdf_attachment_and_writes_nothing_on_disk(client, Session):
    c, tmp = client
    with Session() as db:
        populate(db)
    r = c.get(f"{API}/admin/generate-pdf-report", headers=bearer("tech", "Technicien"))
    assert r.status_code == 200
    assert r.headers["content-type"] == "application/pdf"
    assert r.headers["content-disposition"].startswith('attachment; filename="rapport_sentinelle_')
    assert r.content.startswith(b"%PDF-") and len(r.content) > 5_000
    assert list(tmp.iterdir()) == []                  # aucun fichier créé sur le serveur
    with Session() as db:
        assert db.query(JournalAudit).filter(JournalAudit.action == "RAPPORT_PDF").count() == 1
    assert "par tech" in pdf_text(r.content)


def test_endpoint_reports_missing_reportlab_as_503(client, monkeypatch):
    c, _ = client

    def boom(*a, **k):
        raise ReportUnavailableError("Le module ReportLab n'est pas installé sur le serveur (pip install reportlab).")

    monkeypatch.setattr(reporting_service, "build_pdf_report", boom)
    r = c.get(f"{API}/admin/generate-pdf-report", headers=bearer("tech", "Technicien"))
    assert r.status_code == 503 and "reportlab" in r.json()["detail"].lower()
