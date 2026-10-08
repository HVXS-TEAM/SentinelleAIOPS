"""
Sentinelle AIOps - Remise à zéro des données de démonstration.

Usage (depuis le dossier backend/, serveur ARRÊTÉ) :
    python scripts/nettoyer_donnees.py            # aperçu : n'écrit rien
    python scripts/nettoyer_donnees.py --apply    # sauvegarde la base puis nettoie

Supprime : alertes, prédictions, évènements de sécurité, audits CIS, sauvegardes de configuration
et toutes les métriques. Conserve : équipements, utilisateurs, journal d'audit.
Les scores de santé sont recalculés ensuite. Laisse ensuite le back-end tourner ~10 min avant la démo
pour que les courbes aient un historique.
"""
import argparse
import os
import shutil
import sys
from datetime import datetime

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.core.config import settings  # noqa: E402
from app.core.database import SessionLocal, engine  # noqa: E402
from app.core.maintenance import count_demo_data, reset_demo_data  # noqa: E402
from app.core.migrations import ensure_schema  # noqa: E402


def main() -> int:
    parser = argparse.ArgumentParser(description="Nettoyage des données de démonstration Sentinelle AIOps")
    parser.add_argument("--apply", action="store_true", help="applique réellement le nettoyage (sinon aperçu)")
    args = parser.parse_args()

    ensure_schema(engine)
    db = SessionLocal()
    try:
        print("Données concernées :")
        for nom, n in count_demo_data(db).items():
            print(f"  - {nom:22s} {n}")

        if not args.apply:
            print("\nAperçu uniquement. Relance avec --apply pour nettoyer (une sauvegarde sera créée).")
            return 0

        if settings.DATABASE_URL.startswith("sqlite"):
            db_file = engine.url.database          # fichier réellement utilisé (tient compte du .env)
            backup = f"{db_file}.bak_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            shutil.copy2(db_file, backup)
            print(f"\nSauvegarde créée : {backup}")

        deleted = reset_demo_data(db)
        print("\nSupprimé :")
        for nom, n in deleted.items():
            print(f"  - {nom:22s} {n}")
    finally:
        db.close()

    if settings.DATABASE_URL.startswith("sqlite"):
        with engine.connect().execution_options(isolation_level="AUTOCOMMIT") as conn:
            conn.exec_driver_sql("VACUUM")
        print("\nBase compactée (VACUUM). Nettoyage terminé.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
