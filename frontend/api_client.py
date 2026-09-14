"""
api_client.py — Client HTTP centralisé pour Sentinelle AIOps (Phase 3).

Toutes les pages Streamlit doivent passer par ce module pour parler au
back-end FastAPI, plutôt que d'appeler `requests` directement. Objectifs :
    - une seule base URL / un seul timeout à régler ;
    - gestion uniforme du "mode hors-ligne" : si l'API ne répond pas,
      chaque fonction retourne une valeur par défaut sûre (liste vide,
      dict vide, None) plutôt que de laisser Streamlit planter avec une
      exception non gérée ;
    - un indicateur `api_is_online()` que les pages peuvent utiliser pour
      afficher un bandeau d'avertissement clair au lieu d'un écran de
      crash rouge (cf. Phase_3.md §3.4).

Toutes les fonctions de lecture (get_*) sont décorées avec
st.cache_data(ttl=4) : assez court pour rester "temps réel" avec
l'auto-refresh de 5s, mais suffisant pour éviter de spammer l'API si
plusieurs composants d'une même page demandent la même donnée.
"""

from typing import Any, Optional

import requests
import streamlit as st

API_BASE_URL = "http://localhost:8000/api/v1"
_TIMEOUT = 3  # secondes — court pour ne jamais geler l'UI si l'API est down


def _headers() -> dict:
    token = st.session_state.get("token", "")
    return {"Authorization": f"Bearer {token}"} if token else {}


def _get(path: str, params: Optional[dict] = None) -> Any:
    """GET générique. Retourne None en cas d'échec (API down, timeout, erreur HTTP)."""
    try:
        res = requests.get(f"{API_BASE_URL}{path}", params=params, headers=_headers(), timeout=_TIMEOUT)
        if res.status_code == 200:
            return res.json()
        return None
    except requests.exceptions.RequestException:
        return None


def _post(path: str, json_body: Optional[dict] = None) -> Any:
    """POST générique. Retourne None en cas d'échec (API down, timeout, erreur HTTP)."""
    try:
        res = requests.post(f"{API_BASE_URL}{path}", json=json_body, headers=_headers(), timeout=_TIMEOUT)
        if res.status_code == 200:
            return res.json()
        return None
    except requests.exceptions.RequestException:
        return None


def api_is_online() -> bool:
    """Sonde légère pour savoir si l'API répond, à afficher en bandeau d'avertissement."""
    try:
        res = requests.get(f"{API_BASE_URL.rsplit('/api', 1)[0]}/", timeout=_TIMEOUT)
        return res.status_code == 200
    except requests.exceptions.RequestException:
        return False


# --- Parc / Inventaire -------------------------------------------------------

@st.cache_data(ttl=4)
def get_equipements() -> list[dict]:
    return _get("/inventory/equipements") or []


@st.cache_data(ttl=4)
def get_equipement(equipement_id: int) -> Optional[dict]:
    return _get(f"/inventory/equipements/{equipement_id}")


# --- Supervision --------------------------------------------------------------

@st.cache_data(ttl=4)
def get_metrics(equipement_id: Optional[int] = None, type_metrique: Optional[str] = None, limit: int = 100) -> list[dict]:
    params = {"limit": limit}
    if equipement_id is not None:
        params["equipement_id"] = equipement_id
    if type_metrique is not None:
        params["type_metrique"] = type_metrique
    return _get("/supervision/metrics", params=params) or []


@st.cache_data(ttl=4)
def get_predictions() -> list[dict]:
    return _get("/supervision/predictions") or []


# --- Sécurité -------------------------------------------------------------------

@st.cache_data(ttl=4)
def get_security_events(limit: int = 50) -> list[dict]:
    return _get("/securite/events", params={"limit": limit}) or []


# --- NetDevOps ------------------------------------------------------------------

@st.cache_data(ttl=4)
def get_audits(equipement_id: Optional[int] = None) -> list[dict]:
    params = {"equipement_id": equipement_id} if equipement_id is not None else None
    return _get("/netdevops/audits", params=params) or []


@st.cache_data(ttl=4)
def get_backups(equipement_id: int) -> list[dict]:
    return _get(f"/netdevops/backups/{equipement_id}") or []


# --- Administration / Reporting --------------------------------------------------

@st.cache_data(ttl=4)
def get_alertes(statut: Optional[str] = None) -> list[dict]:
    params = {"statut": statut} if statut else None
    return _get("/admin/alertes", params=params) or []


def acquitter_alerte(alerte_id: int) -> bool:
    """Acquitte une alerte. Retourne True si l'opération a réussi. N'utilise pas le cache (écriture)."""
    result = _post(f"/admin/alertes/{alerte_id}/acquitter")
    return result is not None


@st.cache_data(ttl=4)
def get_journal_audit(limit: int = 100) -> list[dict]:
    return _get("/admin/journal-audit", params={"limit": limit}) or []


def generate_pdf_report() -> Optional[bytes]:
    """Télécharge le rapport PDF généré côté back-end. Retourne les octets bruts, ou None si échec."""
    try:
        res = requests.get(f"{API_BASE_URL}/admin/generate-pdf-report", headers=_headers(), timeout=10)
        if res.status_code == 200:
            return res.content
        return None
    except requests.exceptions.RequestException:
        return None


# --- Assistant IA -----------------------------------------------------------------

def query_assistant(question: str) -> Optional[dict]:
    """Interroge l'assistant IA (lecture seule). Pas de cache : chaque question est unique."""
    return _post("/assistant/query", json_body={"question": question})


# --- Simulation Démo (Phase 2) -----------------------------------------------------
# Ces appels ne sont jamais mis en cache (ce sont des écritures qui doivent
# systématiquement atteindre l'API) et invalident le cache de lecture pour
# que les pages reflètent immédiatement le nouvel état.

def _clear_read_cache() -> None:
    get_equipements.clear()
    get_equipement.clear()
    get_metrics.clear()
    get_predictions.clear()
    get_security_events.clear()
    get_audits.clear()
    get_backups.clear()
    get_alertes.clear()
    get_journal_audit.clear()


def simulate_inject_bruteforce() -> Optional[dict]:
    result = _post("/simulation/inject-bruteforce")
    _clear_read_cache()
    return result


def simulate_stress_disk() -> Optional[dict]:
    result = _post("/simulation/stress-disk")
    _clear_read_cache()
    return result


def simulate_cis_flaw() -> Optional[dict]:
    result = _post("/simulation/cis-flaw")
    _clear_read_cache()
    return result


def simulate_reset() -> Optional[dict]:
    result = _post("/simulation/reset")
    _clear_read_cache()
    return result
