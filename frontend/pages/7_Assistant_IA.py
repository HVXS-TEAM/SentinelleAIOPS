"""
7_Assistant_IA.py — Sentinelle AIOps
Pixel-perfect ref : Ecrans_Reference/Assistant_IA/code.html + screen.png
Sources : DESIGN.md (tokens) + code.html (DOM & layout) + screen.png (vérification visuelle)
"""
import os, sys
import streamlit as st

st.set_page_config(
    page_title="Assistant IA — Sentinelle AIOps",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded",
)

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from page_template import page_bootstrap

# ── Garde d'authentification ─────────────────────────────────────────────────
if not st.session_state.get("authenticated", False):
    st.switch_page("app.py")

page_bootstrap(
    active="Assistant IA",
    page_title="Assistant IA",
    search_placeholder="Rechercher entités, requêtes..."
)

# ── CSS DÉDIÉ AU MODULE ASSISTANT IA ─────────────────────────────────────────
st.markdown("""<style>
@keyframes pulse-op {
0% { opacity: 1; }
100% { opacity: 0.6; }
}
.pulse-critical { animation: pulse-op 0.5s infinite alternate; }

/* Conteneur global centré */
.chat-canvas {
max-width: 860px;
margin: 0 auto;
display: flex;
flex-direction: column;
gap: 24px;
padding: 10px 0 20px 0;
}

/* Bulle Utilisateur */
.user-msg-row {
display: flex;
justify-content: flex-end;
width: 100%;
}
.user-msg-bubble {
background-color: #323538;
border: 1px solid rgba(255, 255, 255, 0.1);
border-radius: 16px 16px 2px 16px;
padding: 14px 20px;
max-width: 80%;
box-shadow: 0 2px 6px rgba(0, 0, 0, 0.25);
}
.user-msg-text {
font-family: 'Inter', sans-serif;
font-size: 15px;
color: #e0e3e6;
line-height: 1.5;
margin: 0;
}

/* Réponse Assistant IA */
.ai-response-row {
display: flex;
gap: 14px;
align-items: flex-start;
width: 100%;
}
.ai-avatar {
width: 38px;
height: 38px;
border-radius: 8px;
background: #1d2022;
border: 1px solid rgba(120, 216, 186, 0.3);
display: flex;
align-items: center;
justify-content: center;
flex-shrink: 0;
margin-top: 2px;
box-shadow: 0 0 12px rgba(120, 216, 186, 0.15);
}
.ai-response-card {
flex: 1;
background-color: #1d2022;
border: 1px solid rgba(255, 255, 255, 0.08);
border-radius: 2px 16px 16px 16px;
padding: 18px 22px;
box-shadow: 0 2px 8px rgba(0, 0, 0, 0.25);
}
.ai-intro-text {
font-family: 'Inter', sans-serif;
font-size: 14.5px;
color: #e0e3e6;
line-height: 1.6;
margin: 0 0 16px 0;
}

/* Tableau de saturation disque */
.ai-table-box {
background-color: #191c1e;
border: 1px solid rgba(255, 255, 255, 0.06);
border-radius: 6px;
overflow: hidden;
margin-bottom: 16px;
}
.ai-table-head {
display: grid;
grid-template-columns: 5fr 4fr 3fr;
gap: 8px;
background-color: #1d2022;
padding: 8px 14px;
border-bottom: 1px solid rgba(255, 255, 255, 0.08);
font-family: 'IBM Plex Sans', monospace;
font-size: 10px;
font-weight: 700;
color: #bdc9c3;
text-transform: uppercase;
letter-spacing: 0.08em;
}
.ai-table-head .col-right { text-align: right; }

.ai-table-row {
display: grid;
grid-template-columns: 5fr 4fr 3fr;
gap: 8px;
padding: 10px 14px;
border-bottom: 1px solid rgba(255, 255, 255, 0.04);
align-items: center;
}
.ai-table-row:last-child { border-bottom: none; }
.ai-table-row:hover { background-color: rgba(255, 255, 255, 0.02); }

.srv-name {
display: flex;
align-items: center;
gap: 8px;
font-family: 'IBM Plex Sans', monospace;
font-size: 12.5px;
font-weight: 600;
}
.srv-date {
font-family: 'Inter', sans-serif;
font-size: 12.5px;
color: #e0e3e6;
}
.srv-usage {
font-family: 'IBM Plex Sans', monospace;
font-size: 12.5px;
font-weight: 700;
text-align: right;
}

/* Bouton Nettoyage */
.btn-ai-action {
display: inline-flex;
align-items: center;
gap: 8px;
background-color: rgba(31, 138, 112, 0.12);
border: 1px solid rgba(31, 138, 112, 0.35);
color: #78d8ba;
font-family: 'IBM Plex Sans', monospace;
font-size: 11px;
font-weight: 700;
text-transform: uppercase;
letter-spacing: 0.06em;
padding: 7px 14px;
border-radius: 4px;
cursor: pointer;
transition: background-color 0.15s ease;
}
.btn-ai-action:hover {
background-color: rgba(31, 138, 112, 0.25);
}

/* Puces de suggestion */
.suggestion-chips {
display: flex;
flex-wrap: wrap;
gap: 8px;
margin-top: 14px;
margin-bottom: 12px;
}
.chip-btn {
display: inline-flex;
align-items: center;
gap: 6px;
background-color: #1d2022;
border: 1px solid rgba(255, 255, 255, 0.1);
border-radius: 9999px;
padding: 5px 14px;
font-family: 'Inter', sans-serif;
font-size: 12.5px;
color: #bdc9c3;
cursor: pointer;
transition: all 0.15s ease;
}
.chip-btn:hover {
border-color: #81d0f8;
color: #81d0f8;
background-color: rgba(129, 208, 248, 0.06);
}

/* Zone de Saisie Inférieure */
.chat-input-box {
position: relative;
background-color: #191c1e;
border: 1px solid rgba(255, 255, 255, 0.12);
border-radius: 12px;
padding: 14px 16px 46px 16px;
min-height: 85px;
transition: border-color 0.15s ease;
}
.chat-input-box:focus-within {
border-color: #81d0f8;
box-shadow: 0 0 12px rgba(1, 112, 148, 0.25);
}
.chat-input-placeholder {
font-family: 'Inter', sans-serif;
font-size: 14.5px;
color: rgba(189, 201, 195, 0.45);
}

.readonly-pill {
position: absolute;
bottom: 10px;
left: 14px;
display: inline-flex;
align-items: center;
gap: 5px;
background-color: #323538;
border: 1px solid rgba(255, 255, 255, 0.08);
border-radius: 4px;
padding: 2px 8px;
font-family: 'IBM Plex Sans', monospace;
font-size: 10px;
font-weight: 600;
color: #bdc9c3;
text-transform: uppercase;
letter-spacing: 0.08em;
}

.chat-input-actions {
position: absolute;
bottom: 8px;
right: 8px;
display: flex;
align-items: center;
gap: 6px;
}
.btn-input-attach {
width: 34px;
height: 34px;
border-radius: 6px;
background: transparent;
border: none;
display: flex;
align-items: center;
justify-content: center;
color: #bdc9c3;
cursor: pointer;
transition: background-color 0.15s ease;
}
.btn-input-attach:hover {
background-color: rgba(255, 255, 255, 0.08);
color: #dfe4e0;
}
.btn-input-send {
width: 34px;
height: 34px;
border-radius: 6px;
background-color: #1F8A70;
border: none;
display: flex;
align-items: center;
justify-content: center;
color: #ffffff;
cursor: pointer;
box-shadow: 0 2px 8px rgba(31, 138, 112, 0.35);
transition: background-color 0.15s ease;
}
.btn-input-send:hover {
background-color: #269e81;
}

.chat-disclaimer {
text-align: center;
font-family: 'IBM Plex Sans', monospace;
font-size: 11px;
color: rgba(189, 201, 195, 0.5);
margin-top: 8px;
}
</style>""", unsafe_allow_html=True)

