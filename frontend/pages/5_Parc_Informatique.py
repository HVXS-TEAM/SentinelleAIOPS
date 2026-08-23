"""
5_Parc_Informatique.py — Sentinelle AIOps
Pixel-perfect ref : Ecrans_Reference/Parc_Informatique/code.html + screen.png

Features:
  - Page header: "Parc informatique", "Gérez et visualisez l'ensemble de vos actifs réseau."
  - 2-column layout [2.5, 1]:
    - Left column:
      - Topology map card: SVG graph topology_graph() + VUE TOPOLOGIQUE toggle + Legend (Sain, Avertissement, Critique)
      - Inventory table card: 4 equipment rows with highlighted selected item (FW-EXT-02)
    - Right column (Detail panel):
      - FW-EXT-02 device details (CRITIQUE status, 2x2 grid field(), performance mini_bar_chart(), security alert_item(), NetDevOps status, Terminal SSH button)
"""
import os, sys
import streamlit as st
import pandas as pd

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from page_template import page_bootstrap
from components import (
    card, mono, badge, topology_graph, mini_bar_chart, alert_item, field
)

# ── 1. BOOTSTRAP ──────────────────────────────────────────────────────────────
# ── Garde d'authentification ─────────────────────────────────────────────────
if not st.session_state.get("authenticated", False):
    st.switch_page("app.py")

page_bootstrap(
    active="Parc Informatique",
    page_title="Parc informatique",
    search_placeholder="Rechercher des équipements, IP, MAC..."
)

# ── 2. CSS SPÉCIFIQUE AU MODULE ──────────────────────────────────────────────
st.markdown("""<style>
/* Inventory table styling */
.inventory-table {
    width: 100%;
    border-collapse: collapse;
    font-family: var(--font-body);
    font-size: 13px;
}
.inventory-table th {
    padding: 10px 14px;
    font-family: var(--font-mono);
    font-size: 10px;
    font-weight: 700;
    color: var(--on-surface-variant);
    text-transform: uppercase;
    letter-spacing: 0.08em;
    background: rgba(25, 28, 30, 0.7);
    border-bottom: 1px solid rgba(255,255,255,0.1);
}
.inventory-table td {
    padding: 10px 14px;
    border-bottom: 1px solid rgba(255,255,255,0.05);
    vertical-align: middle;
}
.inventory-table tr:hover { background: rgba(255,255,255,0.03); }
.inventory-table tr.selected-row {
    background: rgba(255, 180, 171, 0.08);
    border-left: 3px solid var(--error);
}

/* Detail panel sub-sections */
.detail-section {
    background: var(--surface-container);
    border: 1px solid rgba(62,73,69,0.3);
    border-radius: 8px;
    padding: 14px;
    margin-bottom: 16px;
}
.detail-sec-title {
    font-family: var(--font-mono);
    font-size: 10px;
    font-weight: 700;
    color: var(--on-surface-variant);
    text-transform: uppercase;
    letter-spacing: 0.08em;
    margin-bottom: 10px;
    display: flex;
    align-items: center;
    gap: 6px;
}

/* Terminal SSH Button */
.btn-terminal {
    width: 100%;
    padding: 10px 16px;
    border-radius: 6px;
    border: 1px solid var(--secondary);
    background: rgba(1, 112, 148, 0.15);
    color: var(--secondary);
    font-family: var(--font-ui);
    font-size: 13px;
    font-weight: 600;
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 8px;
    cursor: pointer;
    transition: background 150ms ease;
}
.btn-terminal:hover { background: rgba(1, 112, 148, 0.3); }
</style>""", unsafe_allow_html=True)

# ── 3. EN-TÊTE DE PAGE ────────────────────────────────────────────────────────
with st.container(key="parc-page-header"):
    st.markdown('<h1 style="font-size:28px;font-weight:700;margin:0;color:var(--on-surface);font-family:\'IBM Plex Sans\', sans-serif;">Parc informatique</h1>', unsafe_allow_html=True)
    st.markdown('<p style="font-size:14px;color:var(--on-surface-variant);margin:4px 0 20px 0;">Gérez et visualisez l\'ensemble de vos actifs réseau.</p>', unsafe_allow_html=True)

