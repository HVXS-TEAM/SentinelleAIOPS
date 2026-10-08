"""
page_template.py — Socle de démarrage unifié pour l'ensemble des pages de Sentinelle AIOps.
"""
from pathlib import Path
import os
import sys
import time

import streamlit as st
from components import load_theme, sidebar_nav, top_header
import api_client as api

# ── Auto-refresh natif (Streamlit ≥ 1.37, cf. décision D1) ────────────────────
# Remplace l'ancien composant tiers abandonné (dernière release : juin 2023), qui
# relançait toute la page toutes les 5 s. L'équivalent natif est un fragment armé
# avec `run_every` qui demande un rerun complet à chaque tick (doc officielle :
# « To trigger an app rerun from inside a fragment, call st.rerun() directly »).
# Garde anti-boucle : le corps d'un fragment s'exécute AUSSI à chaque run complet,
# donc un `st.rerun()` inconditionnel bouclerait à l'infini sans attendre le tick.
# On n'ordonne le rerun que si ≥ 5 s se sont écoulées depuis le précédent.
# (`run_every` dynamique au décorateur est impossible ici : page_template est un
# module importé une seule fois, son décorateur ne se réévalue pas à chaque run —
# d'où la garde temporelle explicite, robuste dans le navigateur comme sous test.)
# Pause soutenance : quand le fragment n'est plus rendu, Streamlit annule son timer ;
# le bouton pause du panneau démo force un rerun qui (dés)arme le tick.
# Tests AppTest : fragment désarmé (détection `streamlit.testing` ou
# `SENTINELLE_NO_AUTOREFRESH=1`) pour laisser les scripts de vérification se terminer.
_AUTO_REFRESH_SECONDS = 5
_LAST_TICK_KEY = "_sentinelle_last_auto_refresh"


def _under_test() -> bool:
    """Vrai sous AppTest (scripts verif_*) : pas d'auto-refresh."""
    if os.environ.get("SENTINELLE_NO_AUTOREFRESH") == "1":
        return True
    return any(k == "streamlit.testing" or k.startswith("streamlit.testing.") for k in sys.modules)


@st.fragment(run_every=_AUTO_REFRESH_SECONDS)
def _auto_refresh_tick() -> None:
    """Tick : ordonne un rerun complet uniquement si l'intervalle est écoulé."""
    if _under_test():
        return
    now = time.monotonic()
    last = st.session_state.get(_LAST_TICK_KEY)
    if last is None:
        st.session_state[_LAST_TICK_KEY] = now
        return
    if now - last >= _AUTO_REFRESH_SECONDS:
        st.session_state[_LAST_TICK_KEY] = now
        st.rerun()

_LOGO_PATH = Path(__file__).parent / "static" / "logo.png"
_DEFAULT_ICON = str(_LOGO_PATH) if _LOGO_PATH.exists() else "🛡️"


def _demo_panel_impl() -> None:
    """
    Panneau de contrôle démo BTS en 1-clic (cf. Phase_3.md §3.3), affiché
    dans la sidebar sur TOUTES les pages puisque appelé depuis
    page_bootstrap(). Chaque bouton déclenche un endpoint
    /api/v1/simulation/* via api_client et affiche un toast de
    confirmation, puis force un rerun pour que les pages affichent
    immédiatement les nouvelles données (plutôt que d'attendre le
    prochain cycle d'auto-refresh).
    """
    with st.sidebar:
        with st.expander("🎯 Démonstration BTS (1-Clic)", expanded=False):

            if st.button("🔴 Injecter Brute-force SSH", key="demo_btn_bruteforce", width="stretch"):
                result = api.simulate_inject_bruteforce()
                if result:
                    st.toast("🚨 Attaque simulée sur 198.51.100.45 !")
                else:
                    st.toast("⚠️ Échec de l'appel API (backend indisponible ?)")
                st.rerun()

            if st.button("🟡 Simuler Saturation Disque", key="demo_btn_stressdisk", width="stretch"):
                result = api.simulate_stress_disk()
                if result:
                    st.toast("⚠️ Stress disque déclenché sur SRV-APP-01 !")
                else:
                    st.toast("⚠️ Échec de l'appel API (backend indisponible ?)")
                st.rerun()

            if st.button("🔵 Injecter Faille CIS Cisco", key="demo_btn_cisflaw", width="stretch"):
                result = api.simulate_cis_flaw()
                if result:
                    nb = len(result.get("non_conformites", []))
                    st.toast(f"🛡️ {nb} faille(s) CIS détectée(s) sur SW-CORE-01 !")
                else:
                    st.toast("⚠️ Échec de l'appel API (backend indisponible ?)")
                st.rerun()

            if st.button("🟢 Réinitialiser Démo (Reset)", key="demo_btn_reset", width="stretch"):
                result = api.simulate_reset()
                if result:
                    st.toast("✅ Démo réinitialisée à l'état nominal !")
                else:
                    st.toast("⚠️ Échec de l'appel API (backend indisponible ?)")
                st.rerun()

            st.markdown("---")
            paused = st.session_state.get("demo_autorefresh_paused", False)
            label = "▶️ Reprendre l'auto-refresh" if paused else "⏸ Mettre en pause l'auto-refresh"
            if st.button(label, key="demo_btn_pause_refresh", width="stretch"):
                st.session_state.demo_autorefresh_paused = not paused
                st.rerun()

        if not api.api_is_online():
            st.warning("⚠️ Backend indisponible — données non actualisées.", icon="⚠️")


def _demo_panel() -> None:
    """[etape3] Le panneau de démonstration est réservé aux rôles Technicien et Administrateur."""
    if st.session_state.get("role", "") in ("Administrateur", "Technicien"):
        _demo_panel_impl()
    elif not api.api_is_online():
        st.sidebar.warning("⚠️ Backend indisponible — données non actualisées.", icon="⚠️")


def _enforce_session() -> None:
    """[etape3] Jeton expiré (401 reçu de l'API) : retour à l'écran de connexion."""
    if st.session_state.get("session_expired", False):
        for key in ("authenticated", "token", "role", "username", "mfa_pending", "session_expired"):
            st.session_state.pop(key, None)
        st.session_state["login_notice"] = "Session expirée : reconnectez-vous."
        st.switch_page("app.py")


def page_bootstrap(
    active: str = "Dashboard",
    page_title: str = "Sentinelle AIOps",
    search_placeholder: str = "Rechercher...",
    header_title: str | None = None,
    page_icon: str | Path | None = None
):
    """
    Initialise la configuration Streamlit, le thème CSS et le layout commun (sidebar + top header).
    À appeler impérativement tout en haut de chaque page.
    """
    if page_icon is None:
        page_icon = _DEFAULT_ICON

    try:
        st.set_page_config(
            page_title=f"{page_title} — Sentinelle AIOps",
            page_icon=page_icon,
            layout="wide",
            initial_sidebar_state="expanded"
        )
    except Exception:
        pass
    _enforce_session()
    load_theme()
    sidebar_nav(active=active)
    _demo_panel()

    # Auto-refresh discret (5s) — cf. Phase_3.md §3.4. Suspendu si l'utilisateur
    # a cliqué sur pause, pour figer l'écran pendant les explications au jury.
    # Note AppTest : les scripts de vérification positionnent eux-mêmes
    # demo_autorefresh_paused=True, car le timer du fragment empêcherait sinon
    # `at.run()` de se terminer (l'ancien st_autorefresh ne posait pas ce
    # problème en environnement de test).
    if not st.session_state.get("demo_autorefresh_paused", False):
        _auto_refresh_tick()

    top_header(search_placeholder=search_placeholder, page_title=header_title)
