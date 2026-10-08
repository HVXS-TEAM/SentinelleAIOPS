"""Tests de l'étape 2 : rétention automatique et remise à zéro des données de démo."""
from datetime import datetime, timedelta

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.core import maintenance
from app.core.database import Base
from app.models.models import (
    Alerte, AuditReseau, Equipement, EvenementSecurite, Metrique, Prediction, SauvegardeConfig,
)

NOW = datetime(2026, 9, 20, 12, 0, 0)


@pytest.fixture()
def db():
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    session = sessionmaker(bind=engine)()
    session.add(Equipement(nom="SRV-T", ip="10.0.0.1", type="Serveur", health_score=10.0))
    session.commit()
    yield session
    session.close()


def _alerte(statut, age_h):
    return Alerte(type="T", module_origine="supervision", severite="critique", message=f"{statut}-{age_h}",
                  statut=statut, date_creation=NOW - timedelta(hours=age_h))


def test_purge_removes_only_old_data(db):
    db.add_all([
        Metrique(equipement_id=1, type_metrique="cpu_percent", valeur=1, horodatage=NOW - timedelta(hours=30)),
        Metrique(equipement_id=1, type_metrique="cpu_percent", valeur=2, horodatage=NOW - timedelta(hours=1)),
        Prediction(equipement_id=1, metrique="disk_percent", ttf_estime=1, date_calcul=NOW - timedelta(hours=30)),
        Prediction(equipement_id=1, metrique="disk_percent", ttf_estime=2, date_calcul=NOW - timedelta(hours=1)),
        _alerte("resolue", 30), _alerte("resolue", 2),
        _alerte("active", 100), _alerte("acquitte", 100),
    ])
    db.commit()

    counts = maintenance.purge_old_data(db, now=NOW)

    assert counts == {"metriques": 1, "predictions": 1, "alertes_resolues": 1}
    assert db.query(Metrique).count() == 1
    assert db.query(Prediction).count() == 1
    statuts = sorted(a.message for a in db.query(Alerte).all())
    assert statuts == ["acquitte-100", "active-100", "resolue-2"]   # actives/acquittées jamais purgées


def test_purge_is_batched(db, monkeypatch):
    monkeypatch.setattr(maintenance, "BATCH", 7)
    db.add_all([
        Metrique(equipement_id=1, type_metrique="cpu_percent", valeur=i, horodatage=NOW - timedelta(hours=48))
        for i in range(25)
    ])
    db.commit()
    assert maintenance.purge_old_data(db, now=NOW)["metriques"] == 25
    assert db.query(Metrique).count() == 0


def test_purge_keeps_audits_backups_and_events(db):
    db.add_all([
        AuditReseau(equipement_id=1, constat="c", regle_cis="CIS-1.1", criticite="elevee", date_audit=NOW - timedelta(days=90)),
        SauvegardeConfig(equipement_id=1, contenu="x", hash_integrite="h", date_sauvegarde=NOW - timedelta(days=90)),
        EvenementSecurite(source_ip="1.2.3.4", type_evenement="T", score_anomalie=-1, severite="critique",
                          horodatage=NOW - timedelta(days=90)),
    ])
    db.commit()
    maintenance.purge_old_data(db, now=NOW)
    assert (db.query(AuditReseau).count(), db.query(SauvegardeConfig).count(), db.query(EvenementSecurite).count()) == (1, 1, 1)


def test_reset_demo_data_cleans_and_recomputes_health(db):
    recent = datetime.utcnow() - timedelta(minutes=5)
    old = datetime.utcnow() - timedelta(hours=48)
    db.add_all([
        AuditReseau(equipement_id=1, constat="c", regle_cis="CIS-1.1", criticite="elevee"),
        SauvegardeConfig(equipement_id=1, contenu="x", hash_integrite="h"),
        EvenementSecurite(source_ip="1.2.3.4", equipement_id=1, type_evenement="T", score_anomalie=-1, severite="critique"),
        Prediction(equipement_id=1, metrique="disk_percent", ttf_estime=1),
        Alerte(type="T", module_origine="supervision", severite="critique", message="m", statut="active"),
        Metrique(equipement_id=1, type_metrique="cpu_percent", valeur=1, horodatage=old),
        Metrique(equipement_id=1, type_metrique="cpu_percent", valeur=2, horodatage=recent),
    ])
    db.commit()

    preview = maintenance.count_demo_data(db)
    assert preview["alertes"] == 1 and preview["metriques"] == 2

    counts = maintenance.reset_demo_data(db)

    assert counts == {"alertes": 1, "predictions": 1, "evenements_securite": 1, "audits_reseau": 1,
                      "sauvegardes_config": 1, "metriques": 2}
    assert db.query(Metrique).count() == 0                       # tout l'historique de métriques repart à zéro
    assert db.query(Equipement).count() == 1                     # l'équipement est conservé
    assert db.query(Equipement).first().health_score == 100.0    # score recalculé (plus d'audit, d'évènement...)
