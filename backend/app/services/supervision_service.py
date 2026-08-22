from datetime import datetime, timedelta
from typing import List, Optional, Tuple
import numpy as np
from sqlalchemy.orm import Session
from app.models.models import Metrique, Prediction, Equipement, Alerte


class SupervisionService:
    def calculate_ttf(
        self, db: Session, equipement_id: int, type_metrique: str = "disk_percent", critical_threshold: float = 95.0
    ) -> Optional[float]:
        """
        Estimate Time-To-Failure (TTF in hours) using linear regression (np.polyfit) on historical metric points.
        Returns TTF in hours or None if insufficient/stable data.
        """
        # Fetch last 50 points for this metric
        metrics = (
            db.query(Metrique)
            .filter(Metrique.equipement_id == equipement_id, Metrique.type_metrique == type_metrique)
            .order_by(Metrique.horodatage.asc())
            .limit(50)
            .all()
        )

        if len(metrics) < 5:
            return None

        # Convert timestamps to relative hours
        first_time = metrics[0].horodatage
        X = np.array([(m.horodatage - first_time).total_seconds() / 3600.0 for m in metrics])
        y = np.array([m.valeur for m in metrics])

        # Linear regression fit using numpy polyfit: y = slope * x + intercept
        slope, intercept = np.polyfit(X, y, 1)

        if slope <= 0.01:
            # Metric is stable or decreasing
            return None

        current_val = y[-1]
        if current_val >= critical_threshold:
            ttf_hours = 0.0
        else:
            # Solve: critical_threshold = slope * t_critical + intercept
            t_current = X[-1]
            t_critical = (critical_threshold - intercept) / slope
            ttf_hours = max(0.0, float(t_critical - t_current))

        # Save prediction to DB
        pred = Prediction(
            equipement_id=equipement_id,
            metrique=type_metrique,
            ttf_estime=ttf_hours,
            date_calcul=datetime.utcnow()
        )
        db.add(pred)

        # Trigger preventive alert if TTF < 48 hours
        if ttf_hours < 48.0:
            eq = db.query(Equipement).filter(Equipement.id == equipement_id).first()
            eq_name = eq.nom if eq else f"ID {equipement_id}"
            
            # Recalculate equipement health score
            if eq:
                eq.health_score = max(0.0, eq.health_score - 30.0)

            alert = Alerte(
                type="RessourceCritique",
                module_origine="supervision",
                severite="critique" if ttf_hours < 24.0 else "warning",
                message=f"Alerte préventive : TTF estimé à {ttf_hours:.1f}h pour {type_metrique} sur {eq_name}",
                statut="active"
            )
            db.add(alert)

        db.commit()
        return ttf_hours


supervision_service = SupervisionService()
