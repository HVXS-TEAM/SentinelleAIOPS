"""Phase 4 : tests du moteur d'arrière-plan (APScheduler, Phase 1).

Les jobs sont appelés directement (sans attendre les intervalles) avec une
base SQLite in-memory branchée à la place de `SessionLocal`, pour valider :
- la génération de télémétrie simulée bornée et le pinning démo (`pin_metric`) ;
- le calcul de TTF à partir des métriques récentes ;
- le recalcul du score de santé ;
- l'enregistrement idempotent des 4 jobs au démarrage/arrêt du scheduler.
"""
import pytest
from datetime import timedelta

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.core import scheduler as sched
from app.core.database import Base
from app.core.time_utils import utcnow_naive
from app.models.models import Alerte, AuditReseau, Equipement, Metrique, Prediction


@pytest.fixture()
def Session(monkeypatch):
    engine = create_engine("sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool)
    Base.metadata.create_all(engine)
    S = sessionmaker(bind=engine)

    # Les jobs ouvrent leur propre session : on branche la base de test.
    monkeypatch.setattr(sched, "SessionLocal", S)
    # État de simulation inter-module isolé entre tests.
    sched._last_values.clear()
    sched._baselines.clear()

    with S() as db:
        db.add_all([
            Equipement(nom="SRV-T1", ip="10.0.0.1", type="Serveur", health_score=100.0),
            Equipement(nom="SW-T1", ip="10.0.0.2", type="Switch", health_score=100.0),
        ])
        db.commit()

    yield S
    sched._last_values.clear()
    sched._baselines.clear()


def seed_disk_series(db, equipement_id, start=60.0, end=92.0, n=24, step_minutes=5):
    """Série croissante parfaite (R²=1) sur la fenêtre glissante de calculate_ttf."""
    now = utcnow_naive()
    delta = (end - start) / (n - 1)
    for i in range(n):
        db.add(Metrique(
            equipement_id=equipement_id,
            type_metrique="disk_percent",
            valeur=round(start + i * delta, 2),
            horodatage=now - timedelta(minutes=(n - 1 - i) * step_minutes),
        ))
    db.commit()


def test_collect_telemetry_writes_bounded_metrics_for_every_equipment(Session):
    with Session() as db:
        n_eq = db.query(Equipement).count()

    sched.collect_telemetry()

    with Session() as db:
        metrics = db.query(Metrique).all()
        # 2 équipements x 4 types de métriques, sur chaque tick.
        assert len(metrics) == n_eq * len(sched.METRIC_TYPES)
        assert all(m.horodatage is not None for m in metrics)
        assert all(0.0 <= m.valeur <= 100.0 for m in metrics if m.type_metrique != "bandwidth_mbps")
        assert all(0.0 <= m.valeur <= 1000.0 for m in metrics if m.type_metrique == "bandwidth_mbps")

    # Second tick : cumul (pas de remplacement), le scheduler est additif.
    sched.collect_telemetry()
    with Session() as db:
        assert db.query(Metrique).count() == n_eq * len(sched.METRIC_TYPES) * 2


def test_pin_metric_forces_next_simulated_value(Session):
    """Le pinning démo (stress disque) doit survivre au tick suivant du scheduler."""
    with Session() as db:
        eq = db.query(Equipement).filter_by(nom="SRV-T1").first()
        sched.pin_metric(eq.id, "disk_percent", 88.0)

    sched.collect_telemetry()

    with Session() as db:
        m = (db.query(Metrique)
             .filter_by(equipement_id=eq.id, type_metrique="disk_percent")
             .order_by(Metrique.horodatage.desc()).first())
        assert m is not None
        # Réversion vers la baseline + bruit faible : la valeur reste proche de 88.
        assert 80.0 <= m.valeur <= 90.0


def test_next_simulated_value_is_bounded_and_rounded():
    for _ in range(50):
        v = sched._next_simulated_value(-1, "cpu_percent")
        assert 0.0 <= v <= 100.0
        assert round(v, 2) == v
    bw = sched._next_simulated_value(-1, "bandwidth_mbps")
    assert 0.0 <= bw <= 1000.0


def test_evaluate_ttf_creates_prediction_from_recent_metrics(Session):
    with Session() as db:
        eq = db.query(Equipement).filter_by(nom="SRV-T1").first()
        seed_disk_series(db, eq.id)

    sched.evaluate_ttf()

    with Session() as db:
        eq = db.query(Equipement).filter_by(nom="SRV-T1").first()
        preds = db.query(Prediction).filter_by(equipement_id=eq.id, metrique="disk_percent").all()
        assert preds, "une prédiction TTF doit être persistée"
        assert all(p.ttf_estime >= 0.0 for p in preds)
        # La pente 60 -> 92 % sur 115 min est nette : TTF << 48 h -> alerte préventive.
        alerts = db.query(Alerte).filter(
            Alerte.statut == "active", Alerte.message.endswith("pour disk_percent sur SRV-T1", autoescape=True)
        ).all()
        assert alerts, "l'alerte préventive doit être créée"


def test_evaluate_ttf_is_silent_without_enough_data(Session):
    # Aucune métrique : le job ne doit rien planter ni rien créer.
    sched.evaluate_ttf()
    with Session() as db:
        assert db.query(Prediction).count() == 0
        assert db.query(Alerte).count() == 0


def test_recompute_health_applies_penalties_and_resets(Session):
    with Session() as db:
        eq = db.query(Equipement).filter_by(nom="SW-T1").first()
        db.add(AuditReseau(equipement_id=eq.id, constat="test", regle_cis="CIS-2.2",
                           criticite="elevee", correctif_propose="fix", statut="non_corrige",
                           date_audit=utcnow_naive()))
        db.commit()

    sched.recompute_health()

    with Session() as db:
        sw = db.query(Equipement).filter_by(nom="SW-T1").first()
        srv = db.query(Equipement).filter_by(nom="SRV-T1").first()
        assert sw.health_score == 85.0    # -15 : audit elevee ouvert
        assert srv.health_score == 100.0  # aucun défaut


def test_run_purge_never_raises(monkeypatch):
    calls = []
    monkeypatch.setattr(sched, "purge_old_data", lambda: calls.append(1) or {"metriques": 0})
    sched._run_purge()   # doit rester silencieux (erreurs avalées + loggées)
    assert calls == [1]


def test_start_scheduler_registers_jobs_and_is_idempotent(monkeypatch):
    """Les 4 jobs sont enregistrés aux bons intervalles ; double start sans effet ; stop propre."""
    noop = lambda: None
    for name in ("collect_telemetry", "evaluate_ttf", "recompute_health", "_run_purge"):
        monkeypatch.setattr(sched, name, noop)

    try:
        sched.start_scheduler()
        assert sched.scheduler.running

        expected = {
            "collect_telemetry": timedelta(seconds=10),
            "evaluate_ttf": timedelta(seconds=30),
            "recompute_health": timedelta(seconds=60),
            "purge_old_data": timedelta(minutes=10),
        }
        for job_id, interval in expected.items():
            job = sched.scheduler.get_job(job_id)
            assert job is not None, job_id
            assert job.trigger.interval == interval, job_id

        # Idempotent : un second démarrage n'ajoute ni n'écrase rien.
        n_jobs = len(sched.scheduler.get_jobs())
        sched.start_scheduler()
        assert len(sched.scheduler.get_jobs()) == n_jobs
        assert sched.scheduler.running
    finally:
        sched.stop_scheduler()

    assert not sched.scheduler.running


def test_stop_scheduler_without_start_is_safe():
    # Arrêt sans démarrage : doit rester sans effet (pas d'exception).
    if sched.scheduler.running:
        sched.stop_scheduler()
    sched.stop_scheduler()


