"""
6_Reporting_&_Admin.py — Sentinelle AIOps
Pixel-perfect ref : Ecrans_Reference/Admin & Rapport/code.html + screen.png
Sources : DESIGN.md (tokens) + code.html (DOM & layout) + screen.png (vérification visuelle)
"""
import os, sys
from pathlib import Path
import streamlit as st

_LOGO_PATH = str(Path(__file__).parent.parent / "static" / "logo.png")

st.set_page_config(
    page_title="Administration & Rapports — Sentinelle AIOps",
    page_icon=_LOGO_PATH,
    layout="wide",
    initial_sidebar_state="expanded",
)

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from page_template import page_bootstrap

# ── Garde d'authentification ─────────────────────────────────────────────────
if not st.session_state.get("authenticated", False):
    st.switch_page("app.py")

page_bootstrap(
    active="Rapports",
    page_title="Administration & Rapports",
    search_placeholder="Rechercher rapports, utilisateurs, logs..."
)

# ── CSS DÉDIÉ AU MODULE ADMINISTRATION & RAPPORTS ────────────────────────────
st.markdown("""<style>
@keyframes pulse-urgent {
0%, 100% { opacity: 1; transform: scale(1); }
50% { opacity: 0.8; transform: scale(0.95); }
}
.animate-pulse-urgent { animation: pulse-urgent 1s infinite ease-in-out; }

/* Bento Container Cards */
.admin-card {
background-color: var(--surface-container);
border: 1px solid rgba(255, 255, 255, 0.06);
border-radius: 8px;
overflow: hidden;
display: flex;
flex-direction: column;
}

/* En-têtes de cartes */
.admin-card-header {
padding: 12px 18px;
border-bottom: 1px solid rgba(255, 255, 255, 0.06);
background: var(--surface-container-high);
display: flex;
justify-content: space-between;
align-items: center;
}
.admin-card-title {
font-family: 'IBM Plex Sans', monospace;
font-size: 11px;
font-weight: 700;
color: #78d8ba;
text-transform: uppercase;
letter-spacing: 0.08em;
display: flex;
align-items: center;
gap: 8px;
}

/* Tableau Utilisateurs */
.users-table {
width: 100%;
border-collapse: collapse;
font-family: 'Inter', sans-serif;
font-size: 12.5px;
text-align: left;
}
.users-table th {
padding: 10px 16px;
font-family: 'IBM Plex Sans', monospace;
font-size: 10px;
font-weight: 700;
color: var(--on-surface-variant, #bdc9c3);
text-transform: uppercase;
letter-spacing: 0.08em;
background: var(--surface-container-high);
border-bottom: 1px solid rgba(255, 255, 255, 0.1);
}
.users-table td {
padding: 11px 16px;
border-bottom: 1px solid rgba(255, 255, 255, 0.05);
vertical-align: middle;
}
.users-table tr:hover { background-color: rgba(255, 255, 255, 0.03); }

/* Badges de Rôles */
.role-badge-admin {
padding: 2px 8px;
border-radius: 2px;
background: rgba(120, 216, 186, 0.15);
color: #78d8ba;
font-family: 'IBM Plex Sans', monospace;
font-size: 10px;
font-weight: 700;
text-transform: uppercase;
border: 1px solid rgba(120, 216, 186, 0.3);
}
.role-badge-tech {
padding: 2px 8px;
border-radius: 2px;
background: rgba(129, 208, 248, 0.15);
color: #81d0f8;
font-family: 'IBM Plex Sans', monospace;
font-size: 10px;
font-weight: 700;
text-transform: uppercase;
border: 1px solid rgba(129, 208, 248, 0.3);
}
.role-badge-visitor {
padding: 2px 8px;
border-radius: 2px;
background: var(--surface-container-high);
color: var(--on-surface, #e0e3e6);
font-family: 'IBM Plex Sans', monospace;
font-size: 10px;
font-weight: 700;
text-transform: uppercase;
border: 1px solid rgba(255, 255, 255, 0.1);
}

/* Tableau Audit Log */
.audit-table {
width: 100%;
border-collapse: collapse;
font-family: 'IBM Plex Sans', monospace;
font-size: 11px;
text-align: left;
}
.audit-table th {
padding: 8px 12px;
font-weight: 500;
color: rgba(189, 201, 195, 0.7);
text-transform: uppercase;
border-bottom: 1px solid rgba(255, 255, 255, 0.1);
}
.audit-table td {
padding: 7px 12px;
border-bottom: 1px solid rgba(255, 255, 255, 0.05);
color: #bdc9c3;
vertical-align: middle;
}
.audit-table tr:hover { background-color: rgba(255, 255, 255, 0.03); }
.audit-table tr.crit-row { background-color: rgba(255, 180, 171, 0.05); }

/* Item Bibliothèque de Rapports */
.report-card-item {
background-color: var(--surface-container-high);
border: 1px solid rgba(255, 255, 255, 0.08);
border-radius: 6px;
padding: 12px 14px;
display: flex;
justify-content: space-between;
align-items: center;
transition: border-color 0.15s ease;
cursor: pointer;
}
.report-card-item:hover {
border-color: rgba(129, 208, 248, 0.5);
}
.report-dl-btn {
width: 32px; height: 32px;
border-radius: 50%;
background: rgba(255, 255, 255, 0.06);
display: flex; align-items: center; justify-content: center;
color: #bdc9c3;
border: none;
cursor: pointer;
transition: all 0.15s ease;
}
.report-dl-btn:hover {
background: #81d0f8;
color: #003548;
}

/* Toggle Switches */
.toggle-switch {
position: relative;
display: inline-block;
width: 36px;
height: 20px;
}
.toggle-switch input { opacity: 0; width: 0; height: 0; }
.toggle-slider {
position: absolute; cursor: pointer; top: 0; left: 0; right: 0; bottom: 0;
background-color: var(--surface-container-highest); transition: .2s; border-radius: 20px;
}
.toggle-slider:before {
position: absolute; content: ""; height: 14px; width: 14px; left: 3px; bottom: 3px;
background-color: white; transition: .2s; border-radius: 50%;
}
input:checked + .toggle-slider { background-color: #78d8ba; }
input:checked + .toggle-slider:before { transform: translateX(16px); }

/* Boutons Top Header */
.btn-hdr-sync {
padding: 7px 14px; border-radius: 6px; border: 1px solid #81d0f8;
color: #81d0f8; background: transparent; font-family: 'IBM Plex Sans', monospace;
font-size: 11px; font-weight: 600; text-transform: uppercase; letter-spacing: 0.05em;
display: inline-flex; align-items: center; gap: 7px; cursor: pointer; transition: background-color 0.15s ease;
}
.btn-hdr-sync:hover { background-color: rgba(129, 208, 248, 0.12); }
.btn-hdr-new {
padding: 7px 14px; border-radius: 6px; border: none;
background: #78d8ba; color: #00382b; font-family: 'IBM Plex Sans', monospace;
font-size: 11px; font-weight: 700; text-transform: uppercase; letter-spacing: 0.05em;
display: inline-flex; align-items: center; gap: 7px; cursor: pointer; transition: opacity 0.15s ease;
}
.btn-hdr-new:hover { opacity: 0.9; }
</style>""", unsafe_allow_html=True)

