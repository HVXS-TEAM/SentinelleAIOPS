from datetime import datetime
from typing import Dict, Any, List
from sqlalchemy.orm import Session
from app.models.models import Equipement, Metrique, AuditReseau, EvenementSecurite


class InventoryService:
    def calculate_health_score(self, db: Session, equipement_id: int) -> float:
        """
        Calculate weighted health score (0-100) combining:
        - Security events penalty
        - Resource utilization metrics
        - Audit non-conformities
        """
        eq = db.query(Equipement).filter(Equipement.id == equipement_id).first()
        if not eq:
            return 100.0

        score = 100.0

        # Penalty for open uncorrected audit findings
        open_audits = db.query(AuditReseau).filter(
            AuditReseau.equipement_id == equipement_id,
            AuditReseau.statut == "non_corrige"
        ).all()
        for audit in open_audits:
            if audit.criticite == "elevee":
                score -= 15.0
            elif audit.criticite == "moyenne":
                score -= 8.0

        # Penalty for recent security events targeting this host IP
        sec_events = db.query(EvenementSecurite).filter(
            EvenementSecurite.source_ip == eq.ip
        ).count()
        score -= min(30.0, sec_events * 10.0)

        # Check last metrics for CPU/Disk saturation
        last_disk = db.query(Metrique).filter(
            Metrique.equipement_id == equipement_id,
            Metrique.type_metrique == "disk_percent"
        ).order_by(Metrique.horodatage.desc()).first()

        if last_disk and last_disk.valeur > 90.0:
            score -= 25.0

        final_score = max(0.0, min(100.0, round(score, 1)))
        eq.health_score = final_score
        db.commit()
        return final_score


inventory_service = InventoryService()
