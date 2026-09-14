"""
3_Supervision.py — Sentinelle AIOps
Pixel-perfect ref : Ecrans_Reference/Supervision/code.html + screen.png
Sources : DESIGN.md (tokens) + code.html (DOM & layout) + screen.png (vérification visuelle)
"""
import os, sys
from pathlib import Path
import streamlit as st

_LOGO_PATH = str(Path(__file__).parent.parent / "static" / "logo.png")

st.set_page_config(
    page_title="Supervision & Analyses Prédictives — Sentinelle AIOps",
    page_icon=_LOGO_PATH,
    layout="wide",
    initial_sidebar_state="expanded",
)

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from page_template import page_bootstrap
from components import trend_chart

# ── Garde d'authentification ─────────────────────────────────────────────────
if not st.session_state.get("authenticated", False):
    st.switch_page("app.py")

page_bootstrap(
    active="Supervision",
    page_title="Supervision & Analyses Prédictives",
    search_placeholder="Search hosts, metrics, logs (Cmd+K)..."
)

# ── STYLES DÉDIÉS SUPERVISION ────────────────────────────────────────────────
st.html("""
<style>
/* Carte Critique de Prédiction */
.sup-card-critical {
    background-color: var(--surface-container, #1c211e);
    border: 1px solid var(--error, #ffb4ab);
    box-shadow: 0 0 15px rgba(255, 180, 171, 0.15);
    border-radius: 12px;
    padding: 24px;
    position: relative;
    overflow: hidden;
    display: flex;
    flex-direction: column;
    justify-content: space-between;
    min-height: 230px;
}
.sup-glow-bg {
    position: absolute;
    top: -40px; right: -40px;
    width: 160px; height: 160px;
    background: rgba(255, 180, 171, 0.18);
    border-radius: 50%;
    filter: blur(40px);
    pointer-events: none;
}
.btn-intervention {
    background-color: var(--error, #ffb4ab);
    color: var(--on-error, #690005);
    padding: 8px 18px;
    border-radius: 8px;
    border: none;
    font-family: var(--font-body, 'Inter', sans-serif);
    font-size: 13px;
    font-weight: 700;
    display: inline-flex;
    align-items: center;
    gap: 8px;
    cursor: pointer;
    text-decoration: none;
    transition: background-color 0.15s ease;
}
.btn-intervention:hover {
    background-color: #ffdad6;
}

/* Carte Configuration Alertes */
.sup-card-config {
    background-color: var(--surface-container, #1c211e);
    border: 1px solid rgba(255, 255, 255, 0.08);
    border-radius: 12px;
    padding: 20px;
    display: flex;
    flex-direction: column;
    justify-content: space-between;
    min-height: 230px;
}
.config-header {
    font-family: var(--font-headline, 'Inter', sans-serif);
    font-size: 15px;
    font-weight: 600;
    color: var(--on-surface, #dfe4e0);
    display: flex;
    align-items: center;
    gap: 8px;
    padding-bottom: 12px;
    border-bottom: 1px solid rgba(255, 255, 255, 0.08);
    margin-bottom: 16px;
}

/* Carte Projections Télémétriques */
.sup-card-projections {
    background-color: var(--surface-container, #1c211e);
    border: 1px solid rgba(255, 255, 255, 0.08);
    border-radius: 12px;
    padding: 20px;
}
.chart-box {
    background-color: var(--surface-container-low, #181d1b);
    border: 1px solid rgba(255, 255, 255, 0.08);
    border-radius: 8px;
    padding: 14px;
    display: flex;
    flex-direction: column;
}
.chart-box-critical {
    background-color: var(--surface-container-low, #181d1b);
    border: 1px solid rgba(255, 180, 171, 0.4);
    box-shadow: inset 0 0 20px rgba(255, 180, 171, 0.05);
    border-radius: 8px;
    padding: 14px;
    display: flex;
    flex-direction: column;
}

/* Carte Colonne Droite : Urgence Maintenance */
.sup-card-urgency {
    background-color: var(--surface-container, #1c211e);
    border: 1px solid rgba(255, 255, 255, 0.08);
    border-radius: 12px;
    padding: 20px;
    display: flex;
    flex-direction: column;
    height: 100%;
}
.urgency-header {
    font-family: var(--font-headline, 'Inter', sans-serif);
    font-size: 15px;
    font-weight: 600;
    color: var(--on-surface, #dfe4e0);
    display: flex;
    align-items: center;
    gap: 8px;
    padding-bottom: 12px;
    border-bottom: 1px solid rgba(255, 255, 255, 0.08);
    margin-bottom: 14px;
}
.urgency-item {
    background-color: var(--surface-container-high, #262b29);
    border-radius: 0 8px 8px 0;
    padding: 12px 14px;
    margin-bottom: 10px;
    cursor: pointer;
    transition: background-color 0.15s ease;
}
.urgency-item:hover {
    background-color: var(--surface-container-highest);
}
</style>
""")

