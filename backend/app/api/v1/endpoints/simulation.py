"""
Sentinelle AIOps - Routeur de Simulation Interactif (Phase 2).

Permet de déclencher en 1 clic les événements des 6 Actes de la
démonstration BTS, sans dépendre d'une machine Kali Linux ou de
manipulations manuelles sur le réseau. Chaque endpoint réutilise
tel quel les services métiers existants (aucune altération) :
    - security_service.analyze_log_batch      -> Isolation Forest
    - supervision_service.calculate_ttf       -> Régression linéaire
    - netdevops_service.run_full_audit        -> Audit CIS Benchmark

Un état en mémoire (SIMULATION_STATE) garde la trace de tout ce qui a
été injecté par ces endpoints, afin que /reset puisse purger
uniquement les données de simulation et restaurer les scores de
santé initiaux, sans toucher aux vraies données de télémétrie
générées par le scheduler (Phase 1).
"""

from datetime import datetime, timedelta
from typing import Dict, Any, List

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.models import (
    Equipement, Metrique, Prediction, Alerte, EvenementSecurite, AuditReseau, SauvegardeConfig
)
from app.services.security_service import security_service
from app.services.supervision_service import supervision_service
from app.services.netdevops_service import netdevops_service

router = APIRouter()

# --- Etat en mémoire de la session de simulation en cours -------------------
# Réinitialisé à chaque appel de /reset. Ne survit pas à un redémarrage du
# serveur (ce qui est acceptable : au redémarrage, il n'y a de toute façon
# rien à purger).
SIMULATION_STATE: Dict[str, Any] = {
    "evenements_securite_ids": [],
    "alertes_ids": [],
    "metriques_ids": [],
    "predictions_ids": [],
    "audits_ids": [],
    "sauvegardes_ids": [],
    "health_snapshots": {},   # equipement_id -> health_score AVANT simulation
}


def _get_or_create_equipement(db: Session, nom: str, ip: str, type_eq: str) -> Equipement:
    """Récupère l'équipement par son nom, ou le crée s'il n'existe pas encore en base."""
    eq = db.query(Equipement).filter(Equipement.nom == nom).first()
    if eq:
        return eq
    eq = Equipement(nom=nom, ip=ip, type=type_eq, health_score=100.0)
    db.add(eq)
    db.commit()
    db.refresh(eq)
    return eq


def _snapshot_health(equipement_id: int, current_score: float) -> None:
    """Mémorise le score de santé initial d'un équipement, une seule fois par session de simulation."""
    if equipement_id not in SIMULATION_STATE["health_snapshots"]:
        SIMULATION_STATE["health_snapshots"][equipement_id] = current_score


# --- Acte 3 : Sécurité -------------------------------------------------------

@router.post("/inject-bruteforce")
def inject_bruteforce(db: Session = Depends(get_db)):
    """
    Injecte une salve de tentatives SSH infructueuses depuis une IP externe
    simulée (198.51.100.45) ciblant le compte root, aux côtés d'un peu de
    bruit "normal" pour donner à l'Isolation Forest un minimum d'échantillons
    à comparer. Déclenche security_service.analyze_log_batch tel quel.
    """
    target_nom = "SRV-AUTH-01"
    target = _get_or_create_equipement(db, target_nom, "192.168.20.10", "Serveur")
    _snapshot_health(target.id, target.health_score)

    now = datetime.utcnow()
    log_lines: List[str] = []

    # Bruit "normal" : plusieurs IP légitimes avec 1 à 2 tentatives échouées
    # chacune (fautes de frappe habituelles). Nécessaire pour que l'Isolation
    # Forest ait une base de comparaison suffisante et isole nettement
    # l'attaquant plutôt que de produire des scores dégénérés à 2 échantillons.
    bruit = [
        ("203.0.113.10", "admin", 1),
        ("203.0.113.22", "jkouokam", 1),
        ("198.18.0.5", "backup", 2),
        ("192.0.2.77", "svc-monitoring", 1),
    ]
    for ip, user, count in bruit:
        for i in range(count):
            ts = (now - timedelta(seconds=(20 + i) * 3)).strftime("%b %d %H:%M:%S")
            log_lines.append(
                f"{ts} {target_nom.lower()} sshd[{1000 + i}]: Failed password for {user} from {ip} port {50000 + i} ssh2"
            )

    # Attaque simulée : 10 tentatives échouées depuis 198.51.100.45 ciblant root
    for i in range(10):
        ts = (now - timedelta(seconds=(10 - i) * 3)).strftime("%b %d %H:%M:%S")
        log_lines.append(
            f"{ts} {target_nom.lower()} sshd[{2000 + i}]: Failed password for root from 198.51.100.45 port {54000 + i} ssh2"
        )

    events_before = {e.id for e in db.query(EvenementSecurite.id).all()}
    alerts_before = {a.id for a in db.query(Alerte.id).all()}

    events = security_service.analyze_log_batch(db, log_lines)

    # Repérer les nouvelles alertes créées par ce même appel
    new_alerts = db.query(Alerte).filter(~Alerte.id.in_(alerts_before)).all() if alerts_before else \
        db.query(Alerte).all()

    for ev in events:
        SIMULATION_STATE["evenements_securite_ids"].append(ev.id)
    for al in new_alerts:
        SIMULATION_STATE["alertes_ids"].append(al.id)

    # Pénalité de score de santé sur l'hôte ciblé (sshd), comme un incident réel
    critical = any(ev.severite == "critique" for ev in events)
    if critical:
        target.health_score = max(0.0, target.health_score - 25.0)
        db.commit()

    return {
        "scenario": "Acte 3 - Injection SSH Bruteforce",
        "ip_attaquante": "198.51.100.45",
        "evenements_detectes": [
            {"id": ev.id, "type": ev.type_evenement, "severite": ev.severite, "score_anomalie": round(ev.score_anomalie, 3)}
            for ev in events
        ],
        "alertes_generees": len(new_alerts),
        "health_score_hote_cible": target.health_score,
    }


