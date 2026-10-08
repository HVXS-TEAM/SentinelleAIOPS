"""
Vérification du front-end de l'étape 3 (connexion réelle, MFA, rôles, session expirée).
Le back-end doit tourner sur http://localhost:8000.

Usage (depuis "Sentinelle AIOPS/frontend/", même venv que Streamlit) :
    python verif_etape3_front.py
Le secret MFA de l'admin est lu dans ../backend/sentinelle_aiops.db (autre chemin : variable SENTINELLE_DB).
"""
import base64
import hashlib
import hmac
import os
import sqlite3
import struct
import sys
import time
from pathlib import Path
from unittest import mock

import requests

ROOT = Path(__file__).resolve().parent
os.chdir(ROOT)
sys.path.insert(0, str(ROOT))
from streamlit.testing.v1 import AppTest  # noqa: E402

API = "http://localhost:8000/api/v1"
DB = os.environ.get("SENTINELLE_DB", str(ROOT.parent / "backend" / "sentinelle_aiops.db"))
PW = {"admin": "AdminPass2026!", "tech": "TechPass2026!", "visiteur": "VisitorPass2026!"}
ok_all = True


def check(label, cond, detail=""):
    global ok_all
    ok_all &= bool(cond)
    print(f"  [{'OK' if cond else 'ECHEC'}] {label} {detail}")


def totp_now(secret_b32: str) -> str:
    """Code TOTP RFC 6238 (SHA-1, 30 s, 6 chiffres) sans dépendance externe."""
    key = base64.b32decode(secret_b32.upper() + "=" * (-len(secret_b32) % 8))
    counter = struct.pack(">Q", int(time.time()) // 30)
    h = hmac.new(key, counter, hashlib.sha1).digest()
    o = h[-1] & 0x0F
    return f"{(struct.unpack('>I', h[o:o + 4])[0] & 0x7FFFFFFF) % 1_000_000:06d}"


def admin_secret() -> str:
    con = sqlite3.connect(f"file:{DB}?mode=ro", uri=True)
    try:
        return con.execute("SELECT mfa_secret FROM utilisateurs WHERE identifiant='admin'").fetchone()[0]
    finally:
        con.close()


def fresh():
    at = AppTest.from_file(str(ROOT / "app.py"), default_timeout=40)
    at.run()
    return at


def submit(at, user, pwd, totp=None):
    at.text_input(key="login_identifiant").set_value(user)
    at.text_input(key="login_password").set_value(pwd)
    if totp is not None:
        at.text_input(key="login_totp").set_value(totp)
    at.button(key="login_submit").click()
    at.run()
    return at


def ss(at, key):
    return at.session_state[key] if key in at.session_state else None


def token_of(user):
    return requests.post(f"{API}/auth/login", data={"username": user, "password": PW[user]}, timeout=10).json()["access_token"]


def open_page(page, user, role, token=None):
    at = AppTest.from_file(str(ROOT / "app.py"), default_timeout=40)
    at.session_state["authenticated"] = True
    at.session_state["username"] = user
    at.session_state["role"] = role
    at.session_state["token"] = token_of(user) if token is None else token
    at.switch_page(page)
    at.run()
    return at


def has_button(at, key):
    try:
        at.button(key=key)
        return True
    except Exception:
        return False


print("A) Connexion : refus réel, pas de repli démo quand le back-end répond")
at = submit(fresh(), "tech", "faux")
check("mauvais mot de passe : non authentifié", not ss(at, "authenticated"))
check("message d'erreur affiché", len(at.error) >= 1)

print("B) Technicien : connexion avec jeton")
at = submit(fresh(), "tech", PW["tech"])
check("authentifié, rôle Technicien, jeton présent",
      ss(at, "authenticated") and ss(at, "role") == "Technicien" and bool(ss(at, "token")))

print("C) Administrateur : double authentification")
at = submit(fresh(), "admin", PW["admin"])
check("1er clic : code MFA demandé, pas encore connecté", (not ss(at, "authenticated")) and ss(at, "mfa_pending"))
check("champ « CODE MFA » affiché", any(t.key == "login_totp" for t in at.text_input))
at = submit(at, "admin", PW["admin"], "000000")
check("mauvais code : refus", not ss(at, "authenticated"))
at = submit(at, "admin", PW["admin"], totp_now(admin_secret()))
check("bon code : connecté Administrateur avec jeton",
      ss(at, "authenticated") and ss(at, "role") == "Administrateur" and bool(ss(at, "token")))

print("D) Back-end injoignable : repli démo hors-ligne")
with mock.patch("requests.post", side_effect=requests.exceptions.ConnectionError("down")):
    at = submit(fresh(), "visiteur", PW["visiteur"])
check("comptes démo acceptés sans jeton", ss(at, "authenticated") and not ss(at, "token"))
with mock.patch("requests.post", side_effect=requests.exceptions.ConnectionError("down")):
    at = submit(fresh(), "visiteur", "faux")
check("mauvais mot de passe hors-ligne : refus", not ss(at, "authenticated"))

print("E) Rôles sur les pages")
for page in ("pages/1_Dashboard.py", "pages/2_Sécurité.py"):
    at = open_page(page, "tech", "Technicien")
    check(f"{page} technicien : sans erreur, panneau démo présent", not at.exception and has_button(at, "demo_btn_reset"))
    at = open_page(page, "visiteur", "Visiteur")
    check(f"{page} visiteur : sans erreur, panneau démo absent", not at.exception and not has_button(at, "demo_btn_reset"))

print("F) Session expirée")
at = open_page("pages/1_Dashboard.py", "tech", "Technicien", token="jeton.invalide.xyz")
check("jeton invalide détecté (401)", ss(at, "session_expired") is True)
at.run()
check("retour à la connexion (session purgée)", not ss(at, "authenticated"))

print("\nRESULTAT :", "TOUT EST OK" if ok_all else "DES VERIFICATIONS ONT ECHOUE")
sys.exit(0 if ok_all else 1)