# ── 1. EN-TÊTE DE PAGE & ACTIONS ─────────────────────────────────────────────
st.markdown("""<div style="display: flex; justify-content: space-between; align-items: flex-end; margin-bottom: 20px; flex-wrap: wrap; gap: 12px;">
<div>
<div style="font-family: 'Inter', sans-serif; font-size: 28px; font-weight: 700; color: #dfe4e0; line-height: 1.2;">Administration &amp; Rapports</div>
<div style="font-family: 'Inter', sans-serif; font-size: 14px; color: #bdc9c3; margin-top: 4px;">Gestion de la plateforme et audits</div>
</div>
<div style="display: flex; gap: 10px; align-items: center;">
<button class="btn-hdr-sync">
<svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="#81d0f8" stroke-width="2.5" style="display: block;">
<path d="M21.5 2v6h-6M21.34 15.57a10 10 0 1 1-.57-8.38l5.67-5.67"/>
</svg>
<span>SYNCHRONISER</span>
</button>
<button class="btn-hdr-new">
<svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="#00382b" stroke-width="2.5" style="display: block;">
<line x1="12" y1="5" x2="12" y2="19"/><line x1="5" y1="12" x2="19" y2="12"/>
</svg>
<span>NOUVEAU RAPPORT</span>
</button>
</div>
</div>""", unsafe_allow_html=True)