# ── 4. LAYOUT 2 COLONNES (GAUCHE / DROITE) ────────────────────────────────────
col_left, col_right = st.columns([2.5, 1])

# ── COLONNE GAUCHE ─────────────────────────────────────────────────────────────
with col_left:

    # 4a. Carte Topologie Réseau
    with card(key="topology-map-card"):
        # Top-left badge + Legend
        st.html("""
        <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:12px;">
            <div style="font-family:var(--font-mono);font-size:11px;font-weight:700;color:var(--on-surface-variant);background:var(--surface-container-highest);padding:4px 10px;border-radius:4px;border:1px solid rgba(62,73,69,0.3);" class="notranslate" translate="no">
                VUE TOPOLOGIQUE
            </div>
            <div style="display:flex;gap:14px;align-items:center;font-size:11px;color:var(--on-surface-variant);">
                <div style="display:flex;align-items:center;gap:6px;">
                    <span style="width:8px;height:8px;border-radius:50%;background:#3da186;display:inline-block;"></span>
                    <span>Sain</span>
                </div>
                <div style="display:flex;align-items:center;gap:6px;">
                    <span style="width:8px;height:8px;border-radius:50%;background:#d37768;display:inline-block;"></span>
                    <span>Avertissement</span>
                </div>
                <div style="display:flex;align-items:center;gap:6px;">
                    <span style="width:8px;height:8px;border-radius:50%;background:#ffb4ab;display:inline-block;"></span>
                    <span>Critique</span>
                </div>
            </div>
        </div>
        """)

        nodes = [
            {'id': 'CORE-RTR-01', 'label': 'CORE-RTR-01', 'x': 300, 'y': 50,  'status': 'warning'},
            {'id': 'DIST-SW-A',   'label': 'DIST-SW-A',   'x': 150, 'y': 150, 'status': 'healthy'},
            {'id': 'DIST-SW-B',   'label': 'DIST-SW-B',   'x': 450, 'y': 150, 'status': 'healthy'},
            {'id': 'SRV-WEB-01',  'label': 'SRV-WEB-01',  'x': 100, 'y': 250, 'status': 'healthy'},
            {'id': 'SRV-DB-01',   'label': 'SRV-DB-01',   'x': 200, 'y': 250, 'status': 'healthy'},
            {'id': 'FW-EXT-02',   'label': 'FW-EXT-02',   'x': 400, 'y': 250, 'status': 'critical'},
            {'id': 'SRV-APP-02',  'label': 'SRV-APP-02',  'x': 500, 'y': 250, 'status': 'healthy'},
        ]

        edges = [
            ('CORE-RTR-01', 'DIST-SW-A'),
            ('CORE-RTR-01', 'DIST-SW-B'),
            ('DIST-SW-A', 'SRV-WEB-01'),
            ('DIST-SW-A', 'SRV-DB-01'),
            ('DIST-SW-B', 'FW-EXT-02'),
            ('DIST-SW-B', 'SRV-APP-02'),
        ]

        topology_graph(nodes, edges, view_w=600, view_h=300)

    # 4b. Carte Inventaire des Équipements
    with card(key="inventory-card"):
        st.html("""
        <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:12px;">
            <div class="snt-card-title notranslate" translate="no" style="margin:0;">Inventaire (1,248)</div>
            <div style="position:relative;width:240px;">
                <input type="text" placeholder="Filtrer par nom, IP, MAC..." disabled style="width:100%;background:var(--surface-container-high);border:1px solid rgba(62,73,69,0.3);border-radius:4px;padding:4px 8px 4px 28px;font-size:12px;color:var(--on-surface);"/>
                <span style="position:absolute;left:8px;top:5px;font-size:14px;color:var(--on-surface-variant);">🔍</span>
            </div>
        </div>

        <div style="overflow-x:auto;">
            <table class="inventory-table">
                <thead>
                    <tr>
                        <th>Équipement</th>
                        <th>IP / MAC</th>
                        <th>OS / Firmware</th>
                        <th>Uptime</th>
                    </tr>
                </thead>
                <tbody>
                    <!-- Ligne 1: CORE-RTR-01 -->
                    <tr>
                        <td>
                            <div style="display:flex;align-items:center;gap:8px;">
                                <span style="font-size:16px;color:var(--primary);">📟</span>
                                <span style="font-weight:600;color:var(--on-surface);" class="notranslate" translate="no">CORE-RTR-01</span>
                            </div>
                        </td>
                        <td class="notranslate" translate="no">
                            <div class="mono" style="font-size:12px;color:var(--on-surface-variant);">10.0.0.1</div>
                            <div class="mono" style="font-size:10px;color:rgba(189,201,195,0.5);">00:1A:2B:3C:4D:5E</div>
                        </td>
                        <td style="color:var(--on-surface-variant);" class="notranslate" translate="no">Cisco IOS XE 17.3.2</td>
                        <td class="mono notranslate" translate="no" style="color:var(--on-surface-variant);">342d 12h</td>
                    </tr>

                    <!-- Ligne 2: FW-EXT-02 (SÉLECTIONNÉE / CRITIQUE) -->
                    <tr class="selected-row">
                        <td>
                            <div style="display:flex;align-items:center;gap:8px;">
                                <span style="font-size:16px;color:var(--error);">🛡️</span>
                                <span style="font-weight:600;color:var(--on-surface);" class="notranslate" translate="no">FW-EXT-02</span>
                            </div>
                        </td>
                        <td class="notranslate" translate="no">
                            <div class="mono" style="font-size:12px;color:var(--on-surface-variant);">192.168.1.254</div>
                            <div class="mono" style="font-size:10px;color:rgba(189,201,195,0.5);">A1:B2:C3:D4:E5:F6</div>
                        </td>
                        <td style="color:var(--on-surface-variant);" class="notranslate" translate="no">Palo Alto PAN-OS 10.1</td>
                        <td class="mono notranslate" translate="no" style="color:var(--on-surface-variant);">12d 4h</td>
                    </tr>

                    <!-- Ligne 3: SRV-DB-01 -->
                    <tr>
                        <td>
                            <div style="display:flex;align-items:center;gap:8px;">
                                <span style="font-size:16px;color:#d37768;">🖥️</span>
                                <span style="font-weight:600;color:var(--on-surface);" class="notranslate" translate="no">SRV-DB-01</span>
                            </div>
                        </td>
                        <td class="notranslate" translate="no">
                            <div class="mono" style="font-size:12px;color:var(--on-surface-variant);">10.0.10.50</div>
                            <div class="mono" style="font-size:10px;color:rgba(189,201,195,0.5);">11:22:33:44:55:66</div>
                        </td>
                        <td style="color:var(--on-surface-variant);" class="notranslate" translate="no">Ubuntu 22.04 LTS</td>
                        <td class="mono notranslate" translate="no" style="color:var(--on-surface-variant);">45d 8h</td>
                    </tr>

                    <!-- Ligne 4: DIST-SW-A -->
                    <tr>
                        <td>
                            <div style="display:flex;align-items:center;gap:8px;">
                                <span style="font-size:16px;color:var(--primary);">🔌</span>
                                <span style="font-weight:600;color:var(--on-surface);" class="notranslate" translate="no">DIST-SW-A</span>
                            </div>
                        </td>
                        <td class="notranslate" translate="no">
                            <div class="mono" style="font-size:12px;color:var(--on-surface-variant);">10.0.5.1</div>
                            <div class="mono" style="font-size:10px;color:rgba(189,201,195,0.5);">AA:BB:CC:DD:EE:FF</div>
                        </td>
                        <td style="color:var(--on-surface-variant);" class="notranslate" translate="no">ArubaOS-CX 10.08</td>
                        <td class="mono notranslate" translate="no" style="color:var(--on-surface-variant);">120d 2h</td>
                    </tr>
                </tbody>
            </table>
        </div>
        """)