# ── CONTENU DE LA PAGE ASSISTANT IA ──────────────────────────────────────────
st.markdown("""<div class="chat-canvas">

<!-- 1. BULLE UTILISATEUR -->
<div class="user-msg-row">
<div class="user-msg-bubble">
<p class="user-msg-text">Quels serveurs risquent une saturation disque cette semaine ?</p>
</div>
</div>

<!-- 2. RÉPONSE ASSISTANT IA -->
<div class="ai-response-row">
<div class="ai-avatar">
<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="#78d8ba" stroke-width="2" style="display: block;">
<rect x="3" y="11" width="18" height="10" rx="2"/><circle cx="12" cy="5" r="2"/><path d="M12 7v4"/><line x1="8" y1="16" x2="8" y2="16"/><line x1="16" y1="16" x2="16" y2="16"/>
</svg>
</div>
<div class="ai-response-card">
<p class="ai-intro-text">
D'après l'analyse prédictive des tendances de consommation, 3 serveurs présentent un risque élevé de saturation disque ( &gt;90%) d'ici la fin de la semaine :
</p>

<!-- Tableau Données Prédictives -->
<div class="ai-table-box">
<div class="ai-table-head">
<div>Serveur</div>
<div>Date Prévue</div>
<div class="col-right">Usage Actuel</div>
</div>

<!-- Ligne 1 : APP-SRV-01 (Critique) -->
<div class="ai-table-row">
<div class="srv-name" style="color: #ffb4ab;">
<svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="#ffb4ab" stroke-width="2.5" class="pulse-critical" style="display: inline-block;">
<path d="M10.29 3.86L1.82 18a2 2 0 0 0 1.71 3h16.94a2 2 0 0 0 1.71-3L13.71 3.86a2 2 0 0 0-3.42 0z"/><line x1="12" y1="9" x2="12" y2="13"/><line x1="12" y1="17" x2="12.01" y2="17"/>
</svg>
<span>APP-SRV-01</span>
</div>
<div class="srv-date">Jeu. 14 Nov, 02:00</div>
<div class="srv-usage" style="color: #ffb4ab;">88.4%</div>
</div>

<!-- Ligne 2 : DB-CLUSTER-M1 (Teal) -->
<div class="ai-table-row" style="background-color: rgba(25, 28, 30, 0.4);">
<div class="srv-name" style="color: #78d8ba;">
<svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="#78d8ba" stroke-width="2" style="display: inline-block;">
<rect x="2" y="2" width="20" height="8" rx="2"/><rect x="2" y="14" width="20" height="8" rx="2"/><line x1="6" y1="6" x2="6.01" y2="6"/><line x1="6" y1="18" x2="6.01" y2="18"/>
</svg>
<span>DB-CLUSTER-M1</span>
</div>
<div class="srv-date">Ven. 15 Nov, 18:30</div>
<div class="srv-usage" style="color: #78d8ba;">86.1%</div>
</div>

<!-- Ligne 3 : STO-NODE-04 (Teal) -->
<div class="ai-table-row">
<div class="srv-name" style="color: #78d8ba;">
<svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="#78d8ba" stroke-width="2" style="display: inline-block;">
<rect x="2" y="2" width="20" height="8" rx="2"/><rect x="2" y="14" width="20" height="8" rx="2"/><line x1="6" y1="6" x2="6.01" y2="6"/><line x1="6" y1="18" x2="6.01" y2="18"/>
</svg>
<span>STO-NODE-04</span>
</div>
<div class="srv-date">Sam. 16 Nov, 09:15</div>
<div class="srv-usage" style="color: #78d8ba;">85.0%</div>
</div>
</div>

<!-- Bouton d'Action Nettoyage -->
<button class="btn-ai-action">
<svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" style="display: inline-block;">
<path d="M12 2v4M4.93 4.93l2.83 2.83M20 12h-4M19.07 4.93l-2.83 2.83M2 12h4M12 18v4M4.93 19.07l2.83-2.83M19.07 19.07l-2.83-2.83"/>
</svg>
<span>PROPOSER NETTOYAGE</span>
</button>
</div>
</div>

<!-- 3. SUGGESTION CHIPS -->
<div>
<div class="suggestion-chips">
<button class="chip-btn">
<svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" style="display: inline-block;">
<line x1="18" y1="20" x2="18" y2="10"/><line x1="12" y1="20" x2="12" y2="4"/><line x1="6" y1="20" x2="6" y2="14"/>
</svg>
<span>Analyser le trafic réseau</span>
</button>
<button class="chip-btn">
<svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" style="display: inline-block;">
<path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/>
</svg>
<span>Vérifier la conformité</span>
</button>
<button class="chip-btn">
<svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" style="display: inline-block;">
<path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/><polyline points="14 2 14 8 20 8"/><line x1="16" y1="13" x2="8" y2="13"/><line x1="16" y1="17" x2="8" y2="17"/>
</svg>
<span>Résumé des alertes critiques</span>
</button>
</div>

<!-- 4. ZONE DE SAISIE AVEC BADGE LECTURE SEULE -->
<div class="chat-input-box">
<div class="chat-input-placeholder">Demander à Sentinelle IA...</div>
<div class="readonly-pill">
<svg width="11" height="11" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" style="display: inline-block;">
<path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z"/><circle cx="12" cy="12" r="3"/>
</svg>
<span>LECTURE SEULE</span>
</div>
<div class="chat-input-actions">
<button class="btn-input-attach" title="Joindre un fichier">
<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" style="display: inline-block;">
<path d="M21.44 11.05l-9.19 9.19a6 6 0 0 1-8.49-8.49l9.19-9.19a4 4 0 0 1 5.66 5.66l-9.2 9.19a2 2 0 0 1-2.83-2.83l8.49-8.48"/>
</svg>
</button>
<button class="btn-input-send" title="Envoyer">
<svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" style="display: block;">
<line x1="22" y1="2" x2="11" y2="13"/><polygon points="22 2 15 22 11 13 2 9 22 2"/>
</svg>
</button>
</div>
</div>

<div class="chat-disclaimer">
L'IA peut faire des erreurs. Vérifiez les informations critiques dans les dashboards principaux.
</div>
</div>

</div>""", unsafe_allow_html=True)