# ── 2. DISPOSITION BENTO (COLONNE GAUCHE 8/12 & DROITE 4/12) ──────────────────
col_left, col_right = st.columns([2.2, 1.1])

# ── COLONNE GAUCHE ─────────────────────────────────────────────────────────────
with col_left:

    # ── MODULE 1: GESTION DES UTILISATEURS ────────────────────────────────────
    st.markdown("""<div class="admin-card" style="margin-bottom: 20px;">
<div class="admin-card-header">
<div class="admin-card-title">
<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="#78d8ba" stroke-width="2" style="display: block;">
<path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2"/><circle cx="9" cy="7" r="4"/><path d="M23 21v-2a4 4 0 0 0-3-3.87"/><path d="M16 3.13a4 4 0 0 1 0 7.75"/>
</svg>
<span>Gestion des Utilisateurs</span>
</div>
<button style="background: transparent; border: none; color: #bdc9c3; cursor: pointer; padding: 2px;">
<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="#bdc9c3" stroke-width="2" style="display: block;">
<line x1="8" y1="6" x2="21" y2="6"/><line x1="8" y1="12" x2="21" y2="12"/><line x1="8" y1="18" x2="21" y2="18"/><line x1="3" y1="6" x2="3.01" y2="6"/><line x1="3" y1="12" x2="3.01" y2="12"/><line x1="3" y1="18" x2="3.01" y2="18"/>
</svg>
</button>
</div>
<div style="overflow-x: auto;">
<table class="users-table">
<thead>
<tr>
<th>UTILISATEUR</th>
<th>RÔLE</th>
<th>ÉTAT MFA</th>
<th>DERNIÈRE CONNEXION</th>
<th style="text-align: right;">ACTIONS</th>
</tr>
</thead>
<tbody>
<tr>
<td>
<div style="display: flex; align-items: center; gap: 10px;">
<div style="width: 32px; height: 32px; border-radius: 4px; background: #3da186; display: flex; align-items: center; justify-content: center; color: #00382b; font-weight: 700; font-size: 11px;">SC</div>
<div>
<div style="font-weight: 600; color: #dfe4e0;">Sarah Connor</div>
<div style="font-size: 11px; color: #bdc9c3;">s.connor@sentinelle.io</div>
</div>
</div>
</td>
<td><span class="role-badge-admin">Administrateur</span></td>
<td>
<div style="display: flex; align-items: center; gap: 4px; color: #78d8ba; font-size: 12px; font-weight: 500;">
<svg width="14" height="14" viewBox="0 0 24 24" fill="#78d8ba" stroke="#78d8ba" stroke-width="1" style="display: block;">
<path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/>
</svg>
<span>Actif</span>
</div>
</td>
<td style="font-family: 'IBM Plex Sans', monospace; font-size: 11.5px; color: #bdc9c3;">Aujourd'hui, 08:14</td>
<td style="text-align: right;">
<div style="display: flex; align-items: center; justify-content: flex-end; gap: 8px; color: #bdc9c3;">
<button style="background: transparent; border: none; color: inherit; cursor: pointer; padding: 2px;" title="Modifier">
<svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="#bdc9c3" stroke-width="2" style="display: block;"><path d="M11 4H4a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2v-7"/><path d="M18.5 2.5a2.121 2.121 0 0 1 3 3L12 15l-4 1 1-4 9.5-9.5z"/></svg>
</button>
<button style="background: transparent; border: none; color: inherit; cursor: pointer; padding: 2px;" title="Supprimer">
<svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="#bdc9c3" stroke-width="2" style="display: block;"><polyline points="3 6 5 6 21 6"/><path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"/></svg>
</button>
</div>
</td>
</tr>
<tr>
<td>
<div style="display: flex; align-items: center; gap: 10px;">
<div style="width: 32px; height: 32px; border-radius: 4px; background: #017094; display: flex; align-items: center; justify-content: center; color: #ceedff; font-weight: 700; font-size: 11px;">DB</div>
<div>
<div style="font-weight: 600; color: #dfe4e0;">David Bowman</div>
<div style="font-size: 11px; color: #bdc9c3;">d.bowman@sentinelle.io</div>
</div>
</div>
</td>
<td><span class="role-badge-tech">Technicien</span></td>
<td>
<div style="display: flex; align-items: center; gap: 4px; color: #78d8ba; font-size: 12px; font-weight: 500;">
<svg width="14" height="14" viewBox="0 0 24 24" fill="#78d8ba" stroke="#78d8ba" stroke-width="1" style="display: block;">
<path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/>
</svg>
<span>Actif</span>
</div>
</td>
<td style="font-family: 'IBM Plex Sans', monospace; font-size: 11.5px; color: #bdc9c3;">Hier, 16:45</td>
<td style="text-align: right;">
<div style="display: flex; align-items: center; justify-content: flex-end; gap: 8px; color: #bdc9c3;">
<button style="background: transparent; border: none; color: inherit; cursor: pointer; padding: 2px;" title="Modifier">
<svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="#bdc9c3" stroke-width="2" style="display: block;"><path d="M11 4H4a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2v-7"/><path d="M18.5 2.5a2.121 2.121 0 0 1 3 3L12 15l-4 1 1-4 9.5-9.5z"/></svg>
</button>
<button style="background: transparent; border: none; color: inherit; cursor: pointer; padding: 2px;" title="Supprimer">
<svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="#bdc9c3" stroke-width="2" style="display: block;"><polyline points="3 6 5 6 21 6"/><path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"/></svg>
</button>
</div>
</td>
</tr>
<tr>
<td>
<div style="display: flex; align-items: center; gap: 10px;">
<div style="width: 32px; height: 32px; border-radius: 4px; background: #323538; display: flex; align-items: center; justify-content: center; color: #bdc9c3; font-weight: 700; font-size: 11px;">ER</div>
<div>
<div style="font-weight: 600; color: #dfe4e0;">Ellen Ripley</div>
<div style="font-size: 11px; color: #bdc9c3;">e.ripley@audit.ext</div>
</div>
</div>
</td>
<td><span class="role-badge-visitor">Visiteur</span></td>
<td>
<div style="display: flex; align-items: center; gap: 4px; color: #ffb4ab; font-size: 12px; font-weight: 500;">
<svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="#ffb4ab" stroke-width="2" style="display: block;">
<path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/><line x1="12" y1="8" x2="12" y2="12"/><line x1="12" y1="16" x2="12.01" y2="16"/>
</svg>
<span>Inactif</span>
</div>
</td>
<td style="font-family: 'IBM Plex Sans', monospace; font-size: 11.5px; color: #bdc9c3;">02 Mars, 09:00</td>
<td style="text-align: right;">
<div style="display: flex; align-items: center; justify-content: flex-end; gap: 8px; color: #bdc9c3;">
<button style="background: transparent; border: none; color: inherit; cursor: pointer; padding: 2px;" title="Modifier">
<svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="#bdc9c3" stroke-width="2" style="display: block;"><path d="M11 4H4a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2v-7"/><path d="M18.5 2.5a2.121 2.121 0 0 1 3 3L12 15l-4 1 1-4 9.5-9.5z"/></svg>
</button>
<button style="background: transparent; border: none; color: inherit; cursor: pointer; padding: 2px;" title="Supprimer">
<svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="#bdc9c3" stroke-width="2" style="display: block;"><polyline points="3 6 5 6 21 6"/><path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"/></svg>
</button>
</div>
</td>
</tr>
</tbody>
</table>
</div>
</div>""", unsafe_allow_html=True)

    # ── MODULE 2: JOURNAL D'AUDIT ──────────────────────────────────────────────
    st.markdown("""<div class="admin-card">
<div class="admin-card-header">
<div class="admin-card-title">
<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="#78d8ba" stroke-width="2" style="display: block;">
<polyline points="4 17 10 11 4 5"/><line x1="12" y1="19" x2="20" y2="19"/>
</svg>
<span>Journal d'Audit</span>
</div>
<button style="font-family: 'Inter', sans-serif; font-size: 11px; color: var(--on-surface-variant); padding: 3px 8px; background: var(--surface-container-high); border: 1px solid var(--outline); border-radius: 4px; cursor: pointer;">Export CSV</button>
</div>
<div style="overflow-x: auto; padding: 6px; background: var(--surface-container-lowest);">
<table class="audit-table">
<thead>
<tr>
<th>Horodatage</th>
<th>Utilisateur</th>
<th>Action</th>
<th>Cible</th>
<th>Statut</th>
</tr>
</thead>
<tbody>
<tr>
<td style="color: #81d0f8;">2024-03-05T08:15:22Z</td>
<td>s.connor</td>
<td style="color: #78d8ba; font-weight: 600;">AUTH_SUCCESS</td>
<td>auth.gateway.main</td>
<td><span style="width: 6px; height: 6px; border-radius: 50%; background: #78d8ba; display: inline-block; margin-right: 4px;"></span> 200</td>
</tr>
<tr>
<td style="color: #81d0f8;">2024-03-05T08:18:41Z</td>
<td>s.connor</td>
<td style="color: #a7c8ff; font-weight: 600;">CONF_UPDATE</td>
<td>fw-core-eu-west</td>
<td><span style="width: 6px; height: 6px; border-radius: 50%; background: #78d8ba; display: inline-block; margin-right: 4px;"></span> 200</td>
</tr>
<tr class="crit-row">
<td style="color: #81d0f8;">2024-03-05T09:02:11Z</td>
<td>system.auto</td>
<td style="color: #ffb4ab; font-weight: 700;">ALERT_TRIGGER</td>
<td>db-cluster-01.cpu</td>
<td style="color: #ffb4ab; font-weight: 600;" class="animate-pulse-urgent">
<svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="#ffb4ab" stroke-width="2.5" style="display: inline-block; vertical-align: middle; margin-right: 2px;">
<path d="M10.29 3.86L1.82 18a2 2 0 0 0 1.71 3h16.94a2 2 0 0 0 1.71-3L13.71 3.86a2 2 0 0 0-3.42 0z"/><line x1="12" y1="9" x2="12" y2="13"/><line x1="12" y1="17" x2="12.01" y2="17"/>
</svg>
CRIT
</td>
</tr>
<tr>
<td style="color: #81d0f8;">2024-03-05T09:05:00Z</td>
<td>d.bowman</td>
<td style="color: #78d8ba; font-weight: 600;">AUTH_SUCCESS</td>
<td>auth.gateway.vpn</td>
<td><span style="width: 6px; height: 6px; border-radius: 50%; background: #78d8ba; display: inline-block; margin-right: 4px;"></span> 200</td>
</tr>
<tr>
<td style="color: #81d0f8;">2024-03-05T09:12:33Z</td>
<td>d.bowman</td>
<td style="color: #a7c8ff; font-weight: 600;">SERVICE_RESTART</td>
<td>db-cluster-01.node-a</td>
<td><span style="width: 6px; height: 6px; border-radius: 50%; background: #78d8ba; display: inline-block; margin-right: 4px;"></span> 200</td>
</tr>
</tbody>
</table>
</div>
</div>""", unsafe_allow_html=True)

