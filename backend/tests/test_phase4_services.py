"""Phase 4 : tests des services métier non couverts (sécurité, NetDevOps, assistant).

- security_service : parsing, mode de repli statistique déterministe (sans
  scikit-learn) et détection Isolation Forest (chemin réel).
- netdevops_service : audit CIS statique, sauvegarde intégrée (hash SHA-256),
  LLM Ollama court-circuité hors-ligne.
- assistant_service : routage d'intention sur base (4 intents) + repli
  hors-ligne quand Ollama est injoignable.
"""
import hashlib

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.core.database import Base
from app.models.models import Alerte, AuditReseau, Equipement, EvenementSecurite, Prediction, SauvegardeConfig
from app.services import security_service as sec_mod
from app.services.security_service import security_service

CLEAN_CONFIG = (
    "hostname SW-CORE-01\n"
    "service password-encryption\n"
    "banner motd # ACCES RESTREINT #\n"
    "snmp-server community S3cret123 RO\n"
)
FLAWED_CONFIG = (
    "hostname SW-CORE-01\n"
    "snmp-server community public RO\n"
    "snmp-server community private RW\n"
    "line vty 0 4\n login local\n"
)


@pytest.fixture()
def db():
    engine = create_engine("sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool)
    Base.metadata.create_all(engine)
    S = sessionmaker(bind=engine)
    session = S()
    yield session
    session.close()


def attack_lines():
    """Bruit légitime (1-2 tentatives) + salve de 10 échecs depuis l'attaquant."""
    lines = [
        f"Oct 09 10:00:{i:02d} srv sshd[100{i}]: Failed password for backup from 198.18.0.5 port 5000{i} ssh2"
        for i in range(2)
    ]
    lines += [
        f"Oct 09 10:01:{i:02d} srv sshd[200{i}]: Failed password for root from 198.51.100.45 port 5400{i} ssh2"
        for i in range(10)
    ]
    return lines


# ------------------------------------------------------------------ sécurité

def test_analyze_log_batch_returns_empty_without_exploitable_lines(db):
    assert security_service.analyze_log_batch(db, ["Accepted password for admin from 10.0.0.1 port 22 ssh2"]) == []
    assert security_service.analyze_log_batch(db, []) == []
    assert db.query(EvenementSecurite).count() == 0


def test_fallback_statistical_mode_flags_bruteforce_deterministically(db, monkeypatch):
    """Sans scikit-learn : repli statistique — IP à >= 5 tentatives => critique + alerte."""
    monkeypatch.setattr(sec_mod, "HAS_SKLEARN", False)

    results = security_service.analyze_log_batch(db, attack_lines(), equipement_id=None)

    assert len(results) == 1                      # seule l'IP à 10 tentatives est retenue
    ev = results[0]
    assert ev.source_ip == "198.51.100.45"
    assert ev.type_evenement == "SSH_BRUTEFORCE"
    assert ev.severite == "critique"              # score -0.85 < -0.5
    assert ev.score_anomalie == pytest.approx(-0.85)
    alert = db.query(Alerte).filter_by(type="AttaqueDetectee", statut="active").one()
    assert "198.51.100.45" in alert.message
    assert "10 tentatives" in alert.message


def test_isolation_forest_detects_attacker_when_available(db):
    if not sec_mod.HAS_SKLEARN:
        pytest.skip("scikit-learn absent : le repli statistique est couvert par le test déterministe")

    results = security_service.analyze_log_batch(db, attack_lines(), equipement_id=None)

    by_ip = {ev.source_ip: ev for ev in results}
    assert "198.51.100.45" in by_ip, "l'IP à 10 tentatives doit être retenue"
    assert by_ip["198.51.100.45"].type_evenement == "SSH_BRUTEFORCE"
    assert db.query(EvenementSecurite).filter_by(source_ip="198.51.100.45").count() >= 1


# ----------------------------------------------------------------- netdevops

def test_audit_flags_three_cis_issues_and_saves_hashed_backup(db, monkeypatch):
    from app.services.netdevops_service import netdevops_service
    monkeypatch.setattr(netdevops_service, "query_ollama_audit", lambda config_text: None)
    eq = Equipement(nom="SW-CORE-01", ip="192.168.10.1", type="Switch")
    db.add(eq)
    db.commit()

    audits = netdevops_service.run_full_audit(db, eq.id, FLAWED_CONFIG)

    assert len(audits) == 3
    rules = {a.regle_cis.split(" - ")[0] for a in audits}
    assert rules == {"CIS-1.1", "CIS-2.2", "CIS-3.1"}
    assert all(a.statut == "non_corrige" for a in audits)
    assert all(a.correctif_propose for a in audits)  # chaque échec propose un correctif

    saved = db.query(SauvegardeConfig).one()
    assert saved.hash_integrite == hashlib.sha256(FLAWED_CONFIG.encode("utf-8")).hexdigest()
    assert saved.contenu == FLAWED_CONFIG


def test_audit_conforming_config_has_no_finding_but_keeps_backup(db, monkeypatch):
    from app.services.netdevops_service import netdevops_service
    monkeypatch.setattr(netdevops_service, "query_ollama_audit", lambda config_text: None)
    eq = Equipement(nom="SW-CORE-02", ip="192.168.10.2", type="Switch")
    db.add(eq)
    db.commit()

    audits = netdevops_service.run_full_audit(db, eq.id, CLEAN_CONFIG)

    assert audits == []
    assert db.query(SauvegardeConfig).count() == 1  # la sauvegarde est créée dans tous les cas


def test_llm_finding_is_merged_when_ollama_answers(db, monkeypatch):
    from app.services.netdevops_service import netdevops_service
    monkeypatch.setattr(netdevops_service, "query_ollama_audit", lambda config_text: {
        "regle_cis": "CIS-LLM-01", "constat": "Finding LLM de test",
        "criticite": "moyenne", "correctif_propose": "corriger",
    })
    eq = Equipement(nom="SW-CORE-03", ip="192.168.10.3", type="Switch")
    db.add(eq)
    db.commit()

    audits = netdevops_service.run_full_audit(db, eq.id, CLEAN_CONFIG)

    assert len(audits) == 1  # 0 finding statique + 1 finding LLM
    assert audits[0].regle_cis == "CIS-LLM-01"
    assert audits[0].constat == "Finding LLM de test"


# ----------------------------------------------------------------- assistant

def test_assistant_intent_parc_lists_health(db):
    from app.services.assistant_service import assistant_service
    db.add_all([
        Equipement(nom="SRV-A", ip="10.0.0.1", type="Serveur", health_score=95.0),
        Equipement(nom="SW-A", ip="10.0.0.2", type="Switch", health_score=100.0),
    ])
    db.commit()

    out = assistant_service.process_natural_query(db, "Quel est l'état du parc ?")

    assert "2 équipements" in out["reponse"]
    assert len(out["donnees_associees"]) == 2
    assert {d["nom"] for d in out["donnees_associees"]} == {"SRV-A", "SW-A"}
    assert out["donnees_associees"][0]["sante"].endswith("%")


def test_assistant_intent_alertes_lists_only_active(db):
    from app.services.assistant_service import assistant_service
    db.add_all([
        Alerte(type="RessourceCritique", module_origine="supervision", severite="critique",
               message="Disque plein", statut="active"),
        Alerte(type="RessourceCritique", module_origine="supervision", severite="warning",
               message="Ancienne alerte", statut="resolue"),
    ])
    db.commit()

    out = assistant_service.process_natural_query(db, "Y a-t-il des alertes critiques ?")

    assert "1 alerte(s) active(s)" in out["reponse"]
    assert len(out["donnees_associees"]) == 1
    assert out["donnees_associees"][0]["message"] == "Disque plein"


def test_assistant_intent_ttf_returns_predictions(db):
    from app.core.time_utils import utcnow_naive
    from app.services.assistant_service import assistant_service
    eq = Equipement(nom="SRV-DB-01", ip="10.0.0.3", type="Serveur")
    db.add(eq)
    db.commit()
    db.add(Prediction(equipement_id=eq.id, metrique="disk_percent", ttf_estime=12.5,
                      date_calcul=utcnow_naive()))
    db.commit()

    out = assistant_service.process_natural_query(db, "Quel est le TTF du disque ?")

    assert "prédictions de saturation" in out["reponse"]
    assert out["donnees_associees"][0]["equipement"] == "SRV-DB-01"
    assert out["donnees_associees"][0]["ttf_estime"] == "12.5 heures"


def test_assistant_intent_audit_synthesizes_findings(db):
    from app.core.time_utils import utcnow_naive
    from app.services.assistant_service import assistant_service
    eq = Equipement(nom="SW-DB-01", ip="10.0.0.4", type="Switch")
    db.add(eq)
    db.commit()
    db.add(AuditReseau(equipement_id=eq.id, constat="SNMP public", regle_cis="CIS-2.2",
                       criticite="elevee", correctif_propose="no snmp-server community public",
                       statut="non_corrige", date_audit=utcnow_naive()))
    db.commit()

    out = assistant_service.process_natural_query(db, "Montre l'audit CIS réseau")

    assert "1 non-conformité(s)" in out["reponse"]
    assert out["donnees_associees"][0]["regle"] == "CIS-2.2"


def test_assistant_falls_back_to_welcome_message_when_ollama_offline(db, monkeypatch):
    from app.services import assistant_service as asst_mod

    def _raise(*args, **kwargs):
        raise ConnectionError("Ollama hors-ligne")

    monkeypatch.setattr(asst_mod.requests, "post", _raise)

    out = asst_mod.assistant_service.process_natural_query(db, "Bonjour, qui es-tu ?")

    assert "assistant IA Sentinelle AIOps" in out["reponse"]
    assert out["donnees_associees"] is None


