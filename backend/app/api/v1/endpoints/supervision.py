from typing import List, Optional
from fastapi import APIRouter, Depends, Query, HTTPException
from app.api.deps import require_roles, OPS_ROLES, ADMIN_ROLES
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.models.models import Metrique, Prediction
from app.schemas.schemas import MetriqueResponse, PredictionResponse, MetriqueCreate
from app.services.supervision_service import supervision_service

router = APIRouter()


@router.get("/metrics", response_model=List[MetriqueResponse])
def get_metrics(
    equipement_id: Optional[int] = Query(None),
    type_metrique: Optional[str] = Query(None),
    limit: int = 100,
    db: Session = Depends(get_db)
):
    query = db.query(Metrique)
    if equipement_id:
        query = query.filter(Metrique.equipement_id == equipement_id)
    if type_metrique:
        query = query.filter(Metrique.type_metrique == type_metrique)
    return query.order_by(Metrique.horodatage.desc()).limit(limit).all()


@router.post("/metrics", response_model=MetriqueResponse, dependencies=[Depends(require_roles(*OPS_ROLES))])
def add_metric(metric: MetriqueCreate, db: Session = Depends(get_db)):
    m_db = Metrique(**metric.model_dump())
    db.add(m_db)
    db.commit()
    db.refresh(m_db)
    return m_db


@router.get("/predictions", response_model=List[PredictionResponse])
def get_predictions(db: Session = Depends(get_db)):
    return db.query(Prediction).order_by(Prediction.date_calcul.desc()).all()


@router.post("/calculate-ttf/{equipement_id}", dependencies=[Depends(require_roles(*OPS_ROLES))])
def calculate_ttf(
    equipement_id: int,
    type_metrique: str = "disk_percent",
    db: Session = Depends(get_db)
):
    ttf = supervision_service.calculate_ttf(db, equipement_id, type_metrique)
    if ttf is None:
        return {"equipement_id": equipement_id, "metrique": type_metrique, "ttf_estime": "Tendance stable ou données insuffisantes"}
    return {"equipement_id": equipement_id, "metrique": type_metrique, "ttf_estime_heures": round(ttf, 2)}
