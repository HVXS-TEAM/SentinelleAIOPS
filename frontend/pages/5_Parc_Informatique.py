"""
5_Parc_Informatique.py — Sentinelle AIOps
Pixel-perfect ref : Ecrans_Reference/Parc_Informatique/code.html + screen.png
Sources : DESIGN.md (tokens) + code.html (DOM & layout) + screen.png (vérification visuelle)
"""
import os, sys
import streamlit as st

st.set_page_config(
    page_title="Parc Informatique — Sentinelle AIOps",
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
    active="Parc Informatique",
    page_title="Parc informatique",
    search_placeholder="Search resources (Cmd+K)..."
)

# ── STYLES DÉDIÉS AU MODULE PARC INFORMATIQUE ────────────────────────────────
st.markdown("""<style>
/* Cartes conteneurs */
.parc-card {
background-color: var(--surface-container-low, #181d1b);
border: 1px solid rgba(255, 255, 255, 0.08);
border-radius: 10px;
overflow: hidden;
position: relative;
}

/* Zone Topologie */
.topo-canvas {
width: 100%;
min-height: 290px;
background-color: #121715;
background-image: radial-gradient(circle at 2px 2px, rgba(255,255,255,0.06) 1px, transparent 0);
background-size: 24px 24px;
position: relative;
display: flex;
align-items: center;
justify-content: center;
border-radius: 8px;
padding: 10px 0;
}
.topo-badge {
position: absolute;
top: 12px; left: 12px;
background: rgba(38, 43, 41, 0.85);
backdrop-filter: blur(4px);
padding: 4px 10px;
border-radius: 4px;
border: 1px solid rgba(255, 255, 255, 0.1);
font-family: var(--font-mono, 'IBM Plex Sans', monospace);
font-size: 11px;
font-weight: 700;
color: var(--on-surface-variant, #bdc9c3);
letter-spacing: 0.05em;
z-index: 10;
}
.topo-legend {
position: absolute;
bottom: 12px; left: 12px;
background: rgba(38, 43, 41, 0.85);
backdrop-filter: blur(4px);
padding: 8px 12px;
border-radius: 6px;
border: 1px solid rgba(255, 255, 255, 0.1);
z-index: 10;
display: flex;
flex-direction: column;
gap: 4px;
}
.topo-controls {
position: absolute;
bottom: 12px; right: 12px;
display: flex;
flex-direction: column;
gap: 4px;
z-index: 10;
}
.topo-btn {
background: rgba(38, 43, 41, 0.9);
border: 1px solid rgba(255, 255, 255, 0.12);
color: var(--on-surface, #dfe4e0);
width: 28px; height: 28px;
border-radius: 4px;
display: flex;
align-items: center;
justify-content: center;
cursor: pointer;
font-size: 14px;
}
.topo-btn:hover {
background: #313633;
}

/* Tableau Inventaire */
.inv-table {
width: 100%;
border-collapse: collapse;
font-family: var(--font-body, 'Inter', sans-serif);
font-size: 12.5px;
text-align: left;
}
.inv-table th {
padding: 8px 12px;
font-family: var(--font-mono, 'IBM Plex Sans', monospace);
font-size: 10px;
font-weight: 700;
color: var(--on-surface-variant, #bdc9c3);
text-transform: uppercase;
letter-spacing: 0.06em;
border-bottom: 1px solid rgba(255, 255, 255, 0.1);
background-color: var(--surface-container-high, #262b29);
}
.inv-table td {
padding: 8px 12px;
border-bottom: 1px solid rgba(255, 255, 255, 0.05);
vertical-align: middle;
}
.inv-table tr:hover {
background-color: rgba(255, 255, 255, 0.03);
}
.inv-table tr.selected-critical {
background-color: rgba(147, 0, 10, 0.12);
border-left: 3px solid var(--error, #ffb4ab);
}

/* Volet Latéral Détaillé */
.panel-detail {
background-color: var(--surface-container-low, #181d1b);
border: 1px solid rgba(255, 255, 255, 0.08);
border-radius: 10px;
padding: 16px;
display: flex;
flex-direction: column;
gap: 12px;
}
.detail-box {
background-color: var(--surface-container, #1c211e);
border: 1px solid rgba(255, 255, 255, 0.06);
border-radius: 6px;
padding: 10px 12px;
}
.detail-box-title {
font-family: var(--font-mono, 'IBM Plex Sans', monospace);
font-size: 10px;
font-weight: 700;
color: var(--on-surface-variant, #bdc9c3);
letter-spacing: 0.06em;
text-transform: uppercase;
margin-bottom: 8px;
display: flex;
align-items: center;
gap: 6px;
}

/* Sparklines à Barres (CSS) */
.spark-bar-container {
height: 28px;
width: 100%;
border-left: 1px solid rgba(255, 255, 255, 0.15);
border-bottom: 1px solid rgba(255, 255, 255, 0.15);
display: flex;
align-items: flex-end;
gap: 2px;
padding-top: 2px;
margin-top: 4px;
}
.spark-bar {
flex: 1;
border-radius: 1px 1px 0 0;
}

/* Bouton Terminal SSH */
.btn-terminal {
width: 100%;
background-color: rgba(1, 112, 148, 0.15);
border: 1px solid var(--secondary, #81d0f8);
color: var(--secondary, #81d0f8);
padding: 8px 14px;
border-radius: 6px;
font-family: var(--font-body, 'Inter', sans-serif);
font-size: 13px;
font-weight: 600;
display: flex;
align-items: center;
justify-content: center;
gap: 8px;
cursor: pointer;
transition: background-color 0.15s ease;
}
.btn-terminal:hover {
background-color: rgba(1, 112, 148, 0.28);
}
</style>""", unsafe_allow_html=True)

