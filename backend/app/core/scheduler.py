"""
Sentinelle AIOps - Moteur d'arrière-plan autonome (Phase 1).

Ce module attache un scheduler APScheduler au cycle de vie de l'application
FastAPI afin que le back-end génère et mette à jour la télémétrie du parc
supervisé de manière 100% autonome, sans intervention manuelle sur les
endpoints REST.

Jobs enregistrés :
    - collect_telemetry   : toutes les 10s  -> métriques simulées réalistes
                             (+ métriques réelles de la machine hôte via psutil)
    - evaluate_ttf         : toutes les 30s  -> régression linéaire (TTF)
    - recompute_health     : toutes les 60s  -> score de santé consolidé

Le scheduler est démarré/arrêté via le `lifespan` de FastAPI dans main.py.
"""

import logging
import random
from datetime import datetime, timezone
from app.core.time_utils import utcnow_naive

import psutil
from apscheduler.schedulers.background import BackgroundScheduler

from app.core.database import SessionLocal
from app.core.maintenance import purge_old_data
from app.models.models import Equipement, Metrique

logger = logging.getLogger("sentinelle.scheduler")

# Types de métriques simulées suivies par équipement
METRIC_TYPES = ["cpu_percent", "ram_percent", "disk_percent", "bandwidth_mbps"]

# Etat interne en mémoire du "dernier point" simulé par (equipement_id, type_metrique)
# et de la valeur "de repos" autour de laquelle la métrique oscille.
_last_values: dict[tuple[int, str], float] = {}
_baselines: dict[tuple[int, str], float] = {}

# Nom d'hôte considéré comme "la machine locale" : si un équipement de la base
# porte ce nom, ses métriques cpu/ram/disk seront les vraies valeurs psutil
# plutôt que des valeurs simulées.
LOCAL_HOST_EQUIPEMENT_NOM = "SRV-AUTH-01"

# Seuils de démarrage réalistes par type de métrique (si aucune valeur connue)
DEFAULT_BASELINES = {
    "cpu_percent": (15.0, 45.0),
    "ram_percent": (30.0, 60.0),
    "disk_percent": (40.0, 70.0),
    "bandwidth_mbps": (5.0, 80.0),
}

# Bruit par tick (écart-type) : le disque bouge très lentement, le réseau beaucoup.
NOISE_SIGMA = {
    "cpu_percent": 2.0,
    "ram_percent": 0.6,
    "disk_percent": 0.15,
    "bandwidth_mbps": 8.0,
}
REVERSION = 0.05  # force de rappel vers la valeur de repos (évite la dérive vers 100 %)


def pin_metric(equipement_id: int, type_metrique: str, value: float) -> None:
    """Force la prochaine valeur simulée (utilisé par la démo pour rester cohérent après une injection)."""
    _last_values[(equipement_id, type_metrique)] = float(value)


def _next_simulated_value(equipement_id: int, type_metrique: str) -> float:
    """Marche aléatoire bornée avec retour à la moyenne (processus d'Ornstein-Uhlenbeck discret)."""
    key = (equipement_id, type_metrique)
    low, high = DEFAULT_BASELINES.get(type_metrique, (10.0, 50.0))
    base = _baselines.setdefault(key, random.uniform(low, high))
    current = _last_values.setdefault(key, base)

    sigma = NOISE_SIGMA.get(type_metrique, 1.0)
    new_value = current + REVERSION * (base - current) + random.gauss(0.0, sigma)

    # Bornes physiques
    if type_metrique == "bandwidth_mbps":
        new_value = max(0.0, min(1000.0, new_value))
    else:
        new_value = max(0.0, min(100.0, new_value))

    _last_values[key] = new_value
    return round(new_value, 2)


