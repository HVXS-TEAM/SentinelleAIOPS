from datetime import timedelta
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.config import settings
from app.core.security import (
    verify_password,
    create_access_token,
    decode_access_token,
    verify_totp,
    hash_password,
)
from app.models.models import Utilisateur, JournalAudit
from app.schemas.schemas import Token, UtilisateurCreate, UtilisateurResponse, TokenData

router = APIRouter()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl=f"{settings.API_V1_STR}/auth/login")


def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)) -> Utilisateur:
    payload = decode_access_token(token)
    if payload is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Jeton d'authentification invalide ou expiré",
            headers={"WWW-Authenticate": "Bearer"},
        )
    identifiant: str = payload.get("sub")
    if identifiant is None:
        raise HTTPException(status_code=401, detail="Identifiant non trouvé dans le jeton")
    user = db.query(Utilisateur).filter(Utilisateur.identifiant == identifiant).first()
    if user is None:
        raise HTTPException(status_code=401, detail="Utilisateur non trouvé")
    return user


@router.post("/login", response_model=Token)
def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(),
    totp_code: str = None,
    db: Session = Depends(get_db)
):
    user = db.query(Utilisateur).filter(Utilisateur.identifiant == form_data.username).first()
    if not user or not verify_password(form_data.password, user.hash_mot_de_passe):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Identifiant ou mot de passe incorrect",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Check MFA if active
    if user.mfa_active and user.role == "Administrateur":
        if not totp_code:
            return Token(
                access_token="",
                token_type="bearer",
                role=user.role,
                mfa_required=True
            )
        if not verify_totp(user.mfa_secret, totp_code):
            raise HTTPException(status_code=401, detail="Code MFA TOTP invalide")

    access_token = create_access_token(data={"sub": user.identifiant, "role": user.role})

    # Audit log entry
    audit = JournalAudit(
        utilisateur_id=user.id,
        action="CONNEXION_REUSSIE",
        cible=user.identifiant,
        adresse_ip="127.0.0.1"
    )
    db.add(audit)
    db.commit()

    return Token(
        access_token=access_token,
        token_type="bearer",
        role=user.role,
        mfa_required=False
    )


@router.get("/me", response_model=UtilisateurResponse)
def read_users_me(current_user: Utilisateur = Depends(get_current_user)):
    return current_user
