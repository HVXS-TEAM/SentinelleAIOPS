"""Tests de l'étape 1 : TTF sur points récents, alertes dédupliquées, score de santé unique."""
from datetime import datetime, timedelta

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.core.database import Base
from app.core.migrations import ensure_schema
from app.models.models import Alerte, Equipement, EvenementSecurite, Metrique, Prediction
from app.services.inventory_service import inventory_service
from app.services.supervision_service import supervision_service


@pytest.fixture()
def db():
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    ensure_schema(engine)
    supervision_service._last_breach.clear()
    session = sessionmaker(bind=engine)()
    eq = Equipement(nom="SRV-TEST-01", ip="10.0.0.1", type="Serveur", health_score=100.0)
    session.add(eq)
    session.commit()
    yield session
    session.close()


def _add_series(db, eq_id, metrique, values, step_s=10, end=None):
    end = end or datetime.utcnow()
    n = len(values)
    for i, v in enumerate(values):
        db.add(Metrique(equipement_id=eq_id, type_metrique=metrique, valeur=v,
                        horodatage=end - timedelta(seconds=(n - 1 - i) * step_s)))
    db.commit()


def test_estimate_ttf_pure():
    # +6 %/8 min = 45 %/h, dernière valeur 88 -> (95-88)/45 h
    times = [i * 8 / 60 for i in range(6)]
    ttf = supervision_service.estimate_ttf(times, [60, 66, 72, 78, 83, 88], min_points=5)
    assert ttf is not None and 0.10 < ttf < 0.25


def test_estimate_ttf_ignores_flat_noisy_and_decreasing():
    t = [i / 360 for i in range(60)]
    assert supervision_service.estimate_ttf(t, [50.0] * 60) is None
    assert supervision_service.estimate_ttf(t, [80 - i for i in range(60)]) is None
    noisy = [50 + (5 if i % 2 else -5) for i in range(60)]
    assert supervision_service.estimate_ttf(t, noisy) is None


def test_calculate_ttf_uses_most_recent_points(db):
    # Ancien historique en forte hausse (ne doit PAS compter) puis plateau récent stable
    old_end = datetime.utcnow() - timedelta(days=2)
    _add_series(db, 1, "disk_percent", [10 + i for i in range(60)], end=old_end)
    _add_series(db, 1, "disk_percent", [50.0] * 200)
    assert supervision_service.calculate_ttf(db, 1, "disk_percent") is None
    assert db.query(Alerte).count() == 0


def test_alert_is_deduplicated_and_updated_in_place(db):
    _add_series(db, 1, "disk_percent", [60 + i * 0.25 for i in range(130)])  # +1,5 %/min
    for _ in range(5):
        supervision_service.calculate_ttf(db, 1, "disk_percent")
    alerts = db.query(Alerte).filter(Alerte.statut == "active").all()
    assert len(alerts) == 1
    assert "pour disk_percent sur SRV-TEST-01" in alerts[0].message


def test_legacy_duplicates_are_resolved(db):
    _add_series(db, 1, "disk_percent", [60 + i * 0.25 for i in range(130)])
    for i in range(4):
        db.add(Alerte(type="RessourceCritique", module_origine="supervision", severite="critique",
                      message=f"Alerte préventive : TTF estimé à 0.{i}h pour disk_percent sur SRV-TEST-01",
                      statut="active", date_creation=datetime.utcnow() - timedelta(hours=i + 1)))
    db.commit()
    supervision_service.calculate_ttf(db, 1, "disk_percent")
    assert db.query(Alerte).filter(Alerte.statut == "active").count() == 1
    assert db.query(Alerte).filter(Alerte.statut == "resolue").count() == 3


