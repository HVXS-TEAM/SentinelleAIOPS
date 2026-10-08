"""
Vérification de la page Supervision (étape 5) : carte de prédiction critique, seuils, projections
de télémétrie, urgence maintenance — tout sur des données réelles du back-end.
Le back-end doit tourner sur http://localhost:8000.

Usage (depuis "Sentinelle AIOPS/frontend/", même venv que Streamlit) :
    python verif_etape5_supervision.py
"""
import os
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
PWD = os.environ.get("SENTINELLE_PASSWORD", "TechPass2026!")
USER = os.environ.get("SENTINELLE_USER", "tech")
ok_all = True


def check(label, cond, detail=""):
    global ok_all
    ok_all &= bool(cond)
    print(f"  [{'OK' if cond else 'ECHEC'}] {label} {detail}")


def token():
    r = requests.post(f"{API}/auth/login", data={"username": USER, "password": PWD}, timeout=10)
    if r.status_code != 200 or not r.json().get("access_token"):
        print(f"Connexion impossible ({r.status_code}). Utilise un compte sans MFA (SENTINELLE_USER/SENTINELLE_PASSWORD).")
        sys.exit(2)
    return r.json()["access_token"]


def open_page(token_value="__auto__"):
    at = AppTest.from_file(str(ROOT / "app.py"), default_timeout=40)
    at.session_state["authenticated"] = True
    at.session_state["username"] = USER
    at.session_state["role"] = "Technicien"
    at.session_state["token"] = token() if token_value == "__auto__" else token_value
    # Coupe le tick d'auto-refresh : en AppTest, le timer du fragment empêcherait
    # sinon run() de se terminer (ancien st_autorefresh ne posait pas ce problème
    # en environnement de test).
    at.session_state["demo_autorefresh_paused"] = True
    at.switch_page("pages/3_Supervision.py")
    at.run()
    return at


def html_of(at):
    # Lit directement le champ "body" du proto st.html plutôt que .value : certaines versions
    # de streamlit.testing n'implémentent pas le repli value -> body pour les éléments non
    # spécialisés (dont st.html fait partie), ce qui lève AttributeError sur .value.
    return "\n".join(getattr(h.proto, "body", "") for h in at.get("html"))


h = {"Authorization": f"Bearer {token()}"}

print("1) État nominal (après reset)")
requests.post(f"{API}/simulation/reset", headers=h, timeout=15)
time.sleep(1)
at = open_page()
check("aucune exception", not at.exception, str([e.value for e in at.exception][:1]))
text = html_of(at)
check("carte « aucune saturation critique prévue » affichée", "Aucune saturation critique prévue" in text)
check("pas de carte critique en l'absence de prédiction", "PRÉDICTION CRITIQUE IMMINENTE" not in text)
check("liste d'urgence vide affichée proprement", "Aucune maintenance urgente" in text)

print("2) Après injection stress-disk (SRV-APP-01)")
r = requests.post(f"{API}/simulation/stress-disk", headers=h, timeout=15).json()
time.sleep(5)  # laisse passer le cache de lecture (ttl=4 s) de l'api_client
at = open_page()
check("aucune exception", not at.exception, str([e.value for e in at.exception][:1]))
text = html_of(at)
check("carte critique affichée pour SRV-APP-01", "PRÉDICTION CRITIQUE IMMINENTE" in text and "SRV-APP-01" in text)
check("SRV-APP-01 dans la liste « Urgence Maintenance »", "SRV-APP-01" in text and "CRITIQUE" in text)
check("sélecteur d'équipement présent", len(at.selectbox) >= 1)
check("au moins un graphique de tendance rendu", "<polyline" in text)

print("3) Changement d'équipement dans le sélecteur")
# AppTest expose des libellés formatés (format_func) dans .options : on sélectionne donc
# par la VRAIE valeur (l'id d'équipement, connu via l'API), pas par le libellé affiché.
eq_ids = [e["id"] for e in requests.get(f"{API}/inventory/equipements", headers=h, timeout=10).json()]
sb = at.selectbox(key="sup_selected_eq")
autres_ids = [i for i in eq_ids if i != sb.value]
if autres_ids:
    sb.set_value(autres_ids[0])
    at.run()
    check("pas d'exception après changement de sélection", not at.exception)
else:
    print("  (un seul équipement en base : test de sélection ignoré)")

print("4) Back-end injoignable")
with mock.patch("requests.get", side_effect=requests.exceptions.ConnectionError("down")), \
     mock.patch("requests.post", side_effect=requests.exceptions.ConnectionError("down")):
    at2 = open_page(token_value="jeton-hors-ligne")
check("aucune exception en mode hors-ligne", not at2.exception, str([e.value for e in at2.exception][:1]))
check("bandeau d'avertissement affiché", len(at2.warning) >= 1)

print("5) Reset final")
requests.post(f"{API}/simulation/reset", headers=h, timeout=15)

print("\nRESULTAT :", "TOUT EST OK" if ok_all else "DES VERIFICATIONS ONT ECHOUE")
sys.exit(0 if ok_all else 1)
