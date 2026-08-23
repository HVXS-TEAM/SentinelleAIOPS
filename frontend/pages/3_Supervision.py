"""
3_Supervision.py — Sentinelle AIOps
Pixel-perfect ref : Ecrans_Reference/Supervision/code.html + screen.png

Features:
  - Breadcrumb: "Home > Supervision"
  - Page header: "Supervision & Analyses Prédictives", "Analyse de santé et prédiction de pannes en temps réel des équipements critiques."
  - 3-column top row [2, 1.3, 1.3]:
    - Col 1: Failure Prediction Hero card (salmon border, "PRÉDICTION CRITIQUE IMMINENTE", "FW-EXT-02 : Saturation disque estimée", Time-To-Failure 4j 06h, "Planifier Intervention" button)
    - Col 2: Configuration Alertes card (Seuil d'Avertissement 80%, Seuil Critique 95% with native sliders, "Enregistrer" link)
    - Col 3: Urgence Maintenance card (4x maintenance_item for FW-EXT-02, CORE-RTR-01, SRV-APP-14, SW-ACC-4B)
  - Full-width bottom section:
    - Projections des Télémétries Systèmes card (Legend: Historique vs Zone de prédiction +48h, FW-EXT-02 selectbox)
    - Grid 2x2 of telemetry charts using trend_chart() for CPU Utilization, RAM Usage, Disk I/O & Fill (with 100% Saturation line), and Network Traffic.
"""
import os, sys
import streamlit as st

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from page_template import page_bootstrap
from components import (
    card, badge, mono, trend_chart, maintenance_item
)

# ── 1. BOOTSTRAP ──────────────────────────────────────────────────────────────
# ── Garde d'authentification ─────────────────────────────────────────────────
if not st.session_state.get("authenticated", False):
    st.switch_page("app.py")

page_bootstrap(
    active="Supervision",
    page_title="Supervision & Analyses Prédictives",
    search_placeholder="Search hosts, metrics, logs..."
)

# ── 2. CSS SPÉCIFIQUE AU MODULE ──────────────────────────────────────────────
st.markdown("""<style>
/* Supervision Custom Button */
.btn-intervention {
    background-color: var(--predictive-accent);
    color: var(--on-predictive-accent);
    padding: 10px 18px;
    border-radius: 8px;
    border: none;
    font-family: var(--font-ui);
    font-size: 13px;
    font-weight: 700;
    display: inline-flex;
    align-items: center;
    gap: 8px;
    cursor: pointer;
    transition: filter 150ms ease;
}
.btn-intervention:hover {
    filter: brightness(1.1);
}

/* Legend items */
.legend-line-solid {
    display: inline-block;
    width: 16px;
    height: 2px;
    background: var(--primary);
    vertical-align: middle;
    margin-right: 6px;
}
.legend-line-dashed {
    display: inline-block;
    width: 16px;
    height: 0px;
    border-top: 2px dashed var(--predictive-accent);
    vertical-align: middle;
    margin-right: 6px;
}
</style>""", unsafe_allow_html=True)

# ── 3. BREADCRUMB & EN-TÊTE DE PAGE ───────────────────────────────────────────
with st.container(key="supervision-page-header"):
    st.html("""
    <div style="margin-bottom:16px;">
        <div style="font-size:12px;color:var(--on-surface-variant);margin-bottom:6px;display:flex;align-items:center;gap:6px;">
            <span style="color:var(--on-surface-variant);cursor:pointer;">Home</span>
            <span>&gt;</span>
            <span style="font-weight:600;color:var(--on-surface);" class="notranslate" translate="no">Supervision</span>
        </div>
        <h1 style="font-size:28px;font-weight:700;margin:0;color:var(--on-surface);font-family:'IBM Plex Sans', sans-serif;">Supervision &amp; Analyses Prédictives</h1>
        <p style="font-size:14px;color:var(--on-surface-variant);margin:4px 0 0 0;">Analyse de santé et prédiction de pannes en temps réel des équipements critiques.</p>
    </div>
    """)

# ── 4. LIGNE À 3 COLONNES : PRÉDICTION, CONFIG, MAINTENANCE ───────────────────
c1, c2, c3 = st.columns([2, 1.3, 1.3])

