"""
Vérification live de l'étape 2 (le back-end doit tourner sur http://localhost:8000, lancé depuis backend/).
Usage :  python verif_etape2.py      (dure environ 15 s)
A lancer APRÈS scripts/nettoyer_donnees.py --apply et un redémarrage du serveur.
"""
import os
import sqlite3
import sys
import time
from datetime import datetime, timedelta

import requests

sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))
from app.core.config import settings  # noqa: E402
from app.core.database import engine  # noqa: E402

API = "http://localhost:8000/api/v1"
ok_all = True

# --- Authentification (étape 3) : les routes sont protégées, on se connecte d'abord -------------------
# Par défaut : compte "tech" (sans MFA). Surchargeable : SENTINELLE_USER / SENTINELLE_PASSWORD.
S = requests.Session()
_login = S.post(
    f"{API}/auth/login",
    data={"username": os.environ.get("SENTINELLE_USER", "tech"),
          "password": os.environ.get("SENTINELLE_PASSWORD", "TechPass2026!")},
    timeout=10,
)
if _login.status_code != 200 or not _login.json().get("access_token"):
    print(f"Connexion impossible ({_login.status_code} : {_login.text[:120]}). "
          "Utilise un compte sans MFA (tech) ou définis SENTINELLE_USER / SENTINELLE_PASSWORD.")
    sys.exit(2)
S.headers["Authorization"] = f"Bearer {_login.json()['access_token']}"


def check(label, cond, detail=""):
    global ok_all
    ok_all &= bool(cond)
    print(f"  [{'OK' if cond else 'ECHEC'}] {label} {detail}")


if not settings.DATABASE_URL.startswith("sqlite"):
    print("Ce script lit directement la base SQLite ; DATABASE_URL n'est pas SQLite."); sys.exit(2)
db_path = engine.url.database
now = datetime.utcnow()


def scalar(sql, *params):
    con = sqlite3.connect(f"file:{db_path}?mode=ro", uri=True)
    try:
        return con.execute(sql, params).fetchone()[0]
    finally:
        con.close()


print("1) Serveur et télémétrie")
check("l'API répond", S.get("http://localhost:8000/", timeout=5).status_code == 200)
age = 9e9
for _ in range(9):                                   # le 1er tick de télémétrie arrive ~10 s après le démarrage
    last = scalar("SELECT max(horodatage) FROM metriques")
    age = (datetime.utcnow() - datetime.fromisoformat(last)).total_seconds() if last else 9e9
    if age < 30:
        break
    time.sleep(3)
check("la télémétrie arrive (dernier point < 30 s)", age < 30, f"({age:.0f} s)")

print("2) Rétention")
oldest = None
for _ in range(6):                                   # la purge tourne au démarrage : on laisse un peu de temps
    oldest = scalar("SELECT min(horodatage) FROM metriques")
    if oldest and datetime.fromisoformat(oldest) >= now - timedelta(hours=25):
        break
    time.sleep(3)
check("aucune métrique de plus de 25 h", oldest and datetime.fromisoformat(oldest) >= now - timedelta(hours=25), f"(plus ancienne : {oldest})")
n_met = scalar("SELECT count(*) FROM metriques")
check("volume de métriques borné (< 250 000)", n_met < 250_000, f"({n_met})")
cutoff = (now - timedelta(hours=25)).isoformat(sep=" ")
check("aucune prédiction de plus de 25 h", scalar("SELECT count(*) FROM predictions WHERE date_calcul < ?", cutoff) == 0)
check("aucune alerte résolue de plus de 25 h",
      scalar("SELECT count(*) FROM alertes WHERE statut='resolue' AND date_creation < ?", cutoff) == 0)

print("3) Etat du parc")
alertes = S.get(f"{API}/admin/alertes", params={"statut": "active"}, timeout=5).json()
check("alertes actives raisonnables (< 50)", len(alertes) < 50, f"({len(alertes)})")
for eq in S.get(f"{API}/inventory/equipements", timeout=5).json():
    S.post(f"{API}/inventory/recalculate-health/{eq['id']}", timeout=5)   # score à jour
sante = {e["nom"]: e["health_score"] for e in S.get(f"{API}/inventory/equipements", timeout=5).json()}
print("   santé:", sante)
check("aucun équipement à 0 (après nettoyage)", min(sante.values()) > 0)

print("\nRESULTAT :", "TOUT EST OK" if ok_all else "DES VERIFICATIONS ONT ECHOUE")
sys.exit(0 if ok_all else 1)
