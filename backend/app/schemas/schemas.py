from datetime import datetime
from typing import Optional, List, Any
from pydantic import BaseModel, ConfigDict


# --- Equipement Schemas ---
class EquipementBase(BaseModel):
    nom: str
    ip: str
    mac: Optional[str] = None
    type: str  # Switch, Routeur, Serveur, Workstation
    os: Optional[str] = None
    firmware: Optional[str] = None
    uptime: Optional[str] = None
    health_score: float = 100.0


class EquipementCreate(EquipementBase):
    pass


class EquipementResponse(EquipementBase):
    id: int
    date_decouverte: datetime
    model_config = ConfigDict(from_attributes=True)


# --- Metrique Schemas ---
class MetriqueBase(BaseModel):
    equipement_id: int
    type_metrique: str  # cpu_percent, ram_percent, disk_percent, bandwidth_mbps
    valeur: float


class MetriqueCreate(MetriqueBase):
    pass


class MetriqueResponse(MetriqueBase):
    id: int
    horodatage: datetime
    model_config = ConfigDict(from_attributes=True)


# --- Prediction Schemas ---
class PredictionBase(BaseModel):
    equipement_id: int
    metrique: str
    ttf_estime: float  # heures


class PredictionResponse(PredictionBase):
    id: int
    date_calcul: datetime
    model_config = ConfigDict(from_attributes=True)


# --- EvenementSecurite Schemas ---
class EvenementSecuriteBase(BaseModel):
    source_ip: str
    utilisateur: Optional[str] = None
    type_evenement: str
    score_anomalie: float
    severite: str  # info, warning, critique


class EvenementSecuriteCreate(EvenementSecuriteBase):
    pass


class EvenementSecuriteResponse(EvenementSecuriteBase):
    id: int
    horodatage: datetime
    model_config = ConfigDict(from_attributes=True)


# --- AuditReseau Schemas ---
class AuditReseauBase(BaseModel):
    equipement_id: int
    constat: str
    regle_cis: str
    criticite: str  # faible, moyenne, elevee
    correctif_propose: Optional[str] = None
    statut: str = "non_corrige"


class AuditReseauCreate(AuditReseauBase):
    pass


class AuditReseauResponse(AuditReseauBase):
    id: int
    date_audit: datetime
    model_config = ConfigDict(from_attributes=True)


# --- SauvegardeConfig Schemas ---
class SauvegardeConfigBase(BaseModel):
    equipement_id: int
    contenu: str
    hash_integrite: str


class SauvegardeConfigResponse(SauvegardeConfigBase):
    id: int
    date_sauvegarde: datetime
    model_config = ConfigDict(from_attributes=True)


# --- Alerte Schemas ---
class AlerteBase(BaseModel):
    type: str
    module_origine: str
    severite: str  # info, warning, critique
    message: str
    statut: str = "active"


class AlerteCreate(AlerteBase):
    pass


class AlerteResponse(AlerteBase):
    id: int
    date_creation: datetime
    model_config = ConfigDict(from_attributes=True)


# --- Utilisateur & Auth Schemas ---
class UtilisateurBase(BaseModel):
    identifiant: str
    role: str = "Technicien"
    mfa_active: bool = False


class UtilisateurCreate(UtilisateurBase):
    mot_de_passe: str


class UtilisateurResponse(UtilisateurBase):
    id: int
    date_creation: datetime
    model_config = ConfigDict(from_attributes=True)


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
    role: str
    mfa_required: bool = False


class TokenData(BaseModel):
    identifiant: Optional[str] = None
    role: Optional[str] = None


# --- JournalAudit Schemas ---
class JournalAuditBase(BaseModel):
    utilisateur_id: Optional[int] = None
    action: str
    cible: Optional[str] = None
    adresse_ip: Optional[str] = None


class JournalAuditResponse(JournalAuditBase):
    id: int
    horodatage: datetime
    model_config = ConfigDict(from_attributes=True)


# --- Assistant IA Schemas ---
class AssistantQuery(BaseModel):
    question: str


class AssistantResponse(BaseModel):
    reponse: str
    donnees_associees: Optional[Any] = None