# ── COLONNE DROITE ─────────────────────────────────────────────────────────────
with col_right:

    # ── MODULE 3: BIBLIOTHÈQUE DE RAPPORTS ────────────────────────────────────
    st.markdown("""<div class="admin-card" style="margin-bottom: 20px;">
<div class="admin-card-header">
<div class="admin-card-title">
<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="#78d8ba" stroke-width="2" style="display: block;">
<path d="M4 19.5A2.5 2.5 0 0 1 6.5 17H20"/><path d="M6.5 2H20v20H6.5A2.5 2.5 0 0 1 4 19.5v-15A2.5 2.5 0 0 1 6.5 2z"/>
</svg>
<span>Bibliothèque de Rapports</span>
</div>
</div>
<div style="padding: 14px; display: flex; flex-direction: column; gap: 10px;">

<!-- Rapport 1 -->
<div class="report-card-item">
<div>
<div style="font-size: 13.5px; font-weight: 600; color: #dfe4e0;">Audit Sécurité Hebdomadaire</div>
<div style="font-family: 'IBM Plex Sans', monospace; font-size: 10.5px; color: #bdc9c3; margin-top: 3px; display: flex; align-items: center; gap: 5px;">
<svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="#bdc9c3" stroke-width="2" style="display: block;"><rect x="3" y="4" width="18" height="18" rx="2" ry="2"/><line x1="16" y1="2" x2="16" y2="6"/><line x1="8" y1="2" x2="8" y2="6"/><line x1="3" y1="10" x2="21" y2="10"/></svg>
<span>04 Mars 2024</span>
<span style="width: 3px; height: 3px; border-radius: 50%; background: #bdc9c3; opacity: 0.5;"></span>
<span>S9 (Fév 26 - Mar 03)</span>
</div>
</div>
<button class="report-dl-btn" title="Télécharger">
<svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="#bdc9c3" stroke-width="2" style="display: block;"><path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/><polyline points="7 10 12 15 17 10"/><line x1="12" y1="15" x2="12" y2="3"/></svg>
</button>
</div>

<!-- Rapport 2 -->
<div class="report-card-item">
<div>
<div style="font-size: 13.5px; font-weight: 600; color: #dfe4e0;">Synthèse Perf. Mensuelle</div>
<div style="font-family: 'IBM Plex Sans', monospace; font-size: 10.5px; color: #bdc9c3; margin-top: 3px; display: flex; align-items: center; gap: 5px;">
<svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="#bdc9c3" stroke-width="2" style="display: block;"><rect x="3" y="4" width="18" height="18" rx="2" ry="2"/><line x1="16" y1="2" x2="16" y2="6"/><line x1="8" y1="2" x2="8" y2="6"/><line x1="3" y1="10" x2="21" y2="10"/></svg>
<span>01 Mars 2024</span>
<span style="width: 3px; height: 3px; border-radius: 50%; background: #bdc9c3; opacity: 0.5;"></span>
<span>Février 2024</span>
</div>
</div>
<button class="report-dl-btn" title="Télécharger">
<svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="#bdc9c3" stroke-width="2" style="display: block;"><path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/><polyline points="7 10 12 15 17 10"/><line x1="12" y1="15" x2="12" y2="3"/></svg>
</button>
</div>

<!-- Rapport 3 -->
<div class="report-card-item">
<div>
<div style="font-size: 13.5px; font-weight: 600; color: #dfe4e0;">Inventaire Parc Actif</div>
<div style="font-family: 'IBM Plex Sans', monospace; font-size: 10.5px; color: #bdc9c3; margin-top: 3px; display: flex; align-items: center; gap: 5px;">
<svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="#bdc9c3" stroke-width="2" style="display: block;"><rect x="3" y="4" width="18" height="18" rx="2" ry="2"/><line x1="16" y1="2" x2="16" y2="6"/><line x1="8" y1="2" x2="8" y2="6"/><line x1="3" y1="10" x2="21" y2="10"/></svg>
<span>01 Mars 2024</span>
<span style="width: 3px; height: 3px; border-radius: 50%; background: #bdc9c3; opacity: 0.5;"></span>
<span>T1 - Ad Hoc</span>
</div>
</div>
<button class="report-dl-btn" title="Télécharger">
<svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="#bdc9c3" stroke-width="2" style="display: block;"><path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/><polyline points="7 10 12 15 17 10"/><line x1="12" y1="15" x2="12" y2="3"/></svg>
</button>
</div>

</div>
</div>""", unsafe_allow_html=True)

    # ── MODULE 4: CONFIGURATION NOTIFICATIONS ────────────────────────────────
    st.markdown("""<div class="admin-card">
<div class="admin-card-header">
<div class="admin-card-title">
<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="#78d8ba" stroke-width="2" style="display: block;">
<path d="M18 8A6 6 0 0 0 6 8c0 7-3 9-3 9h18s-3-2-3-9"/><path d="M13.73 21a2 2 0 0 1-3.46 0"/>
</svg>
<span>Configuration Notifications</span>
</div>
</div>
<div style="padding: 16px; display: flex; flex-direction: column; gap: 16px;">

<!-- CANAUX DE DIFFUSION -->
<div>
<div style="font-family: 'IBM Plex Sans', monospace; font-size: 10px; color: #bdc9c3; text-transform: uppercase; letter-spacing: 0.08em; padding-bottom: 6px; border-bottom: 1px solid rgba(255, 255, 255, 0.08); margin-bottom: 10px;">
CANAUX DE DIFFUSION
</div>

<div style="display: flex; flex-direction: column; gap: 10px;">
<!-- Email -->
<div style="display: flex; align-items: center; justify-content: space-between;">
<div style="display: flex; align-items: center; gap: 8px;">
<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="#bdc9c3" stroke-width="2" style="display: block;"><path d="M4 4h16c1.1 0 2 .9 2 2v12c0 1.1-.9 2-2 2H4c-1.1 0-2-.9-2-2V6c0-1.1.9-2 2-2z"/><polyline points="22,6 12,13 2,6"/></svg>
<span style="font-size: 12.5px; color: #dfe4e0;">Email (SMTP Interne)</span>
</div>
<label class="toggle-switch">
<input type="checkbox" checked/>
<span class="toggle-slider"></span>
</label>
</div>

<!-- Telegram -->
<div style="display: flex; align-items: center; justify-content: space-between;">
<div style="display: flex; align-items: center; gap: 8px;">
<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="#bdc9c3" stroke-width="2" style="display: block;"><line x1="22" y1="2" x2="11" y2="13"/><polygon points="22 2 15 22 11 13 2 9 22 2"/></svg>
<span style="font-size: 12.5px; color: #dfe4e0;">Telegram (Bot API)</span>
</div>
<label class="toggle-switch">
<input type="checkbox" checked/>
<span class="toggle-slider"></span>
</label>
</div>

<!-- Discord -->
<div style="display: flex; align-items: center; justify-content: space-between;">
<div style="display: flex; align-items: center; gap: 8px;">
<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="#bdc9c3" stroke-width="2" style="display: block;"><path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"/></svg>
<span style="font-size: 12.5px; color: #dfe4e0;">Discord (Webhook)</span>
</div>
<label class="toggle-switch">
<input type="checkbox"/>
<span class="toggle-slider"></span>
</label>
</div>
</div>
</div>

<!-- RÈGLES DE ROUTAGE -->
<div>
<div style="font-family: 'IBM Plex Sans', monospace; font-size: 10px; color: #bdc9c3; text-transform: uppercase; letter-spacing: 0.08em; padding-bottom: 6px; border-bottom: 1px solid rgba(255, 255, 255, 0.08); margin-bottom: 10px;">
RÈGLES DE ROUTAGE
</div>

<div style="display: flex; flex-direction: column; gap: 6px;">
<!-- Critical -->
<div style="background: var(--surface-container-high); padding: 8px 12px; border-radius: 4px; border: 1px solid rgba(255, 255, 255, 0.05); display: flex; align-items: center; justify-content: space-between;">
<div style="display: flex; align-items: center; gap: 6px;">
<span style="width: 8px; height: 8px; border-radius: 50%; background: #ffb4ab;" class="animate-pulse-urgent"></span>
<span style="font-family: 'IBM Plex Sans', monospace; font-size: 11.5px; font-weight: 600; color: var(--on-surface);">Critical</span>
</div>
<span style="font-family: 'IBM Plex Sans', monospace; font-size: 10px; color: var(--on-surface-variant); background: var(--surface-container-lowest); padding: 2px 6px; border-radius: 3px;">Tous les canaux</span>
</div>

<!-- Warning -->
<div style="background: var(--surface-container-high); padding: 8px 12px; border-radius: 4px; border: 1px solid rgba(255, 255, 255, 0.05); display: flex; align-items: center; justify-content: space-between;">
<div style="display: flex; align-items: center; gap: 6px;">
<span style="width: 8px; height: 8px; border-radius: 50%; background: #81d0f8;"></span>
<span style="font-family: 'IBM Plex Sans', monospace; font-size: 11.5px; font-weight: 600; color: var(--on-surface);">Warning</span>
</div>
<span style="font-family: 'IBM Plex Sans', monospace; font-size: 10px; color: var(--on-surface-variant); background: var(--surface-container-lowest); padding: 2px 6px; border-radius: 3px;">Email &amp; Telegram</span>
</div>

<!-- Info -->
<div style="background: var(--surface-container-high); padding: 8px 12px; border-radius: 4px; border: 1px solid rgba(255, 255, 255, 0.05); display: flex; align-items: center; justify-content: space-between;">
<div style="display: flex; align-items: center; gap: 6px;">
<span style="width: 8px; height: 8px; border-radius: 50%; background: #3e4945;"></span>
<span style="font-family: 'IBM Plex Sans', monospace; font-size: 11.5px; font-weight: 600; color: var(--on-surface);">Info</span>
</div>
<span style="font-family: 'IBM Plex Sans', monospace; font-size: 10px; color: var(--on-surface-variant); background: var(--surface-container-lowest); padding: 2px 6px; border-radius: 3px;">Email Uniquement</span>
</div>
</div>
</div>

</div>
</div>""", unsafe_allow_html=True)
