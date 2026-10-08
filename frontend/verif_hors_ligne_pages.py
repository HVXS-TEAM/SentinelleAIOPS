"""Recette étape 3 — mode hors-ligne (API coupée) sur les 7 pages.

Charge chaque page via AppTest avec `requests` neutralisé (ConnectionError)
et vérifie qu'aucune n'affiche un écran rouge : pas d'exception non gérée, et
présence du bandeau d'avertissement « Backend indisponible ».

Le back-end peut tourner ou non : toutes les requêtes réseau sont interceptées.

Usage (depuis "Sentinelle AIOPS/frontend/", même venv que Streamlit) :
    python verif_hors_ligne_pages.py
"""
import os
import sys
from pathlib import Path
from unittest import mock

import requests

ROOT = Path(__file__).resolve().parent
os.chdir(ROOT)
sys.path.insert(0, str(ROOT))
from streamlit.testing.v1 import AppTest  # noqa: E402

PAGES = [
    "pages/1_Dashboard.py",
    "pages/2_Sécurité.py",
    "pages/3_Supervision.py",
    "pages/4_NetDevOps.py",
    "pages/5_Parc_Informatique.py",
    "pages/6_Reporting_&_Admin.py",
    "pages/7_Assistant_IA.py",
]
ok_all = True


def check(label, cond, detail=""):
    global ok_all
    ok_all &= bool(cond)
    print(f"  [{'OK' if cond else 'ECHEC'}] {label} {detail}")


def open_offline(page: str) -> AppTest:
    at = AppTest.from_file(str(ROOT / "app.py"), default_timeout=60)
    at.session_state["authenticated"] = True
    at.session_state["username"] = "tech"
    at.session_state["role"] = "Technicien"
    at.session_state["token"] = "jeton-hors-ligne"
    at.session_state["demo_autorefresh_paused"] = True
    at.switch_page(page)
    with mock.patch("requests.get", side_effect=requests.exceptions.ConnectionError("down")), \
         mock.patch("requests.post", side_effect=requests.exceptions.ConnectionError("down")):
        at.run()
    return at


print("Mode hors-ligne (API injoignable) — une page à la fois")
for page in PAGES:
    at = open_offline(page)
    exceptions = [str(e.value)[:160] for e in at.exception]
    check(f"{os.path.basename(page)} : aucune exception", not exceptions, exceptions[:1])
    check(f"{os.path.basename(page)} : bandeau d'avertissement", len(at.warning) >= 1)

print("\nRESULTAT :", "TOUT EST OK" if ok_all else "DES VERIFICATIONS ONT ECHOUE")
sys.exit(0 if ok_all else 1)
