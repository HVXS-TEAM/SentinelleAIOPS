from typing import List
from fastapi import APIRouter, Depends, HTTPException, Body
from app.api.deps import require_roles, OPS_ROLES, ADMIN_ROLES
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.models.models import AuditReseau, SauvegardeConfig
from app.schemas.schemas import AuditReseauResponse, SauvegardeConfigResponse
from app.services.netdevops_service import netdevops_service

router = APIRouter()


@router.get("/audits", response_model=List[AuditReseauResponse])
def get_audits(equipement_id: int = None, db: Session = Depends(get_db)):
    query = db.query(AuditReseau)
    if equipement_id:
        query = query.filter(AuditReseau.equipement_id == equipement_id)
    return query.order_by(AuditReseau.date_audit.desc()).all()


@router.post("/run-audit/{equipement_id}", response_model=List[AuditReseauResponse], dependencies=[Depends(require_roles(*OPS_ROLES, action="AUDIT_CIS_LANCE"))])
def run_audit(equipement_id: int, config_text: str = Body(..., embed=True), db: Session = Depends(get_db)):
    return netdevops_service.run_full_audit(db, equipement_id, config_text)


@router.get("/backups/{equipement_id}", response_model=List[SauvegardeConfigResponse])
def get_backups(equipement_id: int, db: Session = Depends(get_db)):
    return db.query(SauvegardeConfig).filter(SauvegardeConfig.equipement_id == equipement_id).order_by(SauvegardeConfig.date_sauvegarde.desc()).all()