# ── EN-TÊTE DE PAGE ──────────────────────────────────────────────────────────
st.markdown("""<div style="display: flex; justify-content: space-between; align-items: flex-end; margin-bottom: 18px; flex-wrap: wrap; gap: 12px;">
<div>
<div style="font-family: var(--font-headline, 'Inter'); font-size: 28px; font-weight: 700; color: var(--on-surface, #dfe4e0); line-height: 1.2;">
Parc informatique
</div>
<div style="font-family: var(--font-body, 'Inter'); font-size: 14px; color: var(--on-surface-variant, #bdc9c3); margin-top: 4px;">
Gérez et visualisez l'ensemble de vos actifs réseau.
</div>
</div>
<div style="display: flex; gap: 10px;">
<button style="background: #1c211e; border: 1px solid rgba(255, 255, 255, 0.15); color: #dfe4e0; padding: 6px 14px; border-radius: 6px; font-size: 13px; font-weight: 500; display: inline-flex; align-items: center; gap: 6px; cursor: pointer;">
<svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" xmlns="http://www.w3.org/2000/svg"><polygon points="22 3 2 3 10 12.46 10 19 14 21 14 12.46 22 3"/></svg>
Filtrer
</button>
<button style="background: var(--primary, #78d8ba); color: #00382b; border: none; padding: 6px 14px; border-radius: 6px; font-size: 13px; font-weight: 600; display: inline-flex; align-items: center; gap: 6px; cursor: pointer;">
<svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" xmlns="http://www.w3.org/2000/svg"><line x1="12" y1="5" x2="12" y2="19"/><line x1="5" y1="12" x2="19" y2="12"/></svg>
Ajouter un équipement
</button>
</div>
</div>""", unsafe_allow_html=True)

# ── DISPOSITION EN 2 COLONNES (8/12 et 4/12) ─────────────────────────────────
col_main, col_panel = st.columns([2.2, 1.1])

