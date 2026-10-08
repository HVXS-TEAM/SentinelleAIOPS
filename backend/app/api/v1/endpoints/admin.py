from datetime import datetime
from typing import List
from fastapi import APIRouter, Depends, HTTPException, Response
from app.api.deps import get_current_user, require_roles, OPS_ROLES, ADMIN_ROLES
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.models.models import Alerte, JournalAudit, Utilisateur
from app.schemas.schemas import AlerteResponse, JournalAuditResponse, UtilisateurResponse
from app.services.reporting_service import ReportUnavailableError, reporting_service

router = APIRouter()


@router.get("/alertes", response_model=List[AlerteResponse])
def get_alertes(statut: str = None, db: Session = Depends(get_db)):
    query = db.query(Alerte)
    if statut:
        query = query.filter(Alerte.statut == statut)
    return query.order_by(Alerte.date_creation.desc()).all()


@router.post("/alertes/{alerte_id}/acquitter", dependencies=[Depends(require_roles(*OPS_ROLES, action="ALERTE_ACQUITTEE"))])
def acquitter_alerte(alerte_id: int, db: Session = Depends(get_db)):
    alert = db.query(Alerte).filter(Alerte.id == alerte_id).first()
    if not alert:
        raise HTTPException(status_code=404, detail="Alerte non trouvée")
    alert.statut = "acquitte"
    db.commit()
    return {"status": "success", "message": "Alerte acquittée"}


@router.get("/journal-audit", response_model=List[JournalAuditResponse], dependencies=[Depends(require_roles(*ADMIN_ROLES))])
def get_journal_audit(limit: int = 100, db: Session = Depends(get_db)):
    return db.query(JournalAudit).order_by(JournalAudit.horodatage.desc()).limit(limit).all()


@router.get("/generate-pdf-report", dependencies=[Depends(require_roles(*OPS_ROLES, action="RAPPORT_PDF"))])
def generate_pdf_report(db: Session = Depends(get_db), current_user: Utilisateur = Depends(get_current_user)):
    """Rapport d'audit PDF généré à la volée (en mémoire, rien n'est écrit sur le disque du serveur)."""
    try:
        pdf = reporting_service.build_pdf_report(db, generated_by=current_user.identifiant)
    except ReportUnavailableError as exc:
        raise HTTPException(status_code=503, detail=str(exc))
    filename = f"rapport_sentinelle_{datetime.utcnow().strftime('%Y%m%d_%H%M')}.pdf"
    return Response(
        content=pdf,
        media_type="application/pdf",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )
