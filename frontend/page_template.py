"""
page_template.py — Socle de démarrage unifié pour l'ensemble des pages de Sentinelle AIOps.
"""
import streamlit as st
from components import load_theme, sidebar_nav, top_header


def page_bootstrap(
    active: str = "Dashboard",
    page_title: str = "Sentinelle AIOps",
    search_placeholder: str = "Rechercher...",
    header_title: str | None = None,
    page_icon: str = "🛡️"
):
    """
    Initialise la configuration Streamlit, le thème CSS et le layout commun (sidebar + top header).
    À appeler impérativement tout en haut de chaque page.
    """
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
    top_header(search_placeholder=search_placeholder, page_title=header_title)