def collect_telemetry() -> None:
    """Job (10s) : collecte des métriques réelles (psutil) et simulées pour chaque équipement."""
    db = SessionLocal()
    try:
        equipements = db.query(Equipement).all()
        if not equipements:
            return

        for eq in equipements:
            is_local_host = eq.nom == LOCAL_HOST_EQUIPEMENT_NOM

            for type_metrique in METRIC_TYPES:
                if is_local_host and type_metrique in ("cpu_percent", "ram_percent", "disk_percent"):
                    if type_metrique == "cpu_percent":
                        valeur = psutil.cpu_percent(interval=None)
                    elif type_metrique == "ram_percent":
                        valeur = psutil.virtual_memory().percent
                    else:  # disk_percent
                        valeur = psutil.disk_usage("/").percent
                else:
                    valeur = _next_simulated_value(eq.id, type_metrique)

                db.add(Metrique(
                    equipement_id=eq.id,
                    type_metrique=type_metrique,
                    valeur=valeur,
                    horodatage=utcnow_naive()
                ))
        db.commit()
        logger.debug("Télémétrie collectée pour %d équipement(s).", len(equipements))
    except Exception:
        logger.exception("Erreur lors de la collecte de télémétrie.")
        db.rollback()
    finally:
        db.close()


def evaluate_ttf() -> None:
    """Job (30s) : recalcule le TTF (Time-To-Failure) pour chaque équipement / métrique surveillée."""
    from app.services.supervision_service import supervision_service

    db = SessionLocal()
    try:
        equipements = db.query(Equipement).all()
        for eq in equipements:
            for type_metrique in ("disk_percent", "cpu_percent", "ram_percent"):
                try:
                    supervision_service.calculate_ttf(db, eq.id, type_metrique)
                except Exception:
                    logger.exception(
                        "Erreur calcul TTF pour équipement %s / métrique %s", eq.id, type_metrique
                    )
    except Exception:
        logger.exception("Erreur lors de l'évaluation TTF.")
    finally:
        db.close()


def recompute_health() -> None:
    """Job (60s) : recalcule le score de santé consolidé de chaque équipement."""
    from app.services.inventory_service import inventory_service

    db = SessionLocal()
    try:
        equipements = db.query(Equipement).all()
        for eq in equipements:
            try:
                inventory_service.calculate_health_score(db, eq.id)
            except Exception:
                logger.exception("Erreur recalcul health_score pour équipement %s", eq.id)
    except Exception:
        logger.exception("Erreur lors du recalcul des scores de santé.")
    finally:
        db.close()


def _run_purge() -> None:
    """Job (10 min) : rétention des métriques, prédictions et alertes résolues."""
    try:
        counts = purge_old_data()
        if any(counts.values()):
            logger.info("Purge de rétention : %s", counts)
    except Exception:
        logger.exception("Erreur lors de la purge de rétention.")


scheduler = BackgroundScheduler(timezone="UTC")


def start_scheduler() -> None:
    """Enregistre les jobs et démarre le scheduler. Idempotent (ne redémarre pas si déjà lancé)."""
    if scheduler.running:
        logger.info("Scheduler déjà en cours d'exécution, aucun redémarrage.")
        return

    scheduler.add_job(
        collect_telemetry, "interval", seconds=10,
        id="collect_telemetry", replace_existing=True, max_instances=1
    )
    scheduler.add_job(
        evaluate_ttf, "interval", seconds=30,
        id="evaluate_ttf", replace_existing=True, max_instances=1
    )
    scheduler.add_job(
        recompute_health, "interval", seconds=60,
        id="recompute_health", replace_existing=True, max_instances=1
    )

    # Rétention : une première purge au démarrage, puis toutes les 10 minutes
    scheduler.add_job(
        _run_purge, "interval", minutes=10,
        id="purge_old_data", replace_existing=True, max_instances=1,
        next_run_time=datetime.now(timezone.utc)
    )

    scheduler.start()
    logger.info("Scheduler Sentinelle AIOps démarré (télémétrie=10s, TTF=30s, santé=60s, purge=10min).")


def stop_scheduler() -> None:
    """Arrête proprement le scheduler."""
    if scheduler.running:
        scheduler.shutdown(wait=False)
        logger.info("Scheduler Sentinelle AIOps arrêté.")
