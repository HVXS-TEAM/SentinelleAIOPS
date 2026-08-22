from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.schemas.schemas import AssistantQuery, AssistantResponse
from app.services.assistant_service import assistant_service

router = APIRouter()


@router.post("/query", response_model=AssistantResponse)
def query_assistant(payload: AssistantQuery, db: Session = Depends(get_db)):
    """Natural language read-only query endpoint for Assistant IA."""
    return assistant_service.process_natural_query(db, payload.question)
