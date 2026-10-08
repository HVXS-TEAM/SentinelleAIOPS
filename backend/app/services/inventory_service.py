"""
Sentinelle AIOps - Service d'inventaire / score de santé.

`calculate_health_score` est l'UNIQUE endroit qui écrit Equipement.health_score.
Le score est recalculé de zéro à partir de l'état réel de la base :
    - audits CIS non corrigés                      (elevee -15, moyenne -8)
    - évènements de sécurité des dernières 24 h     (critique -25, warning -10, plafonné à -40)
      visant l'équipement (equipement_id) ou émis par son IP
    - prédictions TTF des 10 dernières minutes      (< 24 h : -20, < 48 h : -10, plafonné à -30)
    - dernier taux d'occupation disque > 90 %       (-25)
"""

from datetime import datetime, timedelta

from sqlalchemy import or_
from sqlalchemy.orm import Session

from app.models.models import Equipement, Metrique, AuditReseau, EvenementSecurite, Prediction

SECURITY_WINDOW = timedelta(hours=24)
TTF_WINDOW = timedelta(minutes=10)
TTF_METRICS = ("disk_percent", "cpu_percent", "ram_percent")


class InventoryService:
    def calculate_health_score(self, db: Session, equipement_id: int) -> float:
        eq = db.query(Equipement).filter(Equipement.id == equipement_id).first()
        if not eq:
            return 100.0

        now = datetime.utcnow()
        score = 100.0

        # 1) Audits CIS ouverts
        open_audits = db.query(AuditReseau).filter(
            AuditReseau.equipement_id == equipement_id,
            AuditReseau.statut == "non_corrige",
        ).all()
        for audit in open_audits:
            if audit.criticite == "elevee":
                score -= 15.0
            elif audit.criticite == "moyenne":
                score -= 8.0

        # 2) Evènements de sécurité récents visant cet équipement
        sec_events = db.query(EvenementSecurite).filter(
            or_(EvenementSecurite.equipement_id == equipement_id, EvenementSecurite.source_ip == eq.ip),
            EvenementSecurite.horodatage >= now - SECURITY_WINDOW,
        ).all()
        sec_penalty = sum(25.0 if e.severite == "critique" else 10.0 for e in sec_events)
        score -= min(40.0, sec_penalty)

        # 3) Prédictions TTF récentes (TTF minimal par métrique sur la fenêtre)
        ttf_penalty = 0.0
        for metrique in TTF_METRICS:
            recent = db.query(Prediction).filter(
                Prediction.equipement_id == equipement_id,
                Prediction.metrique == metrique,
                Prediction.date_calcul >= now - TTF_WINDOW,
            ).all()
            if not recent:
                continue
            worst = min(p.ttf_estime for p in recent)
            if worst < 24.0:
                ttf_penalty += 20.0
            elif worst < 48.0:
                ttf_penalty += 10.0
        score -= min(30.0, ttf_penalty)

        # 4) Saturation disque immédiate
        last_disk = db.query(Metrique).filter(
            Metrique.equipement_id == equipement_id,
            Metrique.type_metrique == "disk_percent",
        ).order_by(Metrique.horodatage.desc()).first()
        if last_disk and last_disk.valeur > 90.0:
            score -= 25.0

        final_score = max(0.0, min(100.0, round(score, 1)))
        eq.health_score = final_score
        db.commit()
        return final_score


inventory_service = InventoryService()
