import sys
import os
from datetime import datetime, timedelta, timezone

# Add backend directory to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'backend')))

from app.core.database import engine, Base, SessionLocal
from app.models.models import (
    Equipement,
    Metrique,
    Prediction,
    EvenementSecurite,
    AuditReseau,
    SauvegardeConfig,
    Alerte,
    Utilisateur,
    JournalAudit
)
from app.core.security import hash_password, generate_totp_secret


def init_db():
    print("Recreating database tables...")
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)

    db = SessionLocal()
    try:
        print("Seeding initial users...")
        admin_user = Utilisateur(
            identifiant="admin",
            hash_mot_de_passe=hash_password("AdminPass2026!"),
            role="Administrateur",
            mfa_active=True,
            mfa_secret=generate_totp_secret(),
            date_creation=datetime.now(timezone.utc).replace(tzinfo=None)
        )
        tech_user = Utilisateur(
            identifiant="tech",
            hash_mot_de_passe=hash_password("TechPass2026!"),
            role="Technicien",
            mfa_active=False,
            date_creation=datetime.now(timezone.utc).replace(tzinfo=None)
        )
        visitor_user = Utilisateur(
            identifiant="visiteur",
            hash_mot_de_passe=hash_password("VisitorPass2026!"),
            role="Visiteur",
            mfa_active=False,
            date_creation=datetime.now(timezone.utc).replace(tzinfo=None)
        )
        db.add_all([admin_user, tech_user, visitor_user])
        db.commit()

        print("Seeding equipment inventory...")
        eq1 = Equipement(
            nom="SW-CORE-01",
            ip="192.168.10.1",
            mac="00:1A:2B:3C:4D:5E",
            type="Switch",
            os="Cisco IOS 15.2",
            firmware="c3750e-universalk9-mz.152-4.E6",
            uptime="45 jours, 12 heures",
            health_score=92.5
        )
        eq2 = Equipement(
            nom="RTR-EDGE-01",
            ip="192.168.10.254",
            mac="00:1A:2B:99:88:77",
            type="Routeur",
            os="Cisco IOS 15.7",
            firmware="c2900-universalk9-mz.SPA.157-3.M3",
            uptime="120 jours, 04 heures",
            health_score=88.0
        )
        eq3 = Equipement(
            nom="SRV-AUTH-01",
            ip="192.168.20.10",
            mac="52:54:00:12:34:56",
            type="Serveur",
            os="Ubuntu 22.04 LTS",
            firmware="Linux Kernel 5.15.0-91-generic",
            uptime="18 jours, 09 heures",
            health_score=64.0  # Alert disk space
        )
        eq4 = Equipement(
            nom="SRV-AD-01",
            ip="192.168.20.11",
            mac="52:54:00:AB:CD:EF",
            type="Serveur",
            os="Windows Server 2022",
            firmware="NT 10.0.20348",
            uptime="60 jours, 22 heures",
            health_score=96.0
        )
        db.add_all([eq1, eq2, eq3, eq4])
        db.commit()

        print("Seeding historical metrics...")
        now = datetime.now(timezone.utc).replace(tzinfo=None)
        metrics = []
        # Generate 24h metrics for SRV-AUTH-01 (Disk filling scenario)
        for h in range(24):
            time_offset = now - timedelta(hours=24-h)
            metrics.append(Metrique(
                equipement_id=eq3.id,
                type_metrique="disk_percent",
                valeur=70.0 + (h * 1.1),  # Progresses from 70% to 95.3%
                horodatage=time_offset
            ))
            metrics.append(Metrique(
                equipement_id=eq3.id,
                type_metrique="cpu_percent",
                valeur=35.0 + (h % 5) * 4.0,
                horodatage=time_offset
            ))
            metrics.append(Metrique(
                equipement_id=eq1.id,
                type_metrique="cpu_percent",
                valeur=15.0 + (h % 3) * 2.0,
                horodatage=time_offset
            ))
        db.add_all(metrics)
        db.commit()

        print("Seeding predictions...")
        pred1 = Prediction(
            equipement_id=eq3.id,
            metrique="disk_percent",
            ttf_estime=14.5,  # 14.5 hours until saturation (95%)
            date_calcul=now
        )
        db.add(pred1)
        db.commit()

        print("Seeding security events...")
        sec1 = EvenementSecurite(
            source_ip="198.51.100.45",
            utilisateur="root",
            type_evenement="SSH_BRUTEFORCE",
            score_anomalie=-0.85,  # Negative score in IsolationForest represents anomaly
            severite="critique",
            horodatage=now - timedelta(minutes=45)
        )
        sec2 = EvenementSecurite(
            source_ip="198.51.100.45",
            utilisateur="admin",
            type_evenement="PORT_SCAN",
            score_anomalie=-0.72,
            severite="warning",
            horodatage=now - timedelta(minutes=30)
        )
        db.add_all([sec1, sec2])
        db.commit()

        print("Seeding NetDevOps CIS audits...")
        audit1 = AuditReseau(
            equipement_id=eq1.id,
            constat="Mots de passe utilisateur configurés en clair (enable password)",
            regle_cis="CIS Cisco IOS Benchmark 1.1 - Password Encryption",
            criticite="elevee",
            correctif_propose="service password-encryption\nenable secret cisco123SecretPass!",
            statut="non_corrige",
            date_audit=now - timedelta(hours=2)
        )
        audit2 = AuditReseau(
            equipement_id=eq1.id,
            constat="SNMP v1/v2c activé avec communauté par défaut 'public'",
            regle_cis="CIS Cisco IOS Benchmark 2.2 - SNMP v3 Enforce",
            criticite="elevee",
            correctif_propose="no snmp-server community public RO\nsnmp-server group AdminGroup v3 priv\nsnmp-server user AdminUser AdminGroup v3 auth sha AuthPass123! priv aes 128 PrivPass123!",
            statut="non_corrige",
            date_audit=now - timedelta(hours=2)
        )
        db.add_all([audit1, audit2])
        db.commit()

        print("Seeding alerts...")
        al1 = Alerte(
            type="RessourceCritique",
            module_origine="supervision",
            severite="critique",
            message="Saturation disque imminente sur SRV-AUTH-01 (TTF estimé: 14.5h)",
            statut="active",
            date_creation=now - timedelta(hours=1)
        )
        al2 = Alerte(
            type="AttaqueDetectee",
            module_origine="securite",
            severite="critique",
            message="Tentative brute-force SSH détectée depuis l'IP 198.51.100.45 (score anomaly: -0.85)",
            statut="active",
            date_creation=now - timedelta(minutes=45)
        )
        db.add_all([al1, al2])
        db.commit()

        print("Seeding audit log...")
        log1 = JournalAudit(
            utilisateur_id=admin_user.id,
            action="INITIALISATION_DATABASE",
            cible="systeme",
            adresse_ip="127.0.0.1",
            horodatage=now
        )
        db.add(log1)
        db.commit()

        print("Database initialized and seeded successfully!")

    except Exception as e:
        db.rollback()
        print(f"Error seeding database: {e}")
        raise
    finally:
        db.close()


if __name__ == "__main__":
    init_db()
