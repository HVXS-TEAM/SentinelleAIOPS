"""
Vérification live de l'étape 1 (le back-end doit tourner sur http://localhost:8000).
Usage :  python verif_etape1.py        (dure ~75 s : il attend un cycle de recalcul de santé)
"""
import os
import sys
import time

import requests

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


def sante():
    return {e["nom"]: e["health_score"] for e in S.get(f"{API}/inventory/equipements", timeout=5).json()}


def alertes_actives():
    return S.get(f"{API}/admin/alertes", params={"statut": "active"}, timeout=5).json()


print("1) Etat de départ (attente du premier cycle du scheduler si nécessaire)")
S.post(f"{API}/simulation/reset", timeout=10)
for _ in range(20):                                   # jusqu'à ~50 s
    if len(alertes_actives()) < 50:
        break
    time.sleep(2.5)
for eq in S.get(f"{API}/inventory/equipements", timeout=5).json():
    S.post(f"{API}/inventory/recalculate-health/{eq['id']}", timeout=5)   # baseline à jour
base, act0 = sante(), alertes_actives()
print("   santé:", base)
check("alertes actives raisonnables (< 50)", len(act0) < 50, f"({len(act0)})")

print("2) Injection des 3 scénarios")
r1 = S.post(f"{API}/simulation/inject-bruteforce", timeout=15).json()
r2 = S.post(f"{API}/simulation/stress-disk", timeout=15).json()
r3 = S.post(f"{API}/simulation/cis-flaw", timeout=15).json()
check("bruteforce : SSH_BRUTEFORCE critique détecté",
      any(e["type"] == "SSH_BRUTEFORCE" and e["severite"] == "critique" for e in r1["evenements_detectes"]))
check("stress-disk : TTF < 24 h", (r2["ttf_estime_heures"] or 99) < 24, f"({r2['ttf_estime_heures']})")
check("cis-flaw : 3 non-conformités", len(r3["non_conformites"]) == 3)
imm = sante()
check("santé SRV-AUTH-01 baisse immédiatement", imm["SRV-AUTH-01"] < base["SRV-AUTH-01"], f"({base['SRV-AUTH-01']} -> {imm['SRV-AUTH-01']})")
check("santé SRV-APP-01 baisse immédiatement", imm["SRV-APP-01"] < base["SRV-APP-01"], f"({base['SRV-APP-01']} -> {imm['SRV-APP-01']})")

print("3) Attente d'un cycle scheduler (65 s) : les pénalités doivent SURVIVRE")
time.sleep(65)
apres = sante()
check("SRV-AUTH-01 toujours pénalisé", apres["SRV-AUTH-01"] < base["SRV-AUTH-01"], f"({apres['SRV-AUTH-01']})")
check("SRV-APP-01 toujours pénalisé", apres["SRV-APP-01"] < base["SRV-APP-01"], f"({apres['SRV-APP-01']})")
disk = [a for a in alertes_actives() if "disk_percent sur SRV-APP-01" in a["message"]]
check("une seule alerte disque active sur SRV-APP-01", len(disk) == 1, f"({len(disk)})")

print("4) Pas d'inflation d'alertes (attente 35 s = 1 cycle TTF)")
n_avant = len(alertes_actives())
time.sleep(35)
n_apres = len(alertes_actives())
check("le nombre d'alertes actives n'augmente pas", n_apres <= n_avant, f"({n_avant} -> {n_apres})")

print("5) Reset")
rr = S.post(f"{API}/simulation/reset", timeout=10).json()
final = sante()
check("scores restaurés", final["SRV-AUTH-01"] >= apres["SRV-AUTH-01"] and final["SRV-APP-01"] >= apres["SRV-APP-01"], f"({final})")
check("plus d'alerte disque SRV-APP-01",
      not [a for a in alertes_actives() if "disk_percent sur SRV-APP-01" in a["message"]])

print("\nRESULTAT :", "TOUT EST OK" if ok_all else "DES VERIFICATIONS ONT ECHOUE")
sys.exit(0 if ok_all else 1)
