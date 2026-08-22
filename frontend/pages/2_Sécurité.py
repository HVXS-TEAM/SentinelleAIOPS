"""
2_Sécurité.py — Sentinelle AIOps
Pixel-perfect ref : Ecrans_Reference/Securite/code.html + screen.png

Features:
  - Page header: "Sécurité Overview", "Real-time threat detection and posture analysis."
  - Top action buttons: "⚠️ ISOLATE DEVICE" (outline secondary) and "◎ RUN FULL SCAN" (primary solid teal glow)
  - 2-column hero layout [2.2, 1]:
    - Left column:
      - Global Threat Map card: radar_map() with 1 critical & 2 anomaly blips, 3 stat_tile() HUD boxes (ACTIVE VECTORS, EVENTS/SEC, BLOCK RATE)
    - Right column:
      - Security Benchmarks card: donut_gauge(85, "CIS COMPLIANT") + 3 progress_row() (Identity 92% teal, Network 64% red, Data 88% blue)
  - Full-width bottom card:
    - Recent Security Incidents table with severity_pill(), highlighted CRITICAL row, monospaced timestamps & IPs, and action buttons.
"""
import os, sys
import streamlit as st

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from page_template import page_bootstrap
from components import (
    card, mono, radar_map, stat_tile, donut_gauge, progress_row, severity_pill
)

# ── 1. BOOTSTRAP ──────────────────────────────────────────────────────────────
page_bootstrap(
    active="Sécurité",
    page_title="Sécurité Overview",
    search_placeholder="Search threats, IPs, policies..."
)

# ── 2. CSS SPÉCIFIQUE AU MODULE ──────────────────────────────────────────────
st.markdown("""<style>
/* Security Action Header Buttons */
.btn-isolate {
    padding: 8px 18px;
    border-radius: 6px;
    border: 1px solid var(--secondary);
    background: rgba(1, 112, 148, 0.1);
    color: var(--secondary);
    font-family: var(--font-mono);
    font-size: 11px;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 0.05em;
    display: inline-flex;
    align-items: center;
    gap: 8px;
    cursor: pointer;
    transition: background 150ms ease;
}
.btn-isolate:hover { background: rgba(1, 112, 148, 0.25); }

.btn-scan {
    padding: 8px 20px;
    border-radius: 6px;
    border: none;
    background: var(--primary);
    color: var(--on-primary);
    font-family: var(--font-mono);
    font-size: 11px;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 0.05em;
    display: inline-flex;
    align-items: center;
    gap: 8px;
    cursor: pointer;
    box-shadow: 0 0 15px rgba(120, 216, 186, 0.25);
    transition: background 150ms ease;
}
.btn-scan:hover { background: var(--primary-fixed); }

/* Incidents Table */
.incidents-table {
    width: 100%;
    border-collapse: collapse;
    font-family: var(--font-body);
    font-size: 13px;
}
.incidents-table th {
    padding: 10px 14px;
    font-family: var(--font-mono);
    font-size: 10px;
    font-weight: 700;
    color: var(--on-surface-variant);
    text-transform: uppercase;
    letter-spacing: 0.08em;
    background: rgba(25, 28, 30, 0.7);
    border-bottom: 1px solid rgba(255,255,255,0.1);
    text-align: left;
}
.incidents-table td {
    padding: 12px 14px;
    border-bottom: 1px solid rgba(255,255,255,0.05);
    vertical-align: middle;
}
.incidents-table tr:hover { background: rgba(255,255,255,0.03); }
.incidents-table tr.critical-row {
    background: rgba(255, 180, 171, 0.08);
    border-left: 3px solid var(--error);
}

.btn-action-dark {
    padding: 4px 12px;
    background: var(--surface-container);
    border: 1px solid rgba(62,73,69,0.4);
    border-radius: 4px;
    color: var(--on-surface);
    font-family: var(--font-mono);
    font-size: 11px;
    font-weight: 600;
    cursor: pointer;
    transition: all 150ms ease;
}
.btn-action-dark:hover {
    border-color: var(--primary);
    color: var(--primary);
}
</style>""", unsafe_allow_html=True)

# ── 3. EN-TÊTE DE PAGE ────────────────────────────────────────────────────────
with st.container(key="security-page-header"):
    st.html("""
    <div style="display:flex;justify-content:space-between;align-items:flex-end;margin-bottom:24px;">
        <div>
            <h1 style="font-size:28px;font-weight:700;margin:0;color:var(--on-surface);font-family:'IBM Plex Sans', sans-serif;">Sécurité Overview</h1>
            <p style="font-size:14px;color:var(--on-surface-variant);margin:4px 0 0 0;">Real-time threat detection and posture analysis.</p>
        </div>
        <div style="display:flex;gap:12px;">
            <div class="btn-isolate notranslate" translate="no">
                <span>⚠️</span>
                <span>ISOLATE DEVICE</span>
            </div>
            <div class="btn-scan notranslate" translate="no">
                <span>◎</span>
                <span>RUN FULL SCAN</span>
            </div>
        </div>
    </div>
    """)

# ── 4. LIGNE 1 : MAP RADAR & BENCHMARKS (2 COLONNES) ──────────────────────────
col_hero_left, col_hero_right = st.columns([2.2, 1])

# ── CARTE GAUCHE : GLOBAL THREAT MAP ─────────────────────────────────────────
with col_hero_left:
    with card(key="global-threat-map-card"):
        # Header indicator pills
        st.html("""
        <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:14px;">
            <div style="display:flex;align-items:center;gap:8px;">
                <span style="font-size:18px;color:var(--primary);">🌐</span>
                <span class="snt-card-title notranslate" translate="no" style="margin:0;">GLOBAL THREAT MAP</span>
            </div>
            <div style="display:flex;gap:16px;align-items:center;font-family:var(--font-mono);font-size:11px;">
                <div style="display:flex;align-items:center;gap:6px;">
                    <span style="width:8px;height:8px;border-radius:50%;background:var(--error);" class="pulse-critical"></span>
                    <span style="color:var(--on-surface-variant);" class="notranslate" translate="no">Critical (1)</span>
                </div>
                <div style="display:flex;align-items:center;gap:6px;">
                    <span style="width:8px;height:8px;border-radius:50%;background:var(--secondary);"></span>
                    <span style="color:var(--on-surface-variant);" class="notranslate" translate="no">Anomalies (2)</span>
                </div>
            </div>
        </div>
        """)

        # Radar map
        radar_points = [
            {'x': 60, 'y': 30, 'status': 'critical'},
            {'x': 20, 'y': 60, 'status': 'anomaly'},
            {'x': 35, 'y': 45, 'status': 'anomaly'}
        ]
        radar_map(radar_points, view_h=260)

        # 3 Stat tiles under radar
        st.html("""
        <div style="display:grid;grid-template-columns:1fr 1fr 1fr;gap:12px;margin-top:16px;">
            """ + stat_tile("ACTIVE VECTORS", "4", color="red") + """
            """ + stat_tile("EVENTS/SEC", "1,248", color="teal") + """
            """ + stat_tile("BLOCK RATE", "99.8%", color="blue") + """
        </div>
        """)

# ── CARTE DROITE : SECURITY BENCHMARKS ────────────────────────────────────────
with col_hero_right:
    with card(key="security-benchmarks-card"):
        st.html("""
        <div style="display:flex;align-items:center;gap:8px;margin-bottom:16px;">
            <span style="font-size:18px;color:var(--secondary);">📋</span>
            <span class="snt-card-title notranslate" translate="no" style="margin:0;">SECURITY BENCHMARKS</span>
        </div>
        """)

        # Donut Gauge
        donut_gauge(85, "CIS COMPLIANT")

        # Progress rows
        st.markdown('<div style="margin-top:20px;"></div>', unsafe_allow_html=True)
        progress_row("Identity & Access", 92, color="var(--primary)")
        progress_row("Network Config", 64, color="var(--error)")
        progress_row("Data Protection", 88, color="var(--secondary)")