# --- Acte 2 : Supervision ----------------------------------------------------

@router.post("/stress-disk")
def stress_disk(db: Session = Depends(get_db)):
    """
    Simule une montée rapide du taux d'occupation disque (60% -> 88%) sur
    SRV-APP-01, puis déclenche supervision_service.calculate_ttf tel quel
    pour faire chuter le TTF sous 24h et générer l'alerte préventive.
    """
    target = _get_or_create_equipement(db, "SRV-APP-01", "192.168.20.12", "Serveur")
    _snapshot_health(target.id, target.health_score)

    now = datetime.utcnow()
    progression = [60.0, 66.0, 72.0, 78.0, 83.0, 88.0]
    inserted_ids = []

    # Points historiques rapprochés (une valeur toutes les ~8 minutes dans le
    # passé simulé) pour obtenir une pente de régression nette et un TTF < 24h.
    for idx, valeur in enumerate(progression):
        horodatage = now - timedelta(minutes=(len(progression) - 1 - idx) * 8)
        m = Metrique(
            equipement_id=target.id,
            type_metrique="disk_percent",
            valeur=valeur,
            horodatage=horodatage
        )
        db.add(m)
        db.flush()
        inserted_ids.append(m.id)

    db.commit()
    SIMULATION_STATE["metriques_ids"].extend(inserted_ids)

    ttf_hours = supervision_service.calculate_ttf(db, target.id, "disk_percent")

    # Retrouver la prédiction fraîchement créée pour pouvoir la purger au reset
    last_pred = (
        db.query(Prediction)
        .filter(Prediction.equipement_id == target.id, Prediction.metrique == "disk_percent")
        .order_by(Prediction.date_calcul.desc())
        .first()
    )
    if last_pred:
        SIMULATION_STATE["predictions_ids"].append(last_pred.id)

    db.refresh(target)

    return {
        "scenario": "Acte 2 - Stress Disque",
        "equipement": target.nom,
        "progression_pourcent": progression,
        "ttf_estime_heures": ttf_hours,
        "health_score_equipement": target.health_score,
    }


# --- Acte 4 : NetDevOps -------------------------------------------------------

