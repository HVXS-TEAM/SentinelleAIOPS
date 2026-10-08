"""
Sentinelle AIOps - Service de supervision prédictive (TTF).

Corrections de l'étape 1 :
    - la régression porte sur les points les PLUS RÉCENTS (et non les plus anciens) ;
    - une tendance n'est retenue que si elle est significative (pente minimale + R²) ;
    - une seule alerte vivante par (équipement, métrique) : mise à jour en place au lieu
      d'en créer une nouvelle toutes les 30 s ; les doublons historiques sont résolus ;
    - une alerte n'est résolue qu'après une durée de vie minimale (anti-scintillement) ;
    - ce service ne touche plus au health_score : c'est inventory_service qui en est
      l'unique responsable (il relit les prédictions récentes).
"""

from datetime import datetime, timedelta
from app.core.time_utils import utcnow_naive
from typing import List, Optional, Sequence, Tuple

import numpy as np
from sqlalchemy.orm import Session

from app.models.models import Metrique, Prediction, Equipement, Alerte

WINDOW_POINTS = 180                 # nb de points récents utilisés (~30 min à 10 s/point)
MIN_POINTS = 20                     # en dessous : pas assez de données
MIN_SLOPE = 0.05                    # pente minimale (points de % par heure)
MIN_R2 = 0.7                        # qualité minimale de l'ajustement linéaire
MIN_LEVEL = 60.0                    # pas de prédiction tant que la métrique est sous ce niveau (%)
CRITICAL_THRESHOLD = 95.0           # seuil de saturation (%)
ALERT_HORIZON_H = 48.0              # une alerte préventive est émise si TTF < 48 h
ALERT_MIN_LIFETIME = timedelta(minutes=10)   # anti-scintillement

ALERT_TYPE = "RessourceCritique"
ALERT_MODULE = "supervision"


class SupervisionService:
    def __init__(self):
        # Dernier instant où le dépassement (TTF < horizon) a été constaté, par (équipement, métrique).
        # Sert à l'anti-scintillement : une alerte réutilisée garde sa date de création d'origine.
        self._last_breach: dict[Tuple[int, str], datetime] = {}

    # ------------------------------------------------------------------ maths
    @staticmethod
    def estimate_ttf(
        times_h: Sequence[float],
        values: Sequence[float],
        critical_threshold: float = CRITICAL_THRESHOLD,
        min_points: int = MIN_POINTS,
    ) -> Optional[float]:
        """
        Fonction pure : TTF (heures) par régression linéaire, ou None si la tendance
        est absente, décroissante, trop faible ou non significative.
        """
        x = np.asarray(times_h, dtype=float)
        y = np.asarray(values, dtype=float)
        if len(y) < min_points or len(y) < 2 or np.ptp(x) <= 0:
            return None

        slope, intercept = np.polyfit(x, y, 1)
        if slope < MIN_SLOPE:
            return None

        fitted = slope * x + intercept
        ss_res = float(np.sum((y - fitted) ** 2))
        ss_tot = float(np.sum((y - y.mean()) ** 2))
        r2 = 1.0 - ss_res / ss_tot if ss_tot > 0 else 0.0
        if r2 < MIN_R2:
            return None
        if y[-1] < MIN_LEVEL:   # bruit d'une métrique basse : extrapoler vers 95 % n'aurait pas de sens
            return None

        if y[-1] >= critical_threshold:
            return 0.0
        current_fitted = slope * x[-1] + intercept
        return max(0.0, float((critical_threshold - current_fitted) / slope))

    # ------------------------------------------------------------- alertes
    @staticmethod
    def _alert_suffix(metrique: str, eq_nom: str) -> str:
        return f"pour {metrique} sur {eq_nom}"

    def _matching_alerts(self, db: Session, metrique: str, eq_nom: str) -> List[Alerte]:
        return (
            db.query(Alerte)
            .filter(
                Alerte.module_origine == ALERT_MODULE,
                Alerte.type == ALERT_TYPE,
                Alerte.statut.in_(["active", "acquitte"]),
                Alerte.message.endswith(self._alert_suffix(metrique, eq_nom), autoescape=True),
            )
            .order_by(Alerte.date_creation.desc(), Alerte.id.desc())
            .all()
        )

    def _sync_alert(
        self, db: Session, eq: Equipement, metrique: str, ttf_hours: Optional[float], now: datetime
    ) -> None:
        existing = self._matching_alerts(db, metrique, eq.nom)
        breaching = ttf_hours is not None and ttf_hours < ALERT_HORIZON_H

        if breaching:
            severite = "critique" if ttf_hours < 24.0 else "warning"
            message = f"Alerte préventive : TTF estimé à {ttf_hours:.1f}h {self._alert_suffix(metrique, eq.nom)}"
            self._last_breach[(eq.id, metrique)] = now
            if existing:
                keep, duplicates = existing[0], existing[1:]
                if keep.statut == "active":          # une alerte acquittée n'est pas ré-ouverte
                    keep.message = message
                    keep.severite = severite
                for dup in duplicates:               # nettoyage des doublons historiques
                    dup.statut = "resolue"
            else:
                db.add(Alerte(
                    type=ALERT_TYPE, module_origine=ALERT_MODULE,
                    severite=severite, message=message, statut="active", date_creation=now,
                ))
        else:
            # Condition disparue : résolution après durée de vie minimale
            for al in existing:
                ref = max(al.date_creation, self._last_breach.get((eq.id, metrique), al.date_creation))
                if now - ref >= ALERT_MIN_LIFETIME:
                    al.statut = "resolue"

    # -------------------------------------------------------- API du service
    def evaluate_series(
        self,
        db: Session,
        equipement_id: int,
        type_metrique: str,
        points: List[Tuple[datetime, float]],
        min_points: int = MIN_POINTS,
    ) -> Optional[float]:
        """Évalue une série [(horodatage, valeur), ...] triée par date, enregistre prédiction + alerte."""
        eq = db.query(Equipement).filter(Equipement.id == equipement_id).first()
        if eq is None or not points:
            return None

        t0 = points[0][0]
        times_h = [(t - t0).total_seconds() / 3600.0 for t, _ in points]
        values = [v for _, v in points]
        ttf_hours = self.estimate_ttf(times_h, values, min_points=min_points)

        now = utcnow_naive()
        if ttf_hours is not None:
            db.add(Prediction(
                equipement_id=equipement_id, metrique=type_metrique,
                ttf_estime=ttf_hours, date_calcul=now,
            ))
        self._sync_alert(db, eq, type_metrique, ttf_hours, now)
        db.commit()
        return ttf_hours

    def calculate_ttf(
        self, db: Session, equipement_id: int, type_metrique: str = "disk_percent",
        critical_threshold: float = CRITICAL_THRESHOLD,
    ) -> Optional[float]:
        """TTF (heures) calculé sur les WINDOW_POINTS points les plus récents de la métrique."""
        rows = (
            db.query(Metrique)
            .filter(Metrique.equipement_id == equipement_id, Metrique.type_metrique == type_metrique)
            .order_by(Metrique.horodatage.desc())
            .limit(WINDOW_POINTS)
            .all()
        )
        rows.reverse()  # ordre chronologique
        if len(rows) < MIN_POINTS:
            return None
        return self.evaluate_series(
            db, equipement_id, type_metrique, [(m.horodatage, m.valeur) for m in rows]
        )


supervision_service = SupervisionService()