with col_main:
    # ── SECTION 1 : VUE TOPOLOGIQUE RÉSEAU (SVG) ──────────────────────────────
    st.markdown("""<div class="parc-card" style="margin-bottom: 16px;">
<div class="topo-canvas">
<div class="topo-badge">VUE TOPOLOGIQUE</div>

<!-- Légende -->
<div class="topo-legend">
<div style="display: flex; align-items: center; gap: 6px; font-size: 11px; color: var(--on-surface-variant);">
<span style="width: 8px; height: 8px; border-radius: 50%; background: #3da186;"></span>
<span>Sain</span>
</div>
<div style="display: flex; align-items: center; gap: 6px; font-size: 11px; color: var(--on-surface-variant);">
<span style="width: 8px; height: 8px; border-radius: 50%; background: #d37768;"></span>
<span>Avertissement</span>
</div>
<div style="display: flex; align-items: center; gap: 6px; font-size: 11px; color: var(--on-surface-variant);">
<span style="width: 8px; height: 8px; border-radius: 50%; background: #ffb4ab;"></span>
<span>Critique</span>
</div>
</div>

<!-- Contrôles -->
<div class="topo-controls">
<div class="topo-btn">+</div>
<div class="topo-btn">−</div>
<div class="topo-btn">⛶</div>
</div>

<!-- Graphe SVG Topologique -->
<svg viewBox="0 0 600 300" width="100%" height="270" xmlns="http://www.w3.org/2000/svg" style="display: block; max-width: 600px; margin: 0 auto;">
<!-- Liens -->
<line x1="300" y1="50" x2="150" y2="150" stroke="#3e4945" stroke-width="1.5"/>
<line x1="300" y1="50" x2="450" y2="150" stroke="#3e4945" stroke-width="1.5"/>
<line x1="150" y1="150" x2="100" y2="250" stroke="#3e4945" stroke-width="1.5"/>
<line x1="150" y1="150" x2="200" y2="250" stroke="#3e4945" stroke-width="1.5"/>
<line x1="450" y1="150" x2="400" y2="250" stroke="#ffb4ab" stroke-width="1.5" stroke-dasharray="4,4"/>
<line x1="450" y1="150" x2="500" y2="250" stroke="#3e4945" stroke-width="1.5"/>
<line x1="200" y1="250" x2="400" y2="250" stroke="#3e4945" stroke-width="1.5" stroke-opacity="0.3"/>

<!-- CORE-RTR-01 (Warning / Orange) -->
<circle cx="300" cy="50" r="20" fill="none" stroke="#d37768" stroke-width="1" opacity="0.4"/>
<circle cx="300" cy="50" r="16" fill="#d37768"/>
<text x="300" y="82" fill="#dfe4e0" font-family="Inter, sans-serif" font-size="10px" text-anchor="middle" font-weight="600">CORE-RTR-01</text>

<!-- DIST-SW-A (Healthy / Teal) -->
<circle cx="150" cy="150" r="12" fill="#3da186"/>
<text x="150" y="176" fill="#dfe4e0" font-family="Inter, sans-serif" font-size="10px" text-anchor="middle">DIST-SW-A</text>

<!-- DIST-SW-B (Healthy / Teal) -->
<circle cx="450" cy="150" r="12" fill="#3da186"/>
<text x="450" y="176" fill="#dfe4e0" font-family="Inter, sans-serif" font-size="10px" text-anchor="middle">DIST-SW-B</text>

<!-- SRV-WEB-01 -->
<circle cx="100" cy="250" r="8" fill="#3da186"/>
<text x="100" y="272" fill="#dfe4e0" font-family="Inter, sans-serif" font-size="10px" text-anchor="middle">SRV-WEB-01</text>

<!-- SRV-DB-01 -->
<circle cx="200" cy="250" r="8" fill="#3da186"/>
<text x="200" y="272" fill="#dfe4e0" font-family="Inter, sans-serif" font-size="10px" text-anchor="middle">SRV-DB-01</text>

<!-- FW-EXT-02 (Critique / Red avec halo pulsant) -->
<circle cx="400" cy="250" r="14" fill="none" stroke="#ffb4ab" stroke-width="1" opacity="0.7">
<animate attributeName="r" values="8;16;8" dur="2s" repeatCount="indefinite"/>
<animate attributeName="opacity" values="0.8;0;0.8" dur="2s" repeatCount="indefinite"/>
</circle>
<circle cx="400" cy="250" r="8" fill="#ffb4ab"/>
<text x="400" y="272" fill="#ffb4ab" font-family="Inter, sans-serif" font-size="10px" text-anchor="middle" font-weight="600">FW-EXT-02</text>

<!-- SRV-APP-02 -->
<circle cx="500" cy="250" r="8" fill="#3da186"/>
<text x="500" y="272" fill="#dfe4e0" font-family="Inter, sans-serif" font-size="10px" text-anchor="middle">SRV-APP-02</text>
</svg>
</div>
</div>""", unsafe_allow_html=True)

    # ── SECTION 2 : TABLEAU D'INVENTAIRE (1,248) ───────────────────────────────
    st.markdown("""<div class="parc-card">
<!-- Header du tableau -->
<div style="padding: 10px 14px; background-color: var(--surface-container, #1c211e); border-bottom: 1px solid rgba(255, 255, 255, 0.08); display: flex; justify-content: space-between; align-items: center;">
<div style="font-family: var(--font-headline); font-size: 15px; font-weight: 600; color: var(--on-surface, #dfe4e0);">
Inventaire (1,248)
</div>
<div style="position: relative; width: 220px;">
<svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="#87938e" stroke-width="2" xmlns="http://www.w3.org/2000/svg" style="position: absolute; left: 8px; top: 7px;">
<circle cx="11" cy="11" r="8"/><line x1="21" y1="21" x2="16.65" y2="16.65"/>
</svg>
<input type="text" placeholder="Filtrer par nom, IP, MAC..." style="width: 100%; background: #262b29; border: 1px solid rgba(255, 255, 255, 0.1); border-radius: 4px; padding: 3px 8px 3px 26px; font-size: 11px; color: #dfe4e0; outline: none;"/>
</div>
</div>

<!-- Table -->
<div style="overflow-x: auto;">
<table class="inv-table">
<thead>
<tr>
<th>Équipement</th>
<th>IP / MAC</th>
<th>OS / Firmware</th>
<th>Uptime</th>
<th style="text-align: center;">Santé</th>
<th style="text-align: right;">Dernière vue</th>
</tr>
</thead>
<tbody>
<!-- Ligne 1 : CORE-RTR-01 -->
<tr>
<td>
<div style="display: flex; align-items: center; gap: 8px;">
<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="#78d8ba" stroke-width="2" xmlns="http://www.w3.org/2000/svg">
<rect x="2" y="6" width="20" height="12" rx="2"/><circle cx="6" cy="12" r="1"/><circle cx="10" cy="12" r="1"/><circle cx="14" cy="12" r="1"/>
</svg>
<span style="font-weight: 600; color: var(--on-surface);">CORE-RTR-01</span>
</div>
</td>
<td style="font-family: var(--font-mono); font-size: 11px;">
<div style="color: var(--on-surface);">10.0.0.1</div>
<div style="font-size: 9px; color: var(--on-surface-variant); opacity: 0.7;">00:1A:2B:3C:4D:5E</div>
</td>
<td style="color: var(--on-surface-variant);">Cisco IOS XE 17.3.2</td>
<td style="font-family: var(--font-mono); color: var(--on-surface-variant);">342d 12h</td>
<td style="text-align: center;">
<div style="position: relative; width: 22px; height: 22px; margin: 0 auto; display: flex; align-items: center; justify-content: center;">
<svg viewBox="0 0 24 24" width="22" height="22" xmlns="http://www.w3.org/2000/svg" style="transform: rotate(-90deg); display: block;">
<circle cx="12" cy="12" r="10" fill="none" stroke="#3e4945" stroke-width="2.5"/>
<circle cx="12" cy="12" r="10" fill="none" stroke="#3da186" stroke-width="2.5" stroke-dasharray="62.8" stroke-dashoffset="6.28"/>
</svg>
<span style="position: absolute; font-family: var(--font-mono); font-size: 8px; font-weight: 700; color: #3da186;">90</span>
</div>
</td>
<td style="text-align: right; color: var(--on-surface-variant); font-size: 11px;">Il y a 2 min</td>
</tr>

<!-- Ligne 2 : FW-EXT-02 (CRITIQUE / SÉLECTIONNÉ) -->
<tr class="selected-critical">
<td>
<div style="display: flex; align-items: center; gap: 8px;">
<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="#ffb4ab" stroke-width="2" xmlns="http://www.w3.org/2000/svg">
<path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/>
</svg>
<span style="font-weight: 600; color: #ffb4ab;">FW-EXT-02</span>
</div>
</td>
<td style="font-family: var(--font-mono); font-size: 11px;">
<div style="color: var(--on-surface);">192.168.1.254</div>
<div style="font-size: 9px; color: var(--on-surface-variant); opacity: 0.7;">A1:B2:C3:D4:E5:F6</div>
</td>
<td style="color: var(--on-surface-variant);">Palo Alto PAN-OS 10.1</td>
<td style="font-family: var(--font-mono); color: var(--on-surface-variant);">12d 4h</td>
<td style="text-align: center;">
<div style="position: relative; width: 22px; height: 22px; margin: 0 auto; display: flex; align-items: center; justify-content: center;">
<svg viewBox="0 0 24 24" width="22" height="22" xmlns="http://www.w3.org/2000/svg" style="transform: rotate(-90deg); display: block;">
<circle cx="12" cy="12" r="10" fill="none" stroke="#3e4945" stroke-width="2.5"/>
<circle cx="12" cy="12" r="10" fill="none" stroke="#ffb4ab" stroke-width="2.5" stroke-dasharray="62.8" stroke-dashoffset="43.96"/>
</svg>
<span style="position: absolute; font-family: var(--font-mono); font-size: 8px; font-weight: 700; color: #ffb4ab;">30</span>
</div>
</td>
<td style="text-align: right; color: var(--on-surface-variant); font-size: 11px;">Il y a 1 min</td>
</tr>

<!-- Ligne 3 : SRV-DB-01 -->
<tr>
<td>
<div style="display: flex; align-items: center; gap: 8px;">
<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="#d37768" stroke-width="2" xmlns="http://www.w3.org/2000/svg">
<rect x="2" y="2" width="20" height="8" rx="2"/><rect x="2" y="14" width="20" height="8" rx="2"/><line x1="6" y1="6" x2="6.01" y2="6"/><line x1="6" y1="18" x2="6.01" y2="18"/>
</svg>
<span style="font-weight: 600; color: var(--on-surface);">SRV-DB-01</span>
</div>
</td>
<td style="font-family: var(--font-mono); font-size: 11px;">
<div style="color: var(--on-surface);">10.0.10.50</div>
<div style="font-size: 9px; color: var(--on-surface-variant); opacity: 0.7;">11:22:33:44:55:66</div>
</td>
<td style="color: var(--on-surface-variant);">Ubuntu 22.04 LTS</td>
<td style="font-family: var(--font-mono); color: var(--on-surface-variant);">45d 8h</td>
<td style="text-align: center;">
<div style="position: relative; width: 22px; height: 22px; margin: 0 auto; display: flex; align-items: center; justify-content: center;">
<svg viewBox="0 0 24 24" width="22" height="22" xmlns="http://www.w3.org/2000/svg" style="transform: rotate(-90deg); display: block;">
<circle cx="12" cy="12" r="10" fill="none" stroke="#3e4945" stroke-width="2.5"/>
<circle cx="12" cy="12" r="10" fill="none" stroke="#d37768" stroke-width="2.5" stroke-dasharray="62.8" stroke-dashoffset="21.98"/>
</svg>
<span style="position: absolute; font-family: var(--font-mono); font-size: 8px; font-weight: 700; color: #d37768;">65</span>
</div>
</td>
<td style="text-align: right; color: var(--on-surface-variant); font-size: 11px;">Il y a 5 min</td>
</tr>

<!-- Ligne 4 : DIST-SW-A -->
<tr>
<td>
<div style="display: flex; align-items: center; gap: 8px;">
<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="#78d8ba" stroke-width="2" xmlns="http://www.w3.org/2000/svg">
<rect x="2" y="4" width="20" height="16" rx="2"/><line x1="6" y1="9" x2="6.01" y2="9"/><line x1="10" y1="9" x2="10.01" y2="9"/><line x1="14" y1="9" x2="14.01" y2="9"/><line x1="18" y1="9" x2="18.01" y2="9"/><line x1="6" y1="15" x2="6.01" y2="15"/><line x1="10" y1="15" x2="10.01" y2="15"/><line x1="14" y1="15" x2="14.01" y2="15"/><line x1="18" y1="15" x2="18.01" y2="15"/>
</svg>
<span style="font-weight: 600; color: var(--on-surface);">DIST-SW-A</span>
</div>
</td>
<td style="font-family: var(--font-mono); font-size: 11px;">
<div style="color: var(--on-surface);">10.0.5.1</div>
<div style="font-size: 9px; color: var(--on-surface-variant); opacity: 0.7;">AA:BB:CC:DD:EE:FF</div>
</td>
<td style="color: var(--on-surface-variant);">ArubaOS-CX 10.08</td>
<td style="font-family: var(--font-mono); color: var(--on-surface-variant);">120d 2h</td>
<td style="text-align: center;">
<div style="position: relative; width: 22px; height: 22px; margin: 0 auto; display: flex; align-items: center; justify-content: center;">
<svg viewBox="0 0 24 24" width="22" height="22" xmlns="http://www.w3.org/2000/svg" style="transform: rotate(-90deg); display: block;">
<circle cx="12" cy="12" r="10" fill="none" stroke="#3e4945" stroke-width="2.5"/>
<circle cx="12" cy="12" r="10" fill="none" stroke="#3da186" stroke-width="2.5" stroke-dasharray="62.8" stroke-dashoffset="1.25"/>
</svg>
<span style="position: absolute; font-family: var(--font-mono); font-size: 8px; font-weight: 700; color: #3da186;">98</span>
</div>
</td>
<td style="text-align: right; color: var(--on-surface-variant); font-size: 11px;">Il y a 1 min</td>
</tr>
</tbody>
</table>
</div>
</div>""", unsafe_allow_html=True)