# ── EN-TÊTE DE PAGE ──────────────────────────────────────────────────────────
st.html(
    """
    <div style="margin-bottom: 20px;">
        <div style="display: flex; align-items: center; gap: 6px; font-family: var(--font-body); font-size: 12px; color: var(--on-surface-variant, #bdc9c3); margin-bottom: 6px;">
            <span style="cursor: pointer;">Home</span>
            <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><polyline points="9 18 15 12 9 6"/></svg>
            <span style="color: var(--on-surface, #dfe4e0); font-weight: 600;">Supervision</span>
        </div>
        <div style="font-family: var(--font-headline, 'Inter'); font-size: 28px; font-weight: 700; color: var(--on-surface, #dfe4e0); line-height: 1.2;">
            Supervision &amp; Analyses Prédictives
        </div>
        <div style="font-family: var(--font-body, 'Inter'); font-size: 14px; color: var(--on-surface-variant, #bdc9c3); margin-top: 4px;">
            Analyse de santé et prédiction de pannes en temps réel des équipements critiques.
        </div>
    </div>
    """
)

# ── DISPOSITION EN 2 GRANDES COLONNES (9/12 et 3/12) ─────────────────────────
col_main, col_side = st.columns([2.8, 1.0])

with col_main:
    # ── LIGNE SUPÉRIEURE : HERO PREDICTION (2/3) + CONFIG ALERTES (1/3) ───────
    c_hero, c_conf = st.columns([1.8, 1.0])
    
    with c_hero:
        st.html(
            """
            <div class="sup-card-critical">
                <div class="sup-glow-bg"></div>
                <div style="position: relative; z-index: 10;">
                    <div style="display: flex; align-items: center; gap: 6px; margin-bottom: 6px;">
                        <svg width="15" height="15" viewBox="0 0 24 24" fill="#ffb4ab" stroke="#ffb4ab" stroke-width="1">
                            <path d="M10.29 3.86L1.82 18a2 2 0 0 0 1.71 3h16.94a2 2 0 0 0 1.71-3L13.71 3.86a2 2 0 0 0-3.42 0z"/>
                            <line x1="12" y1="9" x2="12" y2="13" stroke="#690005" stroke-width="2"/>
                            <line x1="12" y1="17" x2="12.01" y2="17" stroke="#690005" stroke-width="2"/>
                        </svg>
                        <span style="font-family: var(--font-mono); font-size: 11px; font-weight: 700; color: var(--error, #ffb4ab); letter-spacing: 0.08em; text-transform: uppercase;">
                            PRÉDICTION CRITIQUE IMMINENTE
                        </span>
                    </div>
                    <div style="font-family: var(--font-headline); font-size: 20px; font-weight: 700; color: var(--on-surface, #dfe4e0); margin-bottom: 4px;">
                        FW-EXT-02 : Saturation disque estimée
                    </div>
                    <div style="font-family: var(--font-body); font-size: 13px; color: var(--on-surface-variant, #bdc9c3); line-height: 1.4;">
                        Le taux d'écriture des logs indique un remplissage à 100% imminent. Action requise.
                    </div>
                </div>

                <div style="position: relative; z-index: 10; border-top: 1px solid rgba(255, 180, 171, 0.2); padding-top: 14px; margin-top: 16px; display: flex; justify-content: space-between; align-items: flex-end; flex-wrap: wrap; gap: 12px;">
                    <div>
                        <div style="font-family: var(--font-body); font-size: 12px; color: var(--on-surface-variant, #bdc9c3); margin-bottom: 2px;">
                            Time-To-Failure Estimé
                        </div>
                        <div style="font-family: var(--font-mono, 'IBM Plex Sans'); font-size: 28px; font-weight: 700; color: var(--error, #ffb4ab); line-height: 1.1;">
                            4 <span style="font-size: 18px; font-weight: 500; opacity: 0.85;">jours</span> 06 <span style="font-size: 18px; font-weight: 500; opacity: 0.85;">heures</span>
                        </div>
                    </div>
                    <button class="btn-intervention">
                        <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5">
                            <path d="M14.7 6.3a1 1 0 0 0 0 1.4l1.6 1.6a1 1 0 0 0 1.4 0l3.77-3.77a6 6 0 0 1-7.94 7.94l-6.91 6.91a2.12 2.12 0 0 1-3-3l6.91-6.91a6 6 0 0 1 7.94-7.94l-3.76 3.76z"/>
                        </svg>
                        Planifier Intervention
                    </button>
                </div>
            </div>
            """
        )

    with c_conf:
        st.html(
            """
            <div class="sup-card-config">
                <div class="config-header">
                    <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                        <line x1="4" y1="21" x2="4" y2="14"/><line x1="4" y1="10" x2="4" y2="3"/>
                        <line x1="12" y1="21" x2="12" y2="12"/><line x1="12" y1="8" x2="12" y2="3"/>
                        <line x1="20" y1="21" x2="20" y2="16"/><line x1="20" y1="12" x2="20" y2="3"/>
                        <line x1="1" y1="14" x2="7" y2="14"/><line x1="9" y1="8" x2="15" y2="8"/><line x1="17" y1="16" x2="23" y2="16"/>
                    </svg>
                    Configuration Alertes
                </div>

                <div style="display: flex; flex-direction: column; gap: 16px; justify-content: center; flex: 1;">
                    <div>
                        <div style="display: flex; justify-content: space-between; align-items: center; font-size: 12px; margin-bottom: 6px;">
                            <span style="color: var(--on-surface-variant, #bdc9c3);">Seuil d'Avertissement</span>
                            <span style="font-family: var(--font-mono); font-size: 11px; font-weight: 700; color: #d37768; background: rgba(211, 119, 104, 0.15); padding: 1px 6px; border-radius: 4px; border: 1px solid rgba(211, 119, 104, 0.3);">80%</span>
                        </div>
                        <div style="position: relative; width: 100%; height: 4px; background: var(--surface-container-highest); border-radius: 2px;">
                            <div style="position: absolute; left: 0; top: 0; height: 100%; width: 80%; background: #d37768; border-radius: 2px;"></div>
                            <div style="position: absolute; top: 50%; left: 80%; transform: translate(-50%, -50%); width: 12px; height: 12px; border-radius: 50%; background: #d37768; border: 2px solid var(--surface-container); cursor: pointer;"></div>
                        </div>
                    </div>

                    <div>
                        <div style="display: flex; justify-content: space-between; align-items: center; font-size: 12px; margin-bottom: 6px;">
                            <span style="color: var(--on-surface-variant, #bdc9c3);">Seuil Critique</span>
                            <span style="font-family: var(--font-mono); font-size: 11px; font-weight: 700; color: #ffb4ab; background: rgba(255, 180, 171, 0.15); padding: 1px 6px; border-radius: 4px; border: 1px solid rgba(255, 180, 171, 0.3);">95%</span>
                        </div>
                        <div style="position: relative; width: 100%; height: 4px; background: var(--surface-container-highest); border-radius: 2px;">
                            <div style="position: absolute; left: 0; top: 0; height: 100%; width: 95%; background: #ffb4ab; border-radius: 2px;"></div>
                            <div style="position: absolute; top: 50%; left: 95%; transform: translate(-50%, -50%); width: 12px; height: 12px; border-radius: 50%; background: #ffb4ab; border: 2px solid var(--surface-container); cursor: pointer;"></div>
                        </div>
                    </div>
                </div>

                <div style="text-align: right; padding-top: 10px; border-top: 1px solid rgba(255, 255, 255, 0.08); margin-top: 10px;">
                    <a style="font-family: var(--font-body); font-size: 13px; font-weight: 600; color: var(--primary, #78d8ba); cursor: pointer; text-decoration: none;">
                        Enregistrer
                    </a>
                </div>
            </div>
            """
        )

    st.html("<div style='height: 16px;'></div>")

    # ── LIGNE INFÉRIEURE : PROJECTIONS DES TÉLÉMÉTRIES (GRILLE 2x2) ───────────
    st.html(
        """
        <div class="sup-card-projections">
            <div style="display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 12px; margin-bottom: 16px;">
                <div style="font-family: var(--font-headline); font-size: 16px; font-weight: 600; color: var(--on-surface, #dfe4e0);">
                    Projections des Télémétries Systèmes
                </div>
                <div style="display: flex; align-items: center; gap: 16px; font-size: 12px;">
                    <div style="display: flex; align-items: center; gap: 6px; color: var(--on-surface-variant, #bdc9c3);">
                        <span style="width: 14px; height: 2px; background: var(--primary, #78d8ba); border-radius: 1px;"></span>
                        Historique
                    </div>
                    <div style="display: flex; align-items: center; gap: 6px; color: var(--on-surface-variant, #bdc9c3);">
                        <span style="width: 14px; height: 0px; border-top: 2px dashed #d37768;"></span>
                        Zone de prédiction (+48h)
                    </div>
                    <select style="background: var(--surface-container-high); border: 1px solid var(--outline); color: var(--on-surface); font-size: 12px; border-radius: 4px; padding: 4px 8px; outline: none;">
                        <option>FW-EXT-02</option>
                        <option>Cluster Core (All)</option>
                    </select>
                </div>
            </div>
        """
    )

    row1_c1, row1_c2 = st.columns(2)
    with row1_c1:
        with st.container():
            st.html(
                """
                <div class="chart-box">
                    <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 6px;">
                        <span style="font-family: var(--font-body); font-size: 13px; font-weight: 600; color: var(--on-surface, #dfe4e0);">CPU Utilization</span>
                        <span style="font-family: var(--font-mono); font-size: 12px; font-weight: 700; color: var(--primary, #78d8ba);">62.4%</span>
                    </div>
                """
            )
            trend_chart(
                history=[50, 52, 48, 55, 60, 58, 62.4],
                forecast=[64, 66, 68, 70, 72],
                color="#78d8ba",
                view_w=350,
                view_h=110,
            )
            st.html("</div>")

    with row1_c2:
        with st.container():
            st.html(
                """
                <div class="chart-box">
                    <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 6px;">
                        <span style="font-family: var(--font-body); font-size: 13px; font-weight: 600; color: var(--on-surface, #dfe4e0);">RAM Usage</span>
                        <span style="font-family: var(--font-mono); font-size: 12px; font-weight: 700; color: #d37768;">88.1%</span>
                    </div>
                """
            )
            trend_chart(
                history=[40, 45, 55, 65, 75, 82, 88.1],
                forecast=[90, 92, 94, 96, 97],
                color="#78d8ba",
                view_w=350,
                view_h=110,
            )
            st.html("</div>")

    st.html("<div style='height: 10px;'></div>")

    row2_c1, row2_c2 = st.columns(2)
    with row2_c1:
        with st.container():
            st.html(
                """
                <div class="chart-box-critical">
                    <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 6px;">
                        <span style="font-family: var(--font-body); font-size: 13px; font-weight: 600; color: var(--error, #ffb4ab); display: flex; align-items: center; gap: 6px;">
                            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5">
                                <path d="M10.29 3.86L1.82 18a2 2 0 0 0 1.71 3h16.94a2 2 0 0 0 1.71-3L13.71 3.86a2 2 0 0 0-3.42 0z"/>
                                <line x1="12" y1="9" x2="12" y2="13"/>
                                <line x1="12" y1="17" x2="12.01" y2="17"/>
                            </svg>
                            Disk I/O &amp; Fill
                        </span>
                        <span style="font-family: var(--font-mono); font-size: 12px; font-weight: 700; color: var(--error, #ffb4ab);">96.8%</span>
                    </div>
                """
            )
            trend_chart(
                history=[50, 58, 66, 75, 84, 90, 96.8],
                forecast=[97.5, 98.5, 99.2, 100],
                color="#78d8ba",
                threshold=100,
                threshold_label="100% Saturation",
                view_w=350,
                view_h=110,
            )
            st.html("</div>")

    with row2_c2:
        with st.container():
            st.html(
                """
                <div class="chart-box">
                    <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 6px;">
                        <span style="font-family: var(--font-body); font-size: 13px; font-weight: 600; color: var(--on-surface, #dfe4e0);">Network Traffic</span>
                        <span style="font-family: var(--font-mono); font-size: 12px; font-weight: 700; color: var(--primary, #78d8ba);">1.2 Gbps</span>
                    </div>
                """
            )
            trend_chart(
                history=[20, 80, 30, 95, 40, 70, 60],
                forecast=[55, 50, 48, 45],
                color="#81d0f8",
                view_w=350,
                view_h=110,
            )
            st.html("</div>")

    st.html("</div>")

