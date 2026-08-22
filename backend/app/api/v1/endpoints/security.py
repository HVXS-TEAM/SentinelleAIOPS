from typing import List
from fastapi import APIRouter, Depends, Body
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.models.models import EvenementSecurite
from app.schemas.schemas import EvenementSecuriteResponse
from app.services.security_service import security_service

router = APIRouter()


@router.get("/events", response_model=List[EvenementSecuriteResponse])
def get_security_events(limit: int = 50, db: Session = Depends(get_db)):
    return db.query(EvenementSecurite).order_by(EvenementSecurite.horodatage.desc()).limit(limit).all()


@router.post("/analyze-logs", response_model=List[EvenementSecuriteResponse])
def analyze_log_batch(logs: List[str] = Body(...), db: Session = Depends(get_db)):
    """Analyze a batch of log lines using IsolationForest anomaly detection."""
    return security_service.analyze_log_batch(db, logs)
