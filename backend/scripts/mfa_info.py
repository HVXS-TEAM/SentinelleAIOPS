"""
Sentinelle AIOps - Gestion du second facteur (TOTP) des comptes.

Usage (depuis backend/) :
    python scripts/mfa_info.py                    # liste les comptes et l'état du MFA
    python scripts/mfa_info.py admin              # secret, URI otpauth:// et code actuel
    python scripts/mfa_info.py admin --reset      # génère un NOUVEAU secret (l'ancien devient invalide)
    python scripts/mfa_info.py admin --off        # désactive le MFA de ce compte
    python scripts/mfa_info.py admin --on         # (ré)active le MFA (crée un secret s'il n'y en a pas)

Ajoute le secret dans Google Authenticator / Microsoft Authenticator / Aegis (saisie manuelle,
type "basé sur le temps"), ou utilise "le code actuel" affiché ici pour te connecter en démo.
"""
import argparse
import os
import sys

import pyotp

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.core.database import SessionLocal  # noqa: E402
from app.core.security import generate_totp_secret  # noqa: E402
from app.models.models import Utilisateur  # noqa: E402


def main() -> int:
    parser = argparse.ArgumentParser(description="MFA TOTP Sentinelle AIOps")
    parser.add_argument("identifiant", nargs="?", help="compte concerné (sinon : liste des comptes)")
    grp = parser.add_mutually_exclusive_group()
    grp.add_argument("--reset", action="store_true", help="génère un nouveau secret et active le MFA")
    grp.add_argument("--off", action="store_true", help="désactive le MFA")
    grp.add_argument("--on", action="store_true", help="active le MFA")
    args = parser.parse_args()

    db = SessionLocal()
    try:
        if not args.identifiant:
            print(f"{'IDENTIFIANT':14s} {'RÔLE':16s} MFA")
            for u in db.query(Utilisateur).order_by(Utilisateur.id).all():
                print(f"{u.identifiant:14s} {u.role:16s} {'actif' if u.mfa_active else 'inactif'}")
            return 0

        user = db.query(Utilisateur).filter(Utilisateur.identifiant == args.identifiant).first()
        if not user:
            print(f"Compte introuvable : {args.identifiant}")
            return 1

        if args.off:
            user.mfa_active = False
            db.commit()
            print(f"MFA désactivé pour {user.identifiant}.")
            return 0
        if args.reset or args.on:
            if args.reset or not user.mfa_secret:
                user.mfa_secret = generate_totp_secret()
            user.mfa_active = True
            db.commit()
            print(f"MFA activé pour {user.identifiant}" + (" avec un nouveau secret." if args.reset else "."))

        if not user.mfa_secret:
            print(f"{user.identifiant} n'a pas de secret MFA (MFA {'actif' if user.mfa_active else 'inactif'}).")
            return 0

        totp = pyotp.TOTP(user.mfa_secret)
        print(f"\nCompte        : {user.identifiant} ({user.role})")
        print(f"MFA           : {'actif' if user.mfa_active else 'inactif'}")
        print(f"Secret        : {user.mfa_secret}")
        print(f"URI otpauth   : {totp.provisioning_uri(name=user.identifiant, issuer_name='Sentinelle AIOps')}")
        print(f"Code actuel   : {totp.now()}   (valable jusqu'à la fin de la fenêtre de 30 s)")
        return 0
    finally:
        db.close()


if __name__ == "__main__":
    sys.exit(main())