with col_side:
    # ── COLONNE DROITE : URGENCE MAINTENANCE ───────────────────────────────────
    st.html(
        """
        <div class="sup-card-urgency">
            <div class="urgency-header">
                <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="#ffb4ab" stroke-width="2.5">
                    <circle cx="12" cy="12" r="10"/>
                    <line x1="12" y1="8" x2="12" y2="12"/>
                    <line x1="12" y1="16" x2="12.01" y2="16"/>
                </svg>
                Urgence Maintenance
            </div>

            <div style="display: flex; flex-direction: column; gap: 10px;">
                <!-- 1. FW-EXT-02 (CRITIQUE) -->
                <div class="urgency-item" style="border-left: 4px solid #ffb4ab;">
                    <div style="display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 2px;">
                        <span style="font-family: var(--font-mono); font-size: 13px; font-weight: 600; color: #dfe4e0;">FW-EXT-02</span>
                        <span style="font-family: var(--font-mono); font-size: 10px; font-weight: 700; color: #ffb4ab; background: rgba(255, 180, 171, 0.15); padding: 1px 6px; border-radius: 4px; border: 1px solid rgba(255, 180, 171, 0.3); letter-spacing: 0.05em;">CRITIQUE</span>
                    </div>
                    <div style="font-family: var(--font-body); font-size: 12px; color: var(--on-surface-variant, #bdc9c3); margin-bottom: 6px;">
                        Saturation disque estimée
                    </div>
                    <div style="display: flex; align-items: center; gap: 4px; font-family: var(--font-mono); font-size: 12px; color: #ffb4ab;">
                        <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><circle cx="12" cy="12" r="10"/><polyline points="12 6 12 12 16 14"/></svg>
                        <span>4j 06h</span>
                    </div>
                </div>

                <!-- 2. CORE-RTR-01 (ÉLEVÉE) -->
                <div class="urgency-item" style="border-left: 4px solid #d37768;">
                    <div style="display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 2px;">
                        <span style="font-family: var(--font-mono); font-size: 13px; font-weight: 600; color: #dfe4e0;">CORE-RTR-01</span>
                        <span style="font-family: var(--font-mono); font-size: 10px; font-weight: 700; color: #d37768; background: rgba(211, 119, 104, 0.15); padding: 1px 6px; border-radius: 4px; border: 1px solid rgba(211, 119, 104, 0.3); letter-spacing: 0.05em;">ÉLEVÉE</span>
                    </div>
                    <div style="font-family: var(--font-body); font-size: 12px; color: var(--on-surface-variant, #bdc9c3); margin-bottom: 6px;">
                        Memory Leak (Pool A)
                    </div>
                    <div style="display: flex; align-items: center; gap: 4px; font-family: var(--font-mono); font-size: 12px; color: #d37768;">
                        <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><circle cx="12" cy="12" r="10"/><polyline points="12 6 12 12 16 14"/></svg>
                        <span>12j 14h</span>
                    </div>
                </div>

                <!-- 3. SRV-APP-14 (MOYENNE) -->
                <div class="urgency-item" style="border-left: 4px solid #81d0f8;">
                    <div style="display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 2px;">
                        <span style="font-family: var(--font-mono); font-size: 13px; font-weight: 600; color: #dfe4e0;">SRV-APP-14</span>
                        <span style="font-family: var(--font-mono); font-size: 10px; font-weight: 700; color: #81d0f8; background: rgba(129, 208, 248, 0.15); padding: 1px 6px; border-radius: 4px; border: 1px solid rgba(129, 208, 248, 0.3); letter-spacing: 0.05em;">MOYENNE</span>
                    </div>
                    <div style="font-family: var(--font-body); font-size: 12px; color: var(--on-surface-variant, #bdc9c3); margin-bottom: 6px;">
                        Usure ventilateur CPU 2
                    </div>
                    <div style="display: flex; align-items: center; gap: 4px; font-family: var(--font-mono); font-size: 12px; color: #81d0f8;">
                        <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><circle cx="12" cy="12" r="10"/><polyline points="12 6 12 12 16 14"/></svg>
                        <span>24j 00h</span>
                    </div>
                </div>

                <!-- 4. SW-ACC-4B (FAIBLE) -->
                <div class="urgency-item" style="border-left: 4px solid rgba(120, 216, 186, 0.5); opacity: 0.85;">
                    <div style="display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 2px;">
                        <span style="font-family: var(--font-mono); font-size: 13px; font-weight: 600; color: #dfe4e0;">SW-ACC-4B</span>
                        <span style="font-family: var(--font-mono); font-size: 10px; font-weight: 700; color: #78d8ba; background: rgba(120, 216, 186, 0.15); padding: 1px 6px; border-radius: 4px; border: 1px solid rgba(120, 216, 186, 0.3); letter-spacing: 0.05em;">FAIBLE</span>
                    </div>
                    <div style="font-family: var(--font-body); font-size: 12px; color: var(--on-surface-variant, #bdc9c3); margin-bottom: 6px;">
                        Anomalie mineure I/O
                    </div>
                    <div style="display: flex; align-items: center; gap: 4px; font-family: var(--font-mono); font-size: 12px; color: rgba(120, 216, 186, 0.9);">
                        <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><circle cx="12" cy="12" r="10"/><polyline points="12 6 12 12 16 14"/></svg>
                        <span>&gt; 60j</span>
                    </div>
                </div>
            </div>
        </div>
        """
    )