# ── 5. LIGNE 2 : RECENT SECURITY INCIDENTS (PLEINE LARGEUR) ───────────────────
with card(key="recent-incidents-card"):
    st.html("""
    <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:14px;">
        <div style="display:flex;align-items:center;gap:8px;">
            <span style="font-size:18px;color:var(--error);">⚠️</span>
            <span class="snt-card-title notranslate" translate="no" style="margin:0;">RECENT SECURITY INCIDENTS</span>
        </div>
        <div style="font-family:var(--font-mono);font-size:11px;font-weight:700;color:var(--primary);cursor:pointer;" class="notranslate" translate="no">View All Logs</div>
    </div>

    <div style="overflow-x:auto;">
        <table class="incidents-table">
            <thead>
                <tr>
                    <th>SEVERITY</th>
                    <th>TIMESTAMP</th>
                    <th>TYPE</th>
                    <th>SOURCE IP</th>
                    <th>TARGET</th>
                    <th style="text-align:right;">ACTION</th>
                </tr>
            </thead>
            <tbody>
                <!-- Row 1: CRITICAL -->
                <tr class="critical-row">
                    <td>""" + severity_pill("critical") + """</td>
                    <td class="mono notranslate" translate="no" style="color:var(--on-surface-variant);">14:32:01 UTC</td>
                    <td style="font-weight:600;color:var(--on-surface);" class="notranslate" translate="no">IP Spoofing Attempt</td>
                    <td class="mono notranslate" translate="no" style="color:var(--on-surface-variant);">192.168.x.x (Spoofed)</td>
                    <td style="color:var(--on-surface-variant);" class="notranslate" translate="no">Core Router 01</td>
                    <td style="text-align:right;">
                        <button class="btn-action-dark notranslate" translate="no">Investigate</button>
                    </td>
                </tr>

                <!-- Row 2: HIGH -->
                <tr>
                    <td>""" + severity_pill("high") + """</td>
                    <td class="mono notranslate" translate="no" style="color:var(--on-surface-variant);">14:15:44 UTC</td>
                    <td style="font-weight:600;color:var(--on-surface);" class="notranslate" translate="no">Brute Force Detection</td>
                    <td class="mono notranslate" translate="no" style="color:var(--on-surface-variant);">45.33.12.x</td>
                    <td style="color:var(--on-surface-variant);" class="notranslate" translate="no">Auth Gateway</td>
                    <td style="text-align:right;">
                        <span class="mono notranslate" translate="no" style="color:var(--primary);font-size:12px;font-weight:700;display:inline-flex;align-items:center;gap:4px;">
                            <span>✓</span> Blocked
                        </span>
                    </td>
                </tr>

                <!-- Row 3: MEDIUM -->
                <tr>
                    <td>""" + severity_pill("medium") + """</td>
                    <td class="mono notranslate" translate="no" style="color:var(--on-surface-variant);">13:59:12 UTC</td>
                    <td style="font-weight:600;color:var(--on-surface);" class="notranslate" translate="no">Unusual Traffic Volume</td>
                    <td class="mono notranslate" translate="no" style="color:var(--on-surface-variant);">Internal Subnet B</td>
                    <td style="color:var(--on-surface-variant);" class="notranslate" translate="no">DB Cluster 03</td>
                    <td style="text-align:right;">
                        <button class="btn-action-dark notranslate" translate="no">Review</button>
                    </td>
                </tr>

                <!-- Row 4: MEDIUM -->
                <tr>
                    <td>""" + severity_pill("medium") + """</td>
                    <td class="mono notranslate" translate="no" style="color:var(--on-surface-variant);">13:45:00 UTC</td>
                    <td style="font-weight:600;color:var(--on-surface);" class="notranslate" translate="no">Suspicious API Calls</td>
                    <td class="mono notranslate" translate="no" style="color:var(--on-surface-variant);">185.20.x.x</td>
                    <td style="color:var(--on-surface-variant);" class="notranslate" translate="no">Public API v2</td>
                    <td style="text-align:right;">
                        <button class="btn-action-dark notranslate" translate="no">Review</button>
                    </td>
                </tr>
            </tbody>
        </table>
    </div>
    """)
