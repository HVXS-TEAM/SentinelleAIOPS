"""
Sentinelle AIOps - Dépendances d'authentification et d'autorisation (étape 3).

    get_current_user(...)          : exige un jeton JWT valide ; le rôle utilisé est celui de la BASE
                                     (un jeton ne peut pas "s'auto-promouvoir").
    require_roles(*roles, action=) : exige l'un des rôles listés (403 sinon, et l'accès refusé est
                                     journalisé) ; si `action` est fourni, l'action autorisée est inscrite
                                     au journal d'audit.
"""
from typing import Optional

from fastapi import Depends, HTTPException, Request, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.database import get_db
from app.core.security import decode_access_token
from app.models.models import JournalAudit, Utilisateur

ROLE_ADMIN = "Administrateur"
ROLE_TECH = "Technicien"
ROLE_VISITEUR = "Visiteur"

OPS_ROLES = (ROLE_TECH, ROLE_ADMIN)              # opérations : écriture, simulation, rapports
ADMIN_ROLES = (ROLE_ADMIN,)                      # administration : journal d'audit

oauth2_scheme = OAuth2PasswordBearer(tokenUrl=f"{settings.API_V1_STR}/auth/login")


def client_ip(request: Optional[Request]) -> Optional[str]:
    if request is not None and request.client:
        return request.client.host
    return None


def log_action(
    db: Session, user: Optional[Utilisateur], action: str, cible: Optional[str], request: Optional[Request]
) -> None:
    """Inscrit une ligne au journal d'audit (utilisateur_id vide si l'identité est inconnue)."""
    db.add(JournalAudit(
        utilisateur_id=user.id if user else None,
        action=action,
        cible=(cible or "")[:255],
        adresse_ip=client_ip(request),
    ))
    db.commit()


def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)) -> Utilisateur:
    payload = decode_access_token(token)
    if payload is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Jeton d'authentification invalide ou expiré",
            headers={"WWW-Authenticate": "Bearer"},
        )
    identifiant = payload.get("sub")
    if not identifiant:
        raise HTTPException(status_code=401, detail="Identifiant non trouvé dans le jeton",
                            headers={"WWW-Authenticate": "Bearer"})
    user = db.query(Utilisateur).filter(Utilisateur.identifiant == identifiant).first()
    if user is None:
        raise HTTPException(status_code=401, detail="Utilisateur non trouvé",
                            headers={"WWW-Authenticate": "Bearer"})
    return user


def require_roles(*roles: str, action: Optional[str] = None):
    """Fabrique une dépendance FastAPI qui restreint une route aux rôles donnés."""

    def dependency(
        request: Request,
        user: Utilisateur = Depends(get_current_user),
        db: Session = Depends(get_db),
    ) -> Utilisateur:
        cible = f"{request.method} {request.url.path}"
        if user.role not in roles:
            log_action(db, user, "ACCES_REFUSE", cible, request)
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Action réservée aux rôles : {', '.join(roles)}",
            )
        if action:
            log_action(db, user, action, cible, request)
        return user

    return dependency
