"""
login_page_example.py — squelette de l'écran de connexion.

À adapter dans le vrai point d'entrée de l'app (probablement Home.py /
app.py, exécuté avant que l'utilisateur accède aux pages du dossier
pages/). Utilise login.css (palette dédiée, distincte de theme.css) et
n'utilise PAS sidebar_nav()/top_header()/card() de components.py — cet
écran n'a pas de sidebar.
"""

from pathlib import Path
import streamlit as st

st.set_page_config(page_title="Connexion à Sentinelle AIOps", layout="centered")

LOGIN_CSS_PATH = Path(__file__).parent / "login.css"
st.markdown(f"<style>{LOGIN_CSS_PATH.read_text(encoding='utf-8')}</style>", unsafe_allow_html=True)

with st.container(key="login-card"):
    st.markdown(
        """
        <div class="login-logo-wrap">
            <!-- Remplacer par le vrai logo Sentinelle (fichier image du projet) -->
            <img src="app/static/logo.png" alt="Sentinelle AIOps">
        </div>
        <div class="login-title">Connexion à Sentinelle</div>
        <div class="login-subtitle">Accédez à votre centre de commande AIOps</div>
        """,
        unsafe_allow_html=True,
    )

    profil = st.selectbox(
        "👤 Profils",
        ["Administrateur", "Technicien", "Visiteur"],
        key="login_profil",
    )

    identifiant = st.text_input(
        "👤 Identifiant",
        placeholder="admin_aiops",
        key="login_identifiant",
    )

    st.markdown('<a class="login-forgot" href="#">Oublié ?</a>', unsafe_allow_html=True)
    mot_de_passe = st.text_input(
        "🔒 Mot de passe",
        type="password",
        placeholder="••••••••",
        key="login_password",
    )

    if st.button("Se connecter →", key="login_submit"):
        # TODO Antigravity : brancher ici la vraie logique d'authentification
        # (vérification identifiant/mot de passe, gestion de session,
        # redirection vers pages/1_Dashboard.py selon le rôle du profil)
        st.info("Authentification à implémenter.")

    st.markdown('<hr class="login-divider">', unsafe_allow_html=True)
    st.markdown(
        '<div style="text-align:center;">'
        '<span class="login-status-pill">'
        '<span class="login-status-dot"></span> Système Opérationnel'
        '</span></div>',
        unsafe_allow_html=True,
    )
