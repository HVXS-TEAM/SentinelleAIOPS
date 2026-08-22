import streamlit as st
import requests
import os
import sys

# Add parent dir to path
sys.path.append(os.path.abspath(os.path.dirname(__file__)))

from components import load_theme, badge, mono
from page_template import page_bootstrap

st.set_page_config(
    page_title="Connexion — Sentinelle AIOps",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="collapsed"
)

load_theme()

# Session State Initialization
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False
if "username" not in st.session_state:
    st.session_state.username = ""
if "role" not in st.session_state:
    st.session_state.role = ""
if "token" not in st.session_state:
    st.session_state.token = ""

if not st.session_state.authenticated:
    st.title("🔐 Connexion à Sentinelle AIOps")
    st.markdown("Plateforme unifiée d'administration système, supervision prédictive et cybersécurité par IA.")

    col1, col2 = st.columns([1, 1])
    with col1:
        with st.form("login_form"):
            username = st.text_input("Identifiant", value="admin")
            password = st.text_input("Mot de passe", type="password", value="AdminPass2026!")
            totp_code = st.text_input("Code MFA TOTP (Administrateur)", value="")
            submit = st.form_submit_button("Se connecter à la console")

            if submit:
                try:
                    res = requests.post(
                        "http://localhost:8000/api/v1/auth/login",
                        data={"username": username, "password": password},
                        params={"totp_code": totp_code} if totp_code else {},
                        timeout=3
                    )
                    if res.status_code == 200:
                        data = res.json()
                        st.session_state.authenticated = True
                        st.session_state.username = username
                        st.session_state.role = data.get("role", "Administrateur")
                        st.session_state.token = data.get("access_token", "")
                        st.success(f"Connexion réussie en tant que {st.session_state.username}")
                        st.rerun()
                    else:
                        st.error(res.json().get("detail", "Échec de l'authentification"))
                except Exception:
                    if (username == "admin" and password == "AdminPass2026!") or (username == "tech" and password == "TechPass2026!"):
                        st.session_state.authenticated = True
                        st.session_state.username = username
                        st.session_state.role = "Administrateur" if username == "admin" else "Technicien"
                        st.success(f"Connexion démonstration réussie ({st.session_state.role})")
                        st.rerun()
                    else:
                        st.error("Identifiants incorrects")

    with col2:
        st.markdown("""
        <div class="snt-card">
            <h3 style="color:var(--primary); margin-top:0;">🔑 Comptes Démo Pré-Configurés</h3>
            <ul style="line-height:1.8;">
                <li><b style="color:var(--secondary);">Administrateur :</b> <code>admin</code> / <code>AdminPass2026!</code> (MFA)</li>
                <li><b style="color:var(--secondary);">Technicien :</b> <code>tech</code> / <code>TechPass2026!</code></li>
                <li><b style="color:var(--secondary);">Visiteur :</b> <code>visiteur</code> / <code>VisitorPass2026!</code></li>
            </ul>
        </div>
        """, unsafe_allow_html=True)

else:
    page_bootstrap(active="Dashboard", page_title="Sentinelle AIOps Operational Command")
    st.markdown(f"Utilisateur connecté : {mono(st.session_state.username)} | Rôle : {badge(st.session_state.role, 'healthy')}", unsafe_allow_html=True)
    st.markdown("👈 Sélectionnez un module dans le menu latéral à gauche pour naviguer.")