with col_panel:
    # ── VOLET LATÉRAL DÉTAILLÉ DE L'ÉQUIPEMENT (FW-EXT-02) ────────────────────
    st.markdown("""<div class="panel-detail">
<!-- Header du volet -->
<div style="display: flex; justify-content: space-between; align-items: flex-start; padding-bottom: 10px; border-bottom: 1px solid rgba(255, 255, 255, 0.08);">
<div style="display: flex; gap: 10px; align-items: center;">
<div style="width: 36px; height: 36px; border-radius: 6px; background: rgba(147, 0, 10, 0.25); border: 1px solid rgba(255, 180, 171, 0.3); display: flex; align-items: center; justify-content: center;">
<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="#ffb4ab" stroke-width="2" xmlns="http://www.w3.org/2000/svg">
<path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/>
</svg>
</div>
<div>
<div style="font-family: var(--font-headline); font-size: 16px; font-weight: 700; color: var(--on-surface, #dfe4e0);">FW-EXT-02</div>
<div style="display: flex; align-items: center; gap: 4px; margin-top: 1px;">
<span style="width: 6px; height: 6px; border-radius: 50%; background: #ffb4ab;"></span>
<span style="font-family: var(--font-mono); font-size: 10px; font-weight: 700; color: #ffb4ab; letter-spacing: 0.05em;">CRITIQUE</span>
</div>
</div>
</div>
<button style="background: transparent; border: none; color: var(--on-surface-variant); cursor: pointer; padding: 2px;">
<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" xmlns="http://www.w3.org/2000/svg"><line x1="18" y1="6" x2="6" y2="18"/><line x1="6" y1="6" x2="18" y2="18"/></svg>
</button>
</div>

<!-- 1. IDENTIFICATION -->
<div class="detail-box">
<div class="detail-box-title">IDENTIFICATION</div>
<div style="display: grid; grid-template-columns: 1fr 1fr; gap: 8px; font-size: 11.5px;">
<div>
<div style="color: var(--on-surface-variant); font-size: 10px;">Modèle</div>
<div style="color: var(--on-surface); font-weight: 500;">PA-3220</div>
</div>
<div>
<div style="color: var(--on-surface-variant); font-size: 10px;">Numéro de série</div>
<div style="font-family: var(--font-mono); color: var(--on-surface);">0123456789X</div>
</div>
<div>
<div style="color: var(--on-surface-variant); font-size: 10px;">Localisation</div>
<div style="color: var(--on-surface);">Datacenter Paris - Rack 04</div>
</div>
<div>
<div style="color: var(--on-surface-variant); font-size: 10px;">Rôle</div>
<div style="color: var(--on-surface);">Pare-feu Périmétrique</div>
</div>
</div>
</div>

<!-- 2. PERFORMANCES (24H) -->
<div class="detail-box">
<div class="detail-box-title">PERFORMANCES (24H)</div>

<!-- CPU Load -->
<div style="margin-bottom: 10px;">
<div style="display: flex; justify-content: space-between; align-items: center; font-size: 11.5px; margin-bottom: 2px;">
<span style="color: var(--on-surface);">CPU Load</span>
<span style="font-family: var(--font-mono); font-weight: 700; color: #ffb4ab;">94%</span>
</div>
<div class="spark-bar-container">
<div class="spark-bar" style="height: 30%; background: rgba(120, 216, 186, 0.4);"></div>
<div class="spark-bar" style="height: 40%; background: rgba(120, 216, 186, 0.4);"></div>
<div class="spark-bar" style="height: 35%; background: rgba(120, 216, 186, 0.4);"></div>
<div class="spark-bar" style="height: 45%; background: rgba(120, 216, 186, 0.4);"></div>
<div class="spark-bar" style="height: 55%; background: rgba(211, 119, 104, 0.6);"></div>
<div class="spark-bar" style="height: 65%; background: rgba(211, 119, 104, 0.6);"></div>
<div class="spark-bar" style="height: 78%; background: rgba(255, 180, 171, 0.8);"></div>
<div class="spark-bar" style="height: 85%; background: rgba(255, 180, 171, 0.8);"></div>
<div class="spark-bar" style="height: 98%; background: #ffb4ab;"></div>
<div class="spark-bar" style="height: 94%; background: #ffb4ab;"></div>
</div>
</div>

<!-- Mémoire -->
<div>
<div style="display: flex; justify-content: space-between; align-items: center; font-size: 11.5px; margin-bottom: 2px;">
<span style="color: var(--on-surface);">Mémoire</span>
<span style="font-family: var(--font-mono); font-weight: 700; color: #d37768;">78%</span>
</div>
<div class="spark-bar-container">
<div class="spark-bar" style="height: 60%; background: rgba(120, 216, 186, 0.4);"></div>
<div class="spark-bar" style="height: 62%; background: rgba(120, 216, 186, 0.4);"></div>
<div class="spark-bar" style="height: 65%; background: rgba(120, 216, 186, 0.4);"></div>
<div class="spark-bar" style="height: 64%; background: rgba(120, 216, 186, 0.4);"></div>
<div class="spark-bar" style="height: 68%; background: rgba(120, 216, 186, 0.4);"></div>
<div class="spark-bar" style="height: 70%; background: rgba(211, 119, 104, 0.6);"></div>
<div class="spark-bar" style="height: 72%; background: rgba(211, 119, 104, 0.6);"></div>
<div class="spark-bar" style="height: 75%; background: rgba(211, 119, 104, 0.6);"></div>
<div class="spark-bar" style="height: 79%; background: #d37768;"></div>
<div class="spark-bar" style="height: 78%; background: #d37768;"></div>
</div>
</div>
</div>

<!-- 3. ANOMALIES DE SÉCURITÉ -->
<div class="detail-box">
<div class="detail-box-title" style="color: var(--error, #ffb4ab);">
<svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="#ffb4ab" stroke-width="2.5" xmlns="http://www.w3.org/2000/svg"><circle cx="12" cy="12" r="10"/><line x1="12" y1="8" x2="12" y2="12"/><line x1="12" y1="16" x2="12.01" y2="16"/></svg>
ANOMALIES DE SÉCURITÉ
</div>
<div style="display: flex; flex-direction: column; gap: 6px;">
<div style="background: rgba(147, 0, 10, 0.15); border: 1px solid rgba(255, 180, 171, 0.2); padding: 8px; border-radius: 4px; display: flex; gap: 8px; align-items: flex-start;">
<svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="#ffb4ab" stroke-width="2" xmlns="http://www.w3.org/2000/svg" style="margin-top: 1px;"><polygon points="13 2 3 14 12 14 11 22 21 10 12 10 13 2"/></svg>
<div>
<div style="font-size: 11.5px; font-weight: 600; color: var(--on-surface);">DDoS Suspecté (Port 443)</div>
<div style="font-family: var(--font-mono); font-size: 9.5px; color: var(--on-surface-variant); margin-top: 1px;">Il y a 15 min - Règle de blocage automatique échouée</div>
</div>
</div>
<div style="background: rgba(211, 119, 104, 0.12); border: 1px solid rgba(211, 119, 104, 0.2); padding: 8px; border-radius: 4px; display: flex; gap: 8px; align-items: flex-start;">
<svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="#d37768" stroke-width="2" xmlns="http://www.w3.org/2000/svg" style="margin-top: 1px;"><path d="M21 2l-2 2m-1-1l-3 3m2 2l-3 3m-1-1l-3 3m2 2l-3 3M3 21l18-18"/></svg>
<div>
<div style="font-size: 11.5px; font-weight: 600; color: var(--on-surface);">Échecs d'authentification admin multiples</div>
<div style="font-family: var(--font-mono); font-size: 9.5px; color: var(--on-surface-variant); margin-top: 1px;">Il y a 4h - Source: 185.xxx.xxx.xxx</div>
</div>
</div>
</div>
</div>

<!-- 4. NETDEVOPS & SAUVEGARDES -->
<div class="detail-box">
<div class="detail-box-title">NETDEVOPS &amp; SAUVEGARDES</div>
<div style="display: flex; justify-content: space-between; align-items: center; font-size: 11.5px; padding-bottom: 6px; border-bottom: 1px solid rgba(255, 255, 255, 0.05);">
<span style="color: var(--on-surface-variant);">Dernière sauvegarde config</span>
<span style="color: var(--primary, #78d8ba); font-weight: 600; font-size: 11px;">✓ Aujourd'hui, 02:00</span>
</div>
<div style="display: flex; justify-content: space-between; align-items: center; font-size: 11.5px; padding-top: 6px;">
<span style="color: var(--on-surface-variant);">Audit de conformité</span>
<span style="color: var(--error, #ffb4ab); font-weight: 600; font-size: 11px;">⚠ Échec (OS obsolète)</span>
</div>
</div>

<!-- Bouton Terminal SSH -->
<button class="btn-terminal">
<svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" xmlns="http://www.w3.org/2000/svg"><polyline points="4 17 10 11 4 5"/><line x1="12" y1="19" x2="20" y2="19"/></svg>
Ouvrir un terminal SSH
</button>
</div>""", unsafe_allow_html=True)