@router.post("/cis-flaw")
def cis_flaw(db: Session = Depends(get_db)):
    """
    Injecte une configuration Cisco IOS non conforme (SNMP communautaire par
    défaut + absence de chiffrement des mots de passe + absence de bannière
    légale) sur un switch du parc, et déclenche netdevops_service.run_full_audit
    tel quel pour remonter les non-conformités CIS et proposer un correctif.
    """
    target = _get_or_create_equipement(db, "SW-CORE-01", "192.168.10.1", "Switch")
    _snapshot_health(target.id, target.health_score)

    config_text = (
        "hostname SW-CORE-01\n"
        "!\n"
        "snmp-server community public RO\n"
        "snmp-server community private RW\n"
        "!\n"
        "interface GigabitEthernet0/1\n"
        " switchport mode access\n"
        "!\n"
        "line vty 0 4\n"
        " login local\n"
        "!\n"
        "end\n"
    )

    audits_before = {a.id for a in db.query(AuditReseau.id).all()}
    backups_before = {b.id for b in db.query(SauvegardeConfig.id).all()}

    audits = netdevops_service.run_full_audit(db, target.id, config_text)

    new_backups = db.query(SauvegardeConfig).filter(~SauvegardeConfig.id.in_(backups_before)).all() if backups_before else \
        db.query(SauvegardeConfig).all()

    for a in audits:
        SIMULATION_STATE["audits_ids"].append(a.id)
    for b in new_backups:
        SIMULATION_STATE["sauvegardes_ids"].append(b.id)

    # Pénalité de santé proportionnelle au nombre de non-conformités élevées
    nb_elevees = sum(1 for a in audits if a.criticite == "elevee")
    if nb_elevees:
        target.health_score = max(0.0, target.health_score - 10.0 * nb_elevees)
        db.commit()
        db.refresh(target)

    return {
        "scenario": "Acte 4 - Non-conformité CIS Cisco",
        "equipement": target.nom,
        "non_conformites": [
            {"regle_cis": a.regle_cis, "criticite": a.criticite, "constat": a.constat}
            for a in audits
        ],
        "health_score_equipement": target.health_score,
    }


# --- Remise à zéro -------------------------------------------------------------

@router.post("/reset")
def reset_simulation(db: Session = Depends(get_db)):
    """
    Purge uniquement les données injectées par les endpoints de simulation
    ci-dessus (jamais les vraies données du scheduler Phase 1) et restaure
    les scores de santé des équipements touchés à leur valeur d'avant
    simulation.
    """
    purge_counts = {
        "evenements_securite": 0,
        "alertes": 0,
        "metriques": 0,
        "predictions": 0,
        "audits": 0,
        "sauvegardes": 0,
    }

    if SIMULATION_STATE["evenements_securite_ids"]:
        purge_counts["evenements_securite"] = (
            db.query(EvenementSecurite)
            .filter(EvenementSecurite.id.in_(SIMULATION_STATE["evenements_securite_ids"]))
            .delete(synchronize_session=False)
        )
    if SIMULATION_STATE["alertes_ids"]:
        purge_counts["alertes"] = (
            db.query(Alerte)
            .filter(Alerte.id.in_(SIMULATION_STATE["alertes_ids"]))
            .delete(synchronize_session=False)
        )
    if SIMULATION_STATE["metriques_ids"]:
        purge_counts["metriques"] = (
            db.query(Metrique)
            .filter(Metrique.id.in_(SIMULATION_STATE["metriques_ids"]))
            .delete(synchronize_session=False)
        )
    if SIMULATION_STATE["predictions_ids"]:
        purge_counts["predictions"] = (
            db.query(Prediction)
            .filter(Prediction.id.in_(SIMULATION_STATE["predictions_ids"]))
            .delete(synchronize_session=False)
        )
    if SIMULATION_STATE["audits_ids"]:
        purge_counts["audits"] = (
            db.query(AuditReseau)
            .filter(AuditReseau.id.in_(SIMULATION_STATE["audits_ids"]))
            .delete(synchronize_session=False)
        )
    if SIMULATION_STATE["sauvegardes_ids"]:
        purge_counts["sauvegardes"] = (
            db.query(SauvegardeConfig)
            .filter(SauvegardeConfig.id.in_(SIMULATION_STATE["sauvegardes_ids"]))
            .delete(synchronize_session=False)
        )

    # Restauration des scores de santé initiaux
    restored = []
    for equipement_id, original_score in SIMULATION_STATE["health_snapshots"].items():
        eq = db.query(Equipement).filter(Equipement.id == equipement_id).first()
        if eq:
            eq.health_score = original_score
            restored.append({"equipement": eq.nom, "health_score_restaure": original_score})

    db.commit()

    # Réinitialisation de l'état en mémoire
    SIMULATION_STATE["evenements_securite_ids"].clear()
    SIMULATION_STATE["alertes_ids"].clear()
    SIMULATION_STATE["metriques_ids"].clear()
    SIMULATION_STATE["predictions_ids"].clear()
    SIMULATION_STATE["audits_ids"].clear()
    SIMULATION_STATE["sauvegardes_ids"].clear()
    SIMULATION_STATE["health_snapshots"].clear()

    return {
        "scenario": "Reset - Retour à l'état nominal",
        "elements_purges": purge_counts,
        "scores_sante_restaures": restored,
    }