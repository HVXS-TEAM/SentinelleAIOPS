from typing import List
from fastapi import APIRouter, Depends, HTTPException, Response
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.models.models import Alerte, JournalAudit, Utilisateur
from app.schemas.schemas import AlerteResponse, JournalAuditResponse, UtilisateurResponse
from app.services.reporting_service import reporting_service

router = APIRouter()


@router.get("/alertes", response_model=List[AlerteResponse])
def get_alertes(statut: str = None, db: Session = Depends(get_db)):
    query = db.query(Alerte)
    if statut:
        query = query.filter(Alerte.statut == statut)
    return query.order_by(Alerte.date_creation.desc()).all()


@router.post("/alertes/{alerte_id}/acquitter")
def acquitter_alerte(alerte_id: int, db: Session = Depends(get_db)):
    alert = db.query(Alerte).filter(Alerte.id == alerte_id).first()
    if not alert:
        raise HTTPException(status_code=404, detail="Alerte non trouvée")
    alert.statut = "acquitte"
    db.commit()
    return {"status": "success", "message": "Alerte acquittée"}


@router.get("/journal-audit", response_model=List[JournalAuditResponse])
def get_journal_audit(limit: int = 100, db: Session = Depends(get_db)):
    return db.query(JournalAudit).order_by(JournalAudit.horodatage.desc()).limit(limit).all()


@router.get("/generate-pdf-report")
def generate_pdf_report(db: Session = Depends(get_db)):
    pdf_file = reporting_service.generate_pdf_report(db, "rapport_sentinelle_audit.pdf")
    return FileResponse(pdf_file, media_type="application/pdf", filename="rapport_sentinelle_audit.pdf")
