from app.core.time_utils import utcnow_naive

from sqlalchemy import Column, Integer, String, Float, DateTime, Boolean, ForeignKey, Text
from sqlalchemy.orm import relationship
from app.core.database import Base


class Equipement(Base):
    __tablename__ = "equipements"

    id = Column(Integer, primary_key=True, index=True)
    nom = Column(String(100), nullable=False)
    ip = Column(String(45), nullable=False, unique=True, index=True)
    mac = Column(String(17), nullable=True)
    type = Column(String(50), nullable=False)  # Switch, Routeur, Serveur, Workstation
    os = Column(String(100), nullable=True)
    firmware = Column(String(50), nullable=True)
    uptime = Column(String(50), nullable=True)
    health_score = Column(Float, default=100.0)  # Score de santé 0-100
    date_decouverte = Column(DateTime, default=utcnow_naive)

    # Relationships
    metriques = relationship("Metrique", back_populates="equipement", cascade="all, delete-orphan")
    predictions = relationship("Prediction", back_populates="equipement", cascade="all, delete-orphan")
    audits = relationship("AuditReseau", back_populates="equipement", cascade="all, delete-orphan")
    sauvegardes = relationship("SauvegardeConfig", back_populates="equipement", cascade="all, delete-orphan")


class Metrique(Base):
    __tablename__ = "metriques"

    id = Column(Integer, primary_key=True, index=True)
    equipement_id = Column(Integer, ForeignKey("equipements.id"), nullable=False, index=True)
    type_metrique = Column(String(50), nullable=False)  # cpu_percent, ram_percent, disk_percent, bandwidth_mbps
    valeur = Column(Float, nullable=False)
    horodatage = Column(DateTime, default=utcnow_naive, index=True)

    equipement = relationship("Equipement", back_populates="metriques")


class Prediction(Base):
    __tablename__ = "predictions"

    id = Column(Integer, primary_key=True, index=True)
    equipement_id = Column(Integer, ForeignKey("equipements.id"), nullable=False, index=True)
    metrique = Column(String(50), nullable=False)
    ttf_estime = Column(Float, nullable=False)  # Time-To-Failure estimé en heures
    date_calcul = Column(DateTime, default=utcnow_naive)

    equipement = relationship("Equipement", back_populates="predictions")


class EvenementSecurite(Base):
    __tablename__ = "evenements_securite"

    id = Column(Integer, primary_key=True, index=True)
    source_ip = Column(String(45), nullable=False, index=True)
    equipement_id = Column(Integer, ForeignKey("equipements.id"), nullable=True, index=True)  # hôte ciblé
    utilisateur = Column(String(100), nullable=True)
    type_evenement = Column(String(100), nullable=False)  # SSH_BRUTEFORCE, PORT_SCAN, AUTH_FAILURE
    score_anomalie = Column(Float, nullable=False)  # Output d'IsolationForest
    severite = Column(String(20), nullable=False)  # info, warning, critique
    horodatage = Column(DateTime, default=utcnow_naive, index=True)


class AuditReseau(Base):
    __tablename__ = "audits_reseau"

    id = Column(Integer, primary_key=True, index=True)
    equipement_id = Column(Integer, ForeignKey("equipements.id"), nullable=False, index=True)
    constat = Column(Text, nullable=False)
    regle_cis = Column(String(100), nullable=False)  # Identifiant règle CIS Benchmark
    criticite = Column(String(20), nullable=False)  # faible, moyenne, elevee
    correctif_propose = Column(Text, nullable=True)  # Commandes Cisco IOS proposées par Ollama
    statut = Column(String(30), default="non_corrige")  # non_corrige, valide, applique
    date_audit = Column(DateTime, default=utcnow_naive)

    equipement = relationship("Equipement", back_populates="audits")


class SauvegardeConfig(Base):
    __tablename__ = "sauvegardes_config"

    id = Column(Integer, primary_key=True, index=True)
    equipement_id = Column(Integer, ForeignKey("equipements.id"), nullable=False, index=True)
    contenu = Column(Text, nullable=False)
    hash_integrite = Column(String(64), nullable=False)  # SHA-256
    date_sauvegarde = Column(DateTime, default=utcnow_naive)

    equipement = relationship("Equipement", back_populates="sauvegardes")


class Alerte(Base):
    __tablename__ = "alertes"

    id = Column(Integer, primary_key=True, index=True)
    type = Column(String(50), nullable=False)
    module_origine = Column(String(50), nullable=False)  # securite, supervision, netdevops, parc
    severite = Column(String(20), nullable=False)  # info, warning, critique
    message = Column(Text, nullable=False)
    statut = Column(String(20), default="active")  # active, acquitte, resolue
    date_creation = Column(DateTime, default=utcnow_naive, index=True)


class Utilisateur(Base):
    __tablename__ = "utilisateurs"

    id = Column(Integer, primary_key=True, index=True)
    identifiant = Column(String(50), unique=True, nullable=False, index=True)
    hash_mot_de_passe = Column(String(255), nullable=False)
    role = Column(String(30), nullable=False, default="Technicien")  # Administrateur, Technicien, Visiteur
    mfa_active = Column(Boolean, default=False)
    mfa_secret = Column(String(32), nullable=True)
    date_creation = Column(DateTime, default=utcnow_naive)

    journal_actions = relationship("JournalAudit", back_populates="utilisateur", cascade="all, delete-orphan")


class JournalAudit(Base):
    __tablename__ = "journal_audit"

    id = Column(Integer, primary_key=True, index=True)
    utilisateur_id = Column(Integer, ForeignKey("utilisateurs.id"), nullable=True)
    action = Column(String(255), nullable=False)
    cible = Column(String(255), nullable=True)
    adresse_ip = Column(String(45), nullable=True)
    horodatage = Column(DateTime, default=utcnow_naive, index=True)

    utilisateur = relationship("Utilisateur", back_populates="journal_actions")