# ── COLONNE DROITE (PANNEAU DE DÉTAIL) ─────────────────────────────────────────
with col_right:

    with card(key="device-detail-card"):
        # Header FW-EXT-02
        st.html("""
        <div style="display:flex;justify-content:space-between;align-items:flex-start;padding-bottom:14px;border-bottom:1px solid rgba(62,73,69,0.3);margin-bottom:16px;">
            <div style="display:flex;align-items:center;gap:12px;">
                <div style="width:40px;height:40px;border-radius:8px;background:rgba(255,180,171,0.15);border:1px solid rgba(255,180,171,0.3);display:flex;align-items:center;justify-content:center;font-size:20px;">🛡️</div>
                <div>
                    <h3 style="font-size:18px;font-weight:700;color:var(--on-surface);margin:0;" class="notranslate" translate="no">FW-EXT-02</h3>
                    <div style="display:flex;align-items:center;gap:6px;margin-top:2px;">
                        <span style="width:6px;height:6px;border-radius:50%;background:var(--error);" class="pulse-critical"></span>
                        <span style="font-family:var(--font-mono);font-size:10px;font-weight:700;color:var(--error);text-transform:uppercase;" class="notranslate" translate="no">CRITIQUE</span>
                    </div>
                </div>
            </div>
            <div style="color:var(--on-surface-variant);font-size:16px;cursor:pointer;padding:4px;" title="Fermer">✕</div>
        </div>

        <!-- Section 1: IDENTIFICATION -->
        <div class="detail-section">
            <div class="detail-sec-title">IDENTIFICATION</div>
            <div style="display:grid;grid-template-columns:1fr 1fr;gap:12px;">
                """ + field("Modèle", "PA-3220") + """
                """ + field("Numéro de série", "0123456789X", mono_value=True) + """
                """ + field("Localisation", "Datacenter Paris - Rack 04") + """
                """ + field("Rôle", "Pare-feu Périmétrique") + """
            </div>
        </div>

        <!-- Section 2: PERFORMANCES (24H) -->
        <div class="detail-section">
            <div class="detail-sec-title">PERFORMANCES (24H)</div>
            
            <div style="margin-bottom:6px;">
                <div style="display:flex;justify-content:space-between;align-items:center;font-size:12px;margin-bottom:4px;">
                    <span style="color:var(--on-surface);">CPU Load</span>
                    <span style="font-family:var(--font-mono);font-weight:700;color:var(--error);" class="notranslate" translate="no">94%</span>
                </div>
            </div>
        </div>
        """)
        mini_bar_chart([30, 35, 32, 40, 55, 70, 80, 88, 92, 94])

        st.html("""
        <div class="detail-section">
            <div style="display:flex;justify-content:space-between;align-items:center;font-size:12px;margin-bottom:4px;">
                <span style="color:var(--on-surface);">Mémoire</span>
                <span style="font-family:var(--font-mono);font-weight:700;color:#d37768;" class="notranslate" translate="no">78%</span>
            </div>
        </div>
        """)
        mini_bar_chart([60, 62, 65, 64, 68, 70, 72, 75, 79, 78])

        st.html("""

        <!-- Section 3: ANOMALIES DE SÉCURITÉ -->
        <div class="detail-section">
            <div class="detail-sec-title" style="color:var(--error);">
                <span style="color:var(--error);">⚠️</span>
                <span>ANOMALIES DE SÉCURITÉ</span>
            </div>
            """ + alert_item("⚡", "DDoS Suspecté (Port 443)", "Il y a 15 min - Règle de blocage automatique échouée") + """
            """ + alert_item("🔑", "Échecs d'authentification admin multiples", "Il y a 4h - Source: 185.xxx.xxx.xxx") + """
        </div>

        <!-- Section 4: NETDEVOPS & SAUVEGARDES -->
        <div class="detail-section">
            <div class="detail-sec-title">NETDEVOPS &amp; SAUVEGARDES</div>
            
            <div style="display:flex;justify-content:space-between;align-items:center;font-size:12px;padding:6px 0;border-bottom:1px solid rgba(255,255,255,0.05);">
                <span style="color:var(--on-surface-variant);">Dernière sauvegarde config</span>
                <span style="color:var(--primary);font-weight:600;" class="notranslate" translate="no">✓ Aujourd'hui, 02:00</span>
            </div>

            <div style="display:flex;justify-content:space-between;align-items:center;font-size:12px;padding:6px 0 0 0;">
                <span style="color:var(--on-surface-variant);">Audit de conformité</span>
                <span style="color:var(--error);font-weight:600;" class="notranslate" translate="no">⚠ Échec (OS obsolète)</span>
            </div>
        </div>

        <!-- Bouton Ouvrir un terminal SSH -->
        <div class="btn-terminal">
            <span>🖥️</span>
            <span>Ouvrir un terminal SSH</span>
        </div>
        """)
