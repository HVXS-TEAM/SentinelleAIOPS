import time
from typing import Dict, List, Optional

from fastapi import APIRouter, Depends, Form, HTTPException, Request, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app.api.deps import client_ip, get_current_user, log_action  # noqa: F401  (get_current_user ré-exporté)
from app.core.database import get_db
from app.core.security import create_access_token, verify_password, verify_totp
from app.models.models import Utilisateur
from app.schemas.schemas import Token, UtilisateurResponse

router = APIRouter()

# --- Protection anti force brute sur /login (en mémoire, par identifiant + IP) ---------------------
MAX_FAILURES = 5
LOCKOUT_WINDOW_S = 300
_login_failures: Dict[str, List[float]] = {}


def _key(identifiant: str, ip: Optional[str]) -> str:
    return f"{(identifiant or '').lower()}|{ip or '-'}"


def _recent_failures(key: str) -> List[float]:
    now = time.monotonic()
    recent = [t for t in _login_failures.get(key, []) if now - t < LOCKOUT_WINDOW_S]
    _login_failures[key] = recent
    return recent


def _register_failure(key: str) -> None:
    _recent_failures(key).append(time.monotonic())


@router.post("/login", response_model=Token)
def login_for_access_token(
    request: Request,
    form_data: OAuth2PasswordRequestForm = Depends(),
    totp_code: Optional[str] = Form(None),
    db: Session = Depends(get_db),
):
    ip = client_ip(request)
    key = _key(form_data.username, ip)

    if len(_recent_failures(key)) >= MAX_FAILURES:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Trop de tentatives échouées. Réessayez dans quelques minutes.",
        )

    user = db.query(Utilisateur).filter(Utilisateur.identifiant == form_data.username).first()
    if not user or not verify_password(form_data.password, user.hash_mot_de_passe):
        _register_failure(key)
        log_action(db, user, "CONNEXION_ECHEC", form_data.username, request)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Identifiant ou mot de passe incorrect",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Second facteur (TOTP) pour tout compte qui l'a activé
    if user.mfa_active:
        if not user.mfa_secret:
            log_action(db, user, "CONNEXION_ECHEC", f"{user.identifiant} (MFA mal configuré)", request)
            raise HTTPException(status_code=401, detail="MFA activé mais non configuré pour ce compte")
        if not totp_code:
            return Token(access_token="", token_type="bearer", role=user.role, mfa_required=True)
        if not verify_totp(user.mfa_secret, totp_code.strip()):
            _register_failure(key)
            log_action(db, user, "MFA_ECHEC", user.identifiant, request)
            raise HTTPException(status_code=401, detail="Code MFA TOTP invalide")

    _login_failures.pop(key, None)
    access_token = create_access_token(data={"sub": user.identifiant, "role": user.role})
    log_action(db, user, "CONNEXION_REUSSIE", user.identifiant, request)

    return Token(access_token=access_token, token_type="bearer", role=user.role, mfa_required=False)


@router.get("/me", response_model=UtilisateurResponse)
def read_users_me(current_user: Utilisateur = Depends(get_current_user)):
    return current_user
