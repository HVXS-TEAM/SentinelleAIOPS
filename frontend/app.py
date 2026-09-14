"""
app.py — Point d'entrée Sentinelle AIOps
Écran de connexion : palette dédiée via login.css (teal néon #00F2C3,
glasmorphism). NE PAS importer components.py / theme.css ici.
"""
# Masquage du déploiement natif Streamlit + correctifs layout login
_HIDE_STREAMLIT_UI = """
<style>
/* Masque bouton Deploy et menu hamburger Streamlit */
#MainMenu {visibility: hidden;}
header[data-testid="stHeader"] .stDeployButton {display: none;}
[data-testid="stToolbar"] {display: none;}

/* Correctifs layout page de connexion */
/* Force la taille du logo à 128×128 */
div[class*="st-key-login-card"] .login-logo-wrap img {
    width: 128px !important;
    height: 128px !important;
    object-fit: contain;
}
/* Bouton Se connecter pleine largeur */
div[class*="st-key-login-card"] [data-testid="stBaseButton-secondary"],
div[class*="st-key-login-card"] [data-testid="stBaseButton-primary"],
div[class*="st-key-login-card"] .stButton,
div[class*="st-key-login-card"] .stButton > button {
    width: 100% !important;
    display: block;
}
</style>
"""


import os
import sys
from pathlib import Path

import requests
import streamlit as st

# ── Chemin absolu du logo ───────────────────────────────────────────────────
LOGO_PATH = Path(__file__).parent / "static" / "logo.png"

# ── Configuration Streamlit ─────────────────────────────────────────────────
st.set_page_config(
    page_title="Connexion à Sentinelle AIOps",
    page_icon=str(LOGO_PATH) if LOGO_PATH.exists() else "🛡️",
    layout="centered",
    initial_sidebar_state="collapsed",
)

from components import load_login_theme

# ── Injection automatique du thème de connexion (mode clair/sombre horaire) ──
load_login_theme()

# ── Initialisation de la session ────────────────────────────────────────────
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False
if "username" not in st.session_state:
    st.session_state.username = ""
if "role" not in st.session_state:
    st.session_state.role = ""
if "token" not in st.session_state:
    st.session_state.token = ""

# ── Comptes démo (fallback sans backend) ────────────────────────────────────
DEMO_ACCOUNTS = {
    "admin":       {"password": "AdminPass2026!", "role": "Administrateur"},
    "admin_aiops": {"password": "AdminPass2026!", "role": "Administrateur"},
    "tech":        {"password": "TechPass2026!",  "role": "Technicien"},
    "visiteur":    {"password": "VisitorPass2026!", "role": "Visiteur"},
}

# Mapping profil → identifiant démo par défaut
PROFILE_TO_USERNAME = {
    "Administrateur": "admin",
    "Technicien":     "tech",
    "Visiteur":       "visiteur",
}

# ── Chemin absolu du logo ───────────────────────────────────────────────────
LOGO_PATH = Path(__file__).parent / "static" / "sentinelle_logo.png"

# ══════════════════════════════════════════════════════════════════════════════
# ÉCRAN DE CONNEXION
# ══════════════════════════════════════════════════════════════════════════════
if not st.session_state.authenticated:

    # Masquer le menu natif Streamlit
    st.markdown(_HIDE_STREAMLIT_UI, unsafe_allow_html=True)

    with st.container(key="login-card"):

        # ── Logo centré : encodage base64 → balise img dans le HTML ─────────
        import base64
        _logo_b64 = base64.b64encode(LOGO_PATH.read_bytes()).decode()
        st.markdown(
            f'<div class="login-logo-wrap">'
            f'<img src="data:image/png;base64,{_logo_b64}" alt="Sentinelle AIOps">'
            f'</div>',
            unsafe_allow_html=True,
        )

        # ── Titre + Sous-titre ─────────────────────────────────────────────
        st.markdown(
            """
            <div class="login-title">Connexion à Sentinelle</div>
            <div class="login-subtitle">Accédez à votre centre de commande AIOps</div>
            """,
            unsafe_allow_html=True,
        )


        # ── Champ PROFILS ──────────────────────────────────────────────────
        profil = st.selectbox(
            "PROFILS",
            ["Administrateur", "Technicien", "Visiteur"],
            key="login_profil",
        )

        # ── Champ IDENTIFIANT ──────────────────────────────────────────────
        identifiant = st.text_input(
            "IDENTIFIANT",
            placeholder="admin_aiops",
            value=PROFILE_TO_USERNAME.get(profil, ""),
            key="login_identifiant",
        )

        # ── Lien "Oublié ?" + champ MOT DE PASSE ──────────────────────────
        st.markdown(
            '<a class="login-forgot" href="#">Oublié ?</a>',
            unsafe_allow_html=True,
        )
        mot_de_passe = st.text_input(
            "MOT DE PASSE",
            type="password",
            placeholder="••••••••",
            key="login_password",
        )

        # ── Bouton Se connecter ────────────────────────────────────────────
        if st.button("Se connecter →", key="login_submit", use_container_width=True):
            authenticated = False

            # Tentative API (backend FastAPI)
            try:
                res = requests.post(
                    "http://localhost:8000/api/v1/auth/login",
                    data={"username": identifiant, "password": mot_de_passe},
                    timeout=2,
                )
                if res.status_code == 200:
                    data = res.json()
                    st.session_state.authenticated = True
                    st.session_state.username = identifiant
                    st.session_state.role = data.get("role", profil)
                    st.session_state.token = data.get("access_token", "")
                    authenticated = True
            except Exception:
                pass  # Backend absent → fallback démo

            # Fallback comptes démo
            if not authenticated:
                account = DEMO_ACCOUNTS.get(identifiant)
                if account and account["password"] == mot_de_passe:
                    st.session_state.authenticated = True
                    st.session_state.username = identifiant
                    st.session_state.role = account["role"]
                    authenticated = True
                elif not authenticated:
                    st.error("Identifiants incorrects. Vérifiez votre profil, identifiant et mot de passe.")

            if authenticated:
                st.rerun()

        # ── Séparateur + Pilule "Système Opérationnel" ────────────────────
        st.markdown('<hr class="login-divider">', unsafe_allow_html=True)
        st.markdown(
            '<div style="text-align:center;">'
            '<span class="login-status-pill">'
            '<span class="login-status-dot"></span> Système Opérationnel'
            '</span></div>',
            unsafe_allow_html=True,
        )

# ══════════════════════════════════════════════════════════════════════════════
# REDIRECTION APRÈS AUTHENTIFICATION → Dashboard
# ══════════════════════════════════════════════════════════════════════════════
else:
    # L'utilisateur est authentifié : on le redirige immédiatement vers le
    # Dashboard. st.switch_page() charge la page cible avec sa propre
    # st.set_page_config() (layout="wide", sidebar ouverte) — c'est la seule
    # façon d'avoir simultanément la page de connexion en layout="centered"
    # et les pages applicatives en layout="wide".
    st.switch_page("pages/1_Dashboard.py")
