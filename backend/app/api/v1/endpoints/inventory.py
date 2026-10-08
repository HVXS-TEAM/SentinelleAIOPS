from typing import List
from fastapi import APIRouter, Depends, HTTPException
from app.api.deps import require_roles, OPS_ROLES, ADMIN_ROLES
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.models.models import Equipement
from app.schemas.schemas import EquipementResponse, EquipementCreate
from app.services.inventory_service import inventory_service

router = APIRouter()


@router.get("/equipements", response_model=List[EquipementResponse])
def get_equipements(db: Session = Depends(get_db)):
    return db.query(Equipement).all()


@router.get("/equipements/{equipement_id}", response_model=EquipementResponse)
def get_equipement(equipement_id: int, db: Session = Depends(get_db)):
    eq = db.query(Equipement).filter(Equipement.id == equipement_id).first()
    if not eq:
        raise HTTPException(status_code=404, detail="Équipement non trouvé")
    return eq


@router.post("/equipements", response_model=EquipementResponse, dependencies=[Depends(require_roles(*OPS_ROLES, action="EQUIPEMENT_CREE"))])
def create_equipement(eq: EquipementCreate, db: Session = Depends(get_db)):
    eq_db = Equipement(**eq.model_dump())
    db.add(eq_db)
    db.commit()
    db.refresh(eq_db)
    return eq_db


@router.post("/recalculate-health/{equipement_id}", dependencies=[Depends(require_roles(*OPS_ROLES))])
def recalculate_health(equipement_id: int, db: Session = Depends(get_db)):
    score = inventory_service.calculate_health_score(db, equipement_id)
    return {"equipement_id": equipement_id, "health_score": score}