# ── COLONNE 1 : PRÉDICTION CRITIQUE IMMINENTE ─────────────────────────────────
with c1:
    with card(key="hero-prediction-card"):
        # Custom border style wrapped via CSS class
        st.html("""
        <div style="border:1px solid var(--predictive-accent);box-shadow:0 0 15px rgba(255,180,167,0.15);background:var(--surface-container);border-radius:12px;padding:20px;display:flex;flex-direction:column;justify-between;min-height:240px;">
            <div>
                <div style="display:flex;align-items:center;gap:8px;margin-bottom:8px;">
                    <span style="font-size:16px;color:var(--predictive-accent);">⚠️</span>
                    <span style="font-family:var(--font-mono);font-size:11px;font-weight:700;color:var(--predictive-accent);letter-spacing:0.08em;text-transform:uppercase;" class="notranslate" translate="no">PRÉDICTION CRITIQUE IMMINENTE</span>
                </div>
                <h3 style="font-size:20px;font-weight:700;color:var(--on-surface);margin:0 0 6px 0;" class="notranslate" translate="no">FW-EXT-02 : Saturation disque estimée</h3>
                <p style="font-size:13px;color:var(--on-surface-variant);margin:0;line-height:1.5;">Le taux d'écriture des logs indique un remplissage à 100% imminent. Action requise.</p>
            </div>

            <div style="border-top:1px solid rgba(255,180,167,0.2);padding-top:16px;margin-top:16px;display:flex;justify-content:space-between;align-items:flex-end;flex-wrap:wrap;gap:12px;">
                <div>
                    <div style="font-size:11px;color:var(--on-surface-variant);font-family:var(--font-mono);margin-bottom:4px;">Time-To-Failure Estimé</div>
                    <div style="font-family:var(--font-mono);font-size:28px;font-weight:700;color:var(--predictive-accent);line-height:1;" class="notranslate" translate="no">
                        4 <span style="font-size:14px;font-weight:500;">jours</span> 06 <span style="font-size:14px;font-weight:500;">heures</span>
                    </div>
                </div>
                <div class="btn-intervention notranslate" translate="no">
                    <span>⚡</span>
                    <span>Planifier Intervention</span>
                </div>
            </div>
        </div>
        """)

# ── COLONNE 2 : CONFIGURATION ALERTES ─────────────────────────────────────────
with c2:
    with card(key="config-alertes-card"):
        st.html("""
        <div style="display:flex;align-items:center;gap:8px;margin-bottom:16px;border-bottom:1px solid rgba(62,73,69,0.3);padding-bottom:10px;">
            <span style="font-size:16px;color:var(--on-surface-variant);">⚙</span>
            <span class="snt-card-title notranslate" translate="no" style="margin:0;">Configuration Alertes</span>
        </div>
        """)

        # Seuil Avertissement Slider
        col_warn_txt, col_warn_badge = st.columns([3, 1])
        with col_warn_txt:
            st.markdown('<span style="font-size:12px;color:var(--on-surface-variant);">Seuil d\'Avertissement</span>', unsafe_allow_html=True)
        with col_warn_badge:
            st.markdown('<div style="text-align:right;"><span style="font-family:var(--font-mono);font-size:11px;font-weight:700;color:var(--predictive-accent);background:rgba(255,180,167,0.15);padding:2px 8px;border-radius:4px;border:1px solid rgba(255,180,167,0.3);" class="notranslate" translate="no">80%</span></div>', unsafe_allow_html=True)
        
        st.slider("Seuil Avertissement", 0, 100, 80, key="slider_warn", label_visibility="collapsed")

        st.markdown('<div style="height:12px;"></div>', unsafe_allow_html=True)

        # Seuil Critique Slider
        col_crit_txt, col_crit_badge = st.columns([3, 1])
        with col_crit_txt:
            st.markdown('<span style="font-size:12px;color:var(--on-surface-variant);">Seuil Critique</span>', unsafe_allow_html=True)
        with col_crit_badge:
            st.markdown('<div style="text-align:right;"><span style="font-family:var(--font-mono);font-size:11px;font-weight:700;color:var(--error);background:rgba(255,180,171,0.15);padding:2px 8px;border-radius:4px;border:1px solid rgba(255,180,171,0.3);" class="notranslate" translate="no">95%</span></div>', unsafe_allow_html=True)
        
        st.slider("Seuil Critique", 0, 100, 95, key="slider_crit", label_visibility="collapsed")

        # Enregistrer link
        st.html("""
        <div style="text-align:right;margin-top:16px;">
            <span style="font-family:var(--font-mono);font-size:12px;font-weight:700;color:var(--primary);cursor:pointer;" class="notranslate" translate="no">Enregistrer</span>
        </div>
        """)

