"""
Sentinelle AIOps - Maintenance des données (étape 2).

    purge_old_data(...)   : rétention automatique, appelée par le scheduler (au démarrage puis toutes les 10 min)
    reset_demo_data(...)  : remise à zéro manuelle des données de démonstration (script nettoyer_donnees.py)

La rétention ne touche jamais aux alertes actives ou acquittées, ni aux équipements, utilisateurs,
audits, sauvegardes de configuration et évènements de sécurité.
"""

from datetime import datetime, timedelta
from app.core.time_utils import utcnow_naive
from typing import Dict, Optional

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.database import SessionLocal
from app.models.models import (
    Alerte, AuditReseau, Equipement, EvenementSecurite, Metrique, Prediction, SauvegardeConfig,
)

RETENTION_METRICS = timedelta(hours=24)
RETENTION_PREDICTIONS = timedelta(hours=24)
RETENTION_RESOLVED_ALERTS = timedelta(hours=24)
BATCH = 20000


def _delete_where(db: Session, model, *conditions) -> int:
    """Suppression par lots (évite un verrou SQLite long). Retourne le nombre de lignes supprimées."""
    total = 0
    while True:
        ids = select(model.id).where(*conditions).limit(BATCH)
        deleted = db.query(model).filter(model.id.in_(ids)).delete(synchronize_session=False)
        db.commit()
        total += deleted
        if deleted < BATCH:
            return total


def purge_old_data(db: Optional[Session] = None, now: Optional[datetime] = None) -> Dict[str, int]:
    """Supprime les métriques/prédictions de plus de 24 h et les alertes résolues de plus de 24 h."""
    own_session = db is None
    db = db or SessionLocal()
    now = now or utcnow_naive()
    try:
        counts = {
            "metriques": _delete_where(db, Metrique, Metrique.horodatage < now - RETENTION_METRICS),
            "predictions": _delete_where(db, Prediction, Prediction.date_calcul < now - RETENTION_PREDICTIONS),
            "alertes_resolues": _delete_where(
                db, Alerte, Alerte.statut == "resolue", Alerte.date_creation < now - RETENTION_RESOLVED_ALERTS
            ),
        }
        return counts
    except Exception:
        db.rollback()
        raise
    finally:
        if own_session:
            db.close()


def count_demo_data(db: Session) -> Dict[str, int]:
    """Ce que reset_demo_data supprimerait (pour l'aperçu 'dry-run')."""
    return {
        "alertes": db.query(Alerte).count(),
        "predictions": db.query(Prediction).count(),
        "evenements_securite": db.query(EvenementSecurite).count(),
        "audits_reseau": db.query(AuditReseau).count(),
        "sauvegardes_config": db.query(SauvegardeConfig).count(),
        "metriques": db.query(Metrique).count(),
    }


def reset_demo_data(db: Session) -> Dict[str, int]:
    """
    Remise à un état de démonstration propre : supprime alertes, prédictions, évènements de sécurité,
    audits CIS, sauvegardes de configuration et TOUTES les métriques (l'historique issu de l'ancienne
    dérive vers 100 % fausserait les courbes), puis recalcule les scores de santé.
    Conserve équipements, utilisateurs et journal d'audit. Le scheduler repart d'une télémétrie saine.
    """
    from app.services.inventory_service import inventory_service

    counts = {
        "alertes": _delete_where(db, Alerte, Alerte.id > 0),
        "predictions": _delete_where(db, Prediction, Prediction.id > 0),
        "evenements_securite": _delete_where(db, EvenementSecurite, EvenementSecurite.id > 0),
        "audits_reseau": _delete_where(db, AuditReseau, AuditReseau.id > 0),
        "sauvegardes_config": _delete_where(db, SauvegardeConfig, SauvegardeConfig.id > 0),
        "metriques": _delete_where(db, Metrique, Metrique.id > 0),
    }
    for eq in db.query(Equipement).all():
        inventory_service.calculate_health_score(db, eq.id)
    return counts
