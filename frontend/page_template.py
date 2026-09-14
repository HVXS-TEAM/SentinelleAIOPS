"""
page_template.py — Socle de démarrage unifié pour l'ensemble des pages de Sentinelle AIOps.
"""
from pathlib import Path
import streamlit as st
from streamlit_autorefresh import st_autorefresh
from components import load_theme, sidebar_nav, top_header
import api_client as api

_LOGO_PATH = Path(__file__).parent / "static" / "logo.png"
_DEFAULT_ICON = str(_LOGO_PATH) if _LOGO_PATH.exists() else "🛡️"


def _demo_panel() -> None:
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

            if st.button("🔴 Injecter Brute-force SSH", key="demo_btn_bruteforce", use_container_width=True):
                result = api.simulate_inject_bruteforce()
                if result:
                    st.toast("🚨 Attaque simulée sur 198.51.100.45 !")
                else:
                    st.toast("⚠️ Échec de l'appel API (backend indisponible ?)")
                st.rerun()

            if st.button("🟡 Simuler Saturation Disque", key="demo_btn_stressdisk", use_container_width=True):
                result = api.simulate_stress_disk()
                if result:
                    st.toast("⚠️ Stress disque déclenché sur SRV-APP-01 !")
                else:
                    st.toast("⚠️ Échec de l'appel API (backend indisponible ?)")
                st.rerun()

            if st.button("🔵 Injecter Faille CIS Cisco", key="demo_btn_cisflaw", use_container_width=True):
                result = api.simulate_cis_flaw()
                if result:
                    nb = len(result.get("non_conformites", []))
                    st.toast(f"🛡️ {nb} faille(s) CIS détectée(s) sur SW-CORE-01 !")
                else:
                    st.toast("⚠️ Échec de l'appel API (backend indisponible ?)")
                st.rerun()

            if st.button("🟢 Réinitialiser Démo (Reset)", key="demo_btn_reset", use_container_width=True):
                result = api.simulate_reset()
                if result:
                    st.toast("✅ Démo réinitialisée à l'état nominal !")
                else:
                    st.toast("⚠️ Échec de l'appel API (backend indisponible ?)")
                st.rerun()

            st.markdown("---")
            paused = st.session_state.get("demo_autorefresh_paused", False)
            label = "▶️ Reprendre l'auto-refresh" if paused else "⏸ Mettre en pause l'auto-refresh"
            if st.button(label, key="demo_btn_pause_refresh", use_container_width=True):
                st.session_state.demo_autorefresh_paused = not paused
                st.rerun()

        if not api.api_is_online():
            st.warning("⚠️ Backend indisponible — données non actualisées.", icon="⚠️")


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
    load_theme()
    sidebar_nav(active=active)
    _demo_panel()

    # Auto-refresh discret (5s) — cf. Phase_3.md §3.4. Suspendu si l'utilisateur
    # a cliqué sur pause, pour figer l'écran pendant les explications au jury.
    if not st.session_state.get("demo_autorefresh_paused", False):
        st_autorefresh(interval=5000, key="sentinelle_datarefresh")

    top_header(search_placeholder=search_placeholder, page_title=header_title)