# ── COLONNE 3 : URGENCE MAINTENANCE ───────────────────────────────────────────
with c3:
    with card(key="urgence-maintenance-card"):
        st.html("""
        <div style="display:flex;align-items:center;gap:8px;margin-bottom:16px;border-bottom:1px solid rgba(62,73,69,0.3);padding-bottom:10px;">
            <span style="font-size:16px;color:var(--error);">!</span>
            <span class="snt-card-title notranslate" translate="no" style="margin:0;">Urgence Maintenance</span>
        </div>

        <div>
            """ + maintenance_item("FW-EXT-02", "CRITIQUE", "Saturation disque estimée", "4j 06h", color="var(--predictive-accent)") + """
            """ + maintenance_item("CORE-RTR-01", "ÉLEVÉE", "Memory Leak (Pool A)", "12j 14h", color="var(--secondary)") + """
            """ + maintenance_item("SRV-APP-14", "MOYENNE", "Usure ventilateur CPU 2", "24j 00h", color="var(--secondary)") + """
            """ + maintenance_item("SW-ACC-4B", "FAIBLE", "Anomalie mineure I/O", "> 60j", color="var(--primary)") + """
        </div>
        """)

# ── 5. PROJECTIONS DES TÉLÉMÉTRIES SYSTÈMES (GRILLE 2x2) ───────────────────────
with card(key="projections-telemetrie-card"):
    # Header with title, legend, and selectbox
    col_proj_title, col_proj_controls = st.columns([1.5, 1])
    with col_proj_title:
        st.markdown('<div class="snt-card-title notranslate" translate="no" style="margin:0;">Projections des Télémétries Systèmes</div>', unsafe_allow_html=True)
    with col_proj_controls:
        c_leg, c_sel = st.columns([2, 1])
        with c_leg:
            st.html("""
            <div style="font-size:11px;color:var(--on-surface-variant);display:flex;align-items:center;gap:12px;justify-content:flex-end;height:100%;">
                <div><span class="legend-line-solid"></span>Historique</div>
                <div><span class="legend-line-dashed"></span>Zone de prédiction (+48h)</div>
            </div>
            """)
        with c_sel:
            st.selectbox("Equipement", ["FW-EXT-02", "Cluster Core (All)"], key="select_equip", label_visibility="collapsed")

    st.markdown('<div style="height:16px;"></div>', unsafe_allow_html=True)

    # Grid 2x2 of charts
    row1_c1, row1_c2 = st.columns(2)
    with row1_c1:
        with card(key="chart-cpu"):
            st.html("""
            <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:8px;">
                <span style="font-size:13px;font-weight:600;color:var(--on-surface);">CPU Utilization</span>
                <span style="font-family:var(--font-mono);font-size:12px;font-weight:700;color:var(--primary);" class="notranslate" translate="no">62.4%</span>
            </div>
            """)
            trend_chart(
                history=[50, 52, 48, 55, 60, 58, 62.4],
                forecast=[64, 66, 68, 70, 72],
                color="var(--primary)"
            )

    with row1_c2:
        with card(key="chart-ram"):
            st.html("""
            <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:8px;">
                <span style="font-size:13px;font-weight:600;color:var(--on-surface);">RAM Usage</span>
                <span style="font-family:var(--font-mono);font-size:12px;font-weight:700;color:var(--predictive-accent);" class="notranslate" translate="no">88.1%</span>
            </div>
            """)
            trend_chart(
                history=[40, 45, 55, 65, 75, 82, 88.1],
                forecast=[90, 92, 94, 96, 97],
                color="var(--primary)"
            )

    st.markdown('<div style="height:12px;"></div>', unsafe_allow_html=True)

    row2_c1, row2_c2 = st.columns(2)
    with row2_c1:
        with card(key="chart-disk"):
            st.html("""
            <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:8px;">
                <span style="font-size:13px;font-weight:600;color:var(--predictive-accent);" class="notranslate" translate="no">⚠️ Disk I/O &amp; Fill</span>
                <span style="font-family:var(--font-mono);font-size:12px;font-weight:700;color:var(--predictive-accent);" class="notranslate" translate="no">96.8%</span>
            </div>
            """)
            trend_chart(
                history=[50, 58, 66, 75, 84, 90, 96.8],
                forecast=[97.5, 98.5, 99.2, 100],
                color="var(--primary)",
                threshold=100,
                threshold_label="100% Saturation"
            )

    with row2_c2:
        with card(key="chart-net"):
            st.html("""
            <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:8px;">
                <span style="font-size:13px;font-weight:600;color:var(--on-surface);">Network Traffic</span>
                <span style="font-family:var(--font-mono);font-size:12px;font-weight:700;color:var(--secondary);" class="notranslate" translate="no">1.2 Gbps</span>
            </div>
            """)
            trend_chart(
                history=[20, 80, 30, 95, 40, 70, 60],
                forecast=[55, 50, 48, 45],
                color="var(--secondary)"
            )
