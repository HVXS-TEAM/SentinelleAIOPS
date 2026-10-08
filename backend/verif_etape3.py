"""
Vérification live de l'étape 3 : authentification, rôles, MFA, anti force brute, journal d'audit.
Le back-end doit tourner sur http://localhost:8000 (lancé depuis backend/).
Usage :  python verif_etape3.py      (dure environ 15 s)
"""
import os
import sqlite3
import sys

import pyotp
import requests

sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))
from app.core.database import engine  # noqa: E402

API = "http://localhost:8000/api/v1"
PWD = {"admin": "AdminPass2026!", "tech": "TechPass2026!", "visiteur": "VisitorPass2026!"}
ok_all = True


def check(label, cond, detail=""):
    global ok_all
    ok_all &= bool(cond)
    print(f"  [{'OK' if cond else 'ECHEC'}] {label} {detail}")


def login(user, pwd, totp=None):
    data = {"username": user, "password": pwd}
    if totp:
        data["totp_code"] = totp
    return requests.post(f"{API}/auth/login", data=data, timeout=10)


def bearer(user):
    r = login(user, PWD[user])
    return {"Authorization": f"Bearer {r.json()['access_token']}"}


def code(method, path, headers=None):
    return requests.request(method, f"{API}{path}", headers=headers, timeout=15).status_code


print("1) Sans jeton : tout est refusé")
check("GET /inventory/equipements -> 401", code("GET", "/inventory/equipements") == 401)
check("POST /simulation/reset -> 401", code("POST", "/simulation/reset") == 401)
check("mauvais mot de passe -> 401", login("tech", "faux").status_code == 401)

print("2) Visiteur : lecture seule")
h = bearer("visiteur")
check("lecture du parc -> 200", code("GET", "/inventory/equipements", h) == 200)
check("simulation -> 403", code("POST", "/simulation/reset", h) == 403)
check("journal d'audit -> 403", code("GET", "/admin/journal-audit", h) == 403)

print("3) Technicien : opérations, pas d'administration")
h = bearer("tech")
check("simulation reset -> 200", code("POST", "/simulation/reset", h) == 200)
check("journal d'audit -> 403", code("GET", "/admin/journal-audit", h) == 403)

print("4) Administrateur : MFA obligatoire")
r = login("admin", PWD["admin"])
check("sans code : mfa_required, aucun jeton délivré", r.status_code == 200 and r.json().get("mfa_required") is True and not r.json().get("access_token"))
check("mauvais code MFA -> 401", login("admin", PWD["admin"], "000000").status_code == 401)
con = sqlite3.connect(f"file:{engine.url.database}?mode=ro", uri=True)
secret = con.execute("SELECT mfa_secret FROM utilisateurs WHERE identifiant='admin'").fetchone()[0]
con.close()
r = login("admin", PWD["admin"], pyotp.TOTP(secret).now())
check("bon code MFA -> jeton délivré", r.status_code == 200 and bool(r.json().get("access_token")))
h = {"Authorization": f"Bearer {r.json().get('access_token', '')}"}
jr = requests.get(f"{API}/admin/journal-audit", headers=h, timeout=10)
check("journal d'audit accessible -> 200", jr.status_code == 200)
actions = {j["action"] for j in jr.json()} if jr.status_code == 200 else set()
for a in ("CONNEXION_ECHEC", "MFA_ECHEC", "CONNEXION_REUSSIE", "ACCES_REFUSE", "SIMULATION_RESET"):
    check(f"journal contient {a}", a in actions)

print("5) Anti force brute (compte inexistant, pour ne bloquer aucun vrai compte)")
statuts = [login("verif_lockout", "mauvais").status_code for _ in range(7)]
check("blocage 429 après plusieurs échecs", 429 in statuts, f"({statuts})")

print("\nRESULTAT :", "TOUT EST OK" if ok_all else "DES VERIFICATIONS ONT ECHOUE")
sys.exit(0 if ok_all else 1)