def test_alert_resolved_only_after_min_lifetime(db):
    young = Alerte(type="RessourceCritique", module_origine="supervision", severite="critique",
                   message="Alerte préventive : TTF estimé à 1.0h pour cpu_percent sur SRV-TEST-01",
                   statut="active", date_creation=datetime.utcnow() - timedelta(minutes=2))
    old = Alerte(type="RessourceCritique", module_origine="supervision", severite="critique",
                 message="Alerte préventive : TTF estimé à 1.0h pour ram_percent sur SRV-TEST-01",
                 statut="active", date_creation=datetime.utcnow() - timedelta(minutes=30))
    db.add_all([young, old]); db.commit()
    _add_series(db, 1, "cpu_percent", [40.0] * 130)
    _add_series(db, 1, "ram_percent", [40.0] * 130)
    supervision_service.calculate_ttf(db, 1, "cpu_percent")
    supervision_service.calculate_ttf(db, 1, "ram_percent")
    db.refresh(young); db.refresh(old)
    assert young.statut == "active" and old.statut == "resolue"


def test_calculate_ttf_no_longer_touches_health(db):
    _add_series(db, 1, "disk_percent", [60 + i * 0.25 for i in range(130)])
    supervision_service.calculate_ttf(db, 1, "disk_percent")
    assert db.query(Equipement).first().health_score == 100.0


def test_health_uses_recent_ttf_and_targeted_security_events(db):
    db.add(Prediction(equipement_id=1, metrique="disk_percent", ttf_estime=3.0, date_calcul=datetime.utcnow()))
    db.add(Prediction(equipement_id=1, metrique="cpu_percent", ttf_estime=30.0, date_calcul=datetime.utcnow()))
    db.add(Prediction(equipement_id=1, metrique="ram_percent", ttf_estime=1.0,
                      date_calcul=datetime.utcnow() - timedelta(hours=1)))  # trop ancienne : ignorée
    db.add(EvenementSecurite(source_ip="198.51.100.45", equipement_id=1, type_evenement="SSH_BRUTEFORCE",
                             score_anomalie=-0.7, severite="critique"))
    db.commit()
    # 100 - 20 (disk<24h) - 10 (cpu<48h) - 25 (critique ciblé) = 45
    assert inventory_service.calculate_health_score(db, 1) == 45.0
    # Idempotent : un second recalcul donne le même résultat
    assert inventory_service.calculate_health_score(db, 1) == 45.0


def test_ensure_schema_adds_missing_column():
    from sqlalchemy import inspect, text
    engine = create_engine("sqlite:///:memory:")
    with engine.begin() as c:
        c.execute(text("CREATE TABLE equipements (id INTEGER PRIMARY KEY)"))
        c.execute(text("CREATE TABLE evenements_securite (id INTEGER PRIMARY KEY, source_ip VARCHAR(45))"))
    ensure_schema(engine)
    ensure_schema(engine)  # idempotent
    cols = {c["name"] for c in inspect(engine).get_columns("evenements_securite")}
    assert "equipement_id" in cols


def test_reused_old_alert_is_not_resolved_right_after_a_breach(db):
    """Une vieille alerte ré-activée par un nouveau dépassement reste vivante ALERT_MIN_LIFETIME."""
    db.add(Alerte(type="RessourceCritique", module_origine="supervision", severite="critique",
                  message="Alerte préventive : TTF estimé à 9.0h pour disk_percent sur SRV-TEST-01",
                  statut="active", date_creation=datetime.utcnow() - timedelta(hours=5)))
    db.commit()
    end = datetime.utcnow()
    points = [(end - timedelta(minutes=(5 - i) * 8), v) for i, v in enumerate([60.0, 66.0, 72.0, 78.0, 83.0, 88.0])]
    assert supervision_service.evaluate_series(db, 1, "disk_percent", points, min_points=5) < 1.0
    _add_series(db, 1, "disk_percent", [50.0] * 200)         # la tendance disparaît juste après
    supervision_service.calculate_ttf(db, 1, "disk_percent")
    assert db.query(Alerte).filter(Alerte.statut == "active").count() == 1
