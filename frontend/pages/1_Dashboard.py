"""
1_Dashboard.py — Sentinelle AIOps
Pixel-perfect ref : Ecrans_Reference/Dashboard/screen.png
Sources : DESIGN.md (tokens) + screen.png (layout, valeurs visuelles)
"""
import os, sys
import streamlit as st

st.set_page_config(
    page_title="Dashboard Opérationnel — Sentinelle AIOps",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded",
)

import plotly.graph_objects as go
import plotly.express as px
import pandas as pd

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from page_template import page_bootstrap
from components import badge, mono

# ── Garde d'authentification ─────────────────────────────────────────────────
if not st.session_state.get("authenticated", False):
    st.switch_page("app.py")

page_bootstrap(
    active="Dashboard",
    page_title="Dashboard Opérationnel",
    search_placeholder="Rechercher IP, appareil, alerte..."
)

# ── STYLES DÉDIÉS DASHBOARD (alignés sur DESIGN.md et screen.png) ───────────
st.markdown("""
<style>
/* Cartes KPI du haut */
.dash-kpi-card {
    background-color: var(--surface-container, #1d2022);
    border: 1px solid var(--border-subtle, rgba(255, 255, 255, 0.08));
    border-radius: 12px;
    padding: 16px;
    height: 100%;
    display: flex;
    flex-direction: column;
    justify-content: space-between;
}
.dash-kpi-card.critical {
    border-color: rgba(255, 180, 171, 0.35);
    background: linear-gradient(180deg, rgba(147, 0, 10, 0.12) 0%, rgba(29, 32, 34, 1) 100%);
}
.dash-kpi-title {
    font-family: var(--font-mono, 'JetBrains Mono', monospace);
    font-size: 11px;
    font-weight: 500;
    letter-spacing: 0.05em;
    color: var(--on-surface-variant, #bdc9c3);
    text-transform: uppercase;
    display: flex;
    align-items: center;
    gap: 6px;
    margin-bottom: 8px;
}
.dash-kpi-value-row {
    display: flex;
    align-items: baseline;
    justify-content: space-between;
    gap: 8px;
}
.dash-kpi-val {
    font-family: var(--font-mono, 'JetBrains Mono', monospace);
    font-size: 32px;
    font-weight: 600;
    line-height: 1.1;
    color: var(--on-surface, #e0e3e6);
}
.dash-delta-up {
    font-family: var(--font-mono, 'JetBrains Mono', monospace);
    font-size: 12px;
    font-weight: 600;
    color: var(--primary, #78d8ba);
}
.dash-delta-down {
    font-family: var(--font-mono, 'JetBrains Mono', monospace);
    font-size: 12px;
    font-weight: 600;
    color: var(--error, #ffb4ab);
}

/* Boutons d'en-tête */
.dash-btn-ghost {
    display: inline-flex;
    align-items: center;
    gap: 6px;
    background: transparent;
    border: 1px solid var(--outline-variant, #3e4945);
    color: var(--on-surface, #e0e3e6);
    font-family: var(--font-mono, 'JetBrains Mono', monospace);
    font-size: 11px;
    font-weight: 600;
    letter-spacing: 0.04em;
    padding: 8px 14px;
    border-radius: 8px;
    cursor: pointer;
}
.dash-btn-primary {
    display: inline-flex;
    align-items: center;
    gap: 4px;
    background: var(--primary, #78d8ba);
    border: none;
    color: var(--on-primary, #00382b);
    font-family: var(--font-mono, 'JetBrains Mono', monospace);
    font-size: 11px;
    font-weight: 700;
    letter-spacing: 0.04em;
    padding: 8px 16px;
    border-radius: 8px;
    cursor: pointer;
}

/* Flux d'alertes actives */
.dash-alert-card {
    background-color: var(--surface-container, #1d2022);
    border: 1px solid var(--border-subtle, rgba(255, 255, 255, 0.08));
    border-radius: 10px;
    padding: 12px 14px;
    margin-bottom: 10px;
    border-left: 3px solid var(--primary, #78d8ba);
}
.dash-alert-card.critical {
    border-left-color: var(--error, #ffb4ab);
}
.dash-alert-card.warning {
    border-left-color: #ffcc80;
}
.dash-alert-top {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 6px;
}
.dash-badge-crit {
    background-color: rgba(147, 0, 10, 0.4);
    color: #ffdad6;
    font-family: var(--font-mono, 'JetBrains Mono', monospace);
    font-size: 10px;
    font-weight: 700;
    padding: 2px 6px;
    border-radius: 4px;
    letter-spacing: 0.05em;
}
.dash-badge-warn {
    background-color: rgba(102, 77, 3, 0.4);
    color: #ffe082;
    font-family: var(--font-mono, 'JetBrains Mono', monospace);
    font-size: 10px;
    font-weight: 700;
    padding: 2px 6px;
    border-radius: 4px;
    letter-spacing: 0.05em;
}
.dash-alert-time {
    font-family: var(--font-mono, 'JetBrains Mono', monospace);
    font-size: 11px;
    color: var(--on-surface-variant, #bdc9c3);
}
.dash-alert-title {
    font-family: var(--font-body, 'Inter', sans-serif);
    font-size: 13px;
    font-weight: 600;
    color: var(--on-surface, #e0e3e6);
    margin-bottom: 2px;
}
.dash-alert-desc {
    font-family: var(--font-body, 'Inter', sans-serif);
    font-size: 12px;
    color: var(--on-surface-variant, #bdc9c3);
    margin-bottom: 8px;
}
.dash-alert-tag {
    display: inline-flex;
    align-items: center;
    gap: 4px;
    background: rgba(255, 255, 255, 0.05);
    border: 1px solid rgba(255, 255, 255, 0.1);
    color: var(--on-surface-variant, #bdc9c3);
    font-family: var(--font-mono, 'JetBrains Mono', monospace);
    font-size: 10px;
    padding: 2px 8px;
    border-radius: 4px;
}
</style>
""", unsafe_allow_html=True)

# ── TITRE + BOUTONS D'ACTION ─────────────────────────────────────────────────
tc, bc = st.columns([3, 1])
with tc:
    st.markdown(
        """
        <div style="margin-bottom: 16px;">
            <div style="font-family: var(--font-display, 'IBM Plex Sans'); font-size: 28px; font-weight: 600; color: var(--on-surface, #e0e3e6); line-height: 1.2;">
                Dashboard Opérationnel
            </div>
            <div style="font-family: var(--font-body, 'Inter'); font-size: 14px; color: var(--on-surface-variant, #bdc9c3); margin-top: 4px;">
                Vue d'ensemble de l'infrastructure AIOps
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )
with bc:
    st.markdown(
        """
        <div style="display:flex; gap:10px; justify-content:flex-end; align-items:center; padding-top:6px;">
            <button class="dash-btn-ghost">
                <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                    <rect x="3" y="4" width="18" height="18" rx="2" ry="2"/>
                    <line x1="16" y1="2" x2="16" y2="6"/>
                    <line x1="8" y1="2" x2="8" y2="6"/>
                    <line x1="3" y1="10" x2="21" y2="10"/>
                </svg>
                7 DERNIERS JOURS
            </button>
            <button class="dash-btn-primary">
                + ACTION
            </button>
        </div>
        """,
        unsafe_allow_html=True
    )

# ── 5 CARTES KPI SUPÉRIEURES ────────────────────────────────────────────────
k1, k2, k3, k4, k5 = st.columns(5)

with k1:
    st.markdown("""
    <div class="dash-kpi-card">
        <div class="dash-kpi-title">APPAREILS SURVEILLÉS</div>
        <div class="dash-kpi-value-row">
            <span class="dash-kpi-val">1,248</span>
            <span class="dash-delta-up">↗ 2.4%</span>
        </div>
    </div>""", unsafe_allow_html=True)

with k2:
    st.markdown("""
    <div class="dash-kpi-card critical">
        <div class="dash-kpi-title" style="color: var(--error, #ffb4ab);">
            <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5">
                <path d="M10.29 3.86L1.82 18a2 2 0 0 0 1.71 3h16.94a2 2 0 0 0 1.71-3L13.71 3.86a2 2 0 0 0-3.42 0z"/>
                <line x1="12" y1="9" x2="12" y2="13"/>
                <line x1="12" y1="17" x2="12.01" y2="17"/>
            </svg>
            ALERTES CRITIQUES
        </div>
        <div class="dash-kpi-value-row">
            <span class="dash-kpi-val" style="color: var(--error, #ffb4ab);">3</span>
        </div>
        <div style="font-family: var(--font-body); font-size: 11px; color: var(--error, #ffb4ab); margin-top: 6px; font-weight: 500;">
            Action requise
        </div>
    </div>""", unsafe_allow_html=True)

with k3:
    st.markdown("""
    <div class="dash-kpi-card">
        <div class="dash-kpi-title">SCORE DE SANTÉ</div>
        <div class="dash-kpi-value-row">
            <span class="dash-kpi-val" style="color: var(--primary, #78d8ba);">94%</span>
            <svg width="56" height="24" viewBox="0 0 64 28" style="vertical-align: middle;">
                <polyline points="0,22 10,18 20,12 30,15 40,8 50,6 64,10"
                          fill="none" stroke="#78d8ba" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"/>
            </svg>
        </div>
    </div>""", unsafe_allow_html=True)

with k4:
    st.markdown("""
    <div class="dash-kpi-card">
        <div class="dash-kpi-title">INCIDENTS PRÉDITS</div>
        <div class="dash-kpi-value-row">
            <span class="dash-kpi-val" style="color: var(--secondary, #81d0f8);">12</span>
            <span style="font-family: var(--font-body); font-size: 11px; color: var(--on-surface-variant, #bdc9c3);">Prochains 7j</span>
        </div>
    </div>""", unsafe_allow_html=True)

with k5:
    st.markdown("""
    <div class="dash-kpi-card">
        <div class="dash-kpi-title">CONFORMITÉ RÉSEAU</div>
        <div class="dash-kpi-value-row">
            <span class="dash-kpi-val">88%</span>
            <span class="dash-delta-down">↘ 1.2%</span>
        </div>
    </div>""", unsafe_allow_html=True)

st.markdown("<div style='height: 16px;'></div>", unsafe_allow_html=True)

# ── SECTION CENTRALE : GRAPHIQUE TENDANCES + FLUX D'ALERTES ──────────────────
col_chart, col_alerts = st.columns([2.3, 1])

with col_chart:
    st.markdown(
        """
        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px;">
            <div style="font-family: var(--font-mono, monospace); font-size: 11px; font-weight: 600; letter-spacing: 0.05em; color: var(--on-surface-variant, #bdc9c3); text-transform: uppercase;">
                TENDANCES RESSOURCES &amp; PRÉDICTIONS IA
            </div>
            <div style="display: flex; gap: 14px; align-items: center; font-family: var(--font-mono, monospace); font-size: 11px; color: var(--on-surface-variant, #bdc9c3);">
                <span style="display: flex; align-items: center; gap: 5px;"><span style="width: 8px; height: 8px; border-radius: 50%; background: #78d8ba; display: inline-block;"></span> CPU</span>
                <span style="display: flex; align-items: center; gap: 5px;"><span style="width: 8px; height: 8px; border-radius: 50%; background: #81d0f8; display: inline-block;"></span> RAM</span>
                <span style="display: flex; align-items: center; gap: 5px;"><span style="width: 8px; height: 8px; border-radius: 50%; border: 1.5px dashed #78d8ba; display: inline-block;"></span> Prédictions IA</span>
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

    all_days = ["J-7", "J-5", "J-3", "Hier", "Aujourd'hui", "J+1", "J+3"]
    cpu_y    = [34, 42, 58, 48, 68, None, None]
    ram_y    = [50, 54, 44, 49, 59, None, None]
    pred_y   = [None, None, None, None, 68, 72, 65]

    fig = go.Figure()

    # CPU — ligne pleine teal + fill semi-transparent
    fig.add_trace(go.Scatter(
        x=all_days, y=cpu_y,
        name="CPU", mode="lines",
        line=dict(color="#78d8ba", width=2.5),
        fill="tozeroy",
        fillcolor="rgba(120, 216, 186, 0.08)",
        connectgaps=False,
        showlegend=False
    ))

    # RAM — ligne pleine cyan + fill semi-transparent
    fig.add_trace(go.Scatter(
        x=all_days, y=ram_y,
        name="RAM", mode="lines",
        line=dict(color="#81d0f8", width=2.5),
        fill="tozeroy",
        fillcolor="rgba(129, 208, 248, 0.06)",
        connectgaps=False,
        showlegend=False
    ))

    # Prédictions IA — tirets saumon/teal
    fig.add_trace(go.Scatter(
        x=all_days, y=pred_y,
        name="Prédictions IA", mode="lines+markers",
        line=dict(color="#78d8ba", width=2, dash="dash"),
        marker=dict(symbol="circle-open", size=6, color="#78d8ba"),
        connectgaps=False,
        showlegend=False
    ))

    # Ligne verticale de démarcation "Aujourd'hui"
    fig.add_shape(
        type="line",
        x0="Aujourd'hui", x1="Aujourd'hui",
        y0=0, y1=1, xref="x", yref="paper",
        line=dict(dash="dot", color="rgba(255, 255, 255, 0.3)", width=1.5)
    )

    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(family="IBM Plex Sans, Inter, sans-serif", color="#bdc9c3", size=11),
        margin=dict(l=10, r=10, t=10, b=10),
        xaxis=dict(
            showgrid=False,
            tickfont=dict(size=11, family="JetBrains Mono"),
            color="#87938e",
            categoryorder="array",
            categoryarray=all_days
        ),
        yaxis=dict(
            showgrid=True,
            gridcolor="rgba(255,255,255,0.05)",
            tickvals=[0, 25, 50, 75, 100],
            ticktext=["0%", "25%", "50%", "75%", "100%"],
            tickfont=dict(size=10, family="JetBrains Mono"),
            color="#87938e",
            range=[0, 100]
        ),
        height=320,
    )
    st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})

with col_alerts:
    st.markdown("""
    <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:12px;">
        <div style="font-family: var(--font-mono, monospace); font-size: 11px; font-weight: 600; letter-spacing: 0.05em; color: var(--on-surface-variant, #bdc9c3); text-transform: uppercase;">
            FLUX D'ALERTES ACTIVES
        </div>
        <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="#87938e" stroke-width="2">
            <line x1="21" y1="10" x2="3" y2="10"/>
            <line x1="21" y1="6" x2="3" y2="6"/>
            <line x1="21" y1="14" x2="3" y2="14"/>
            <line x1="21" y1="18" x2="3" y2="18"/>
        </svg>
    </div>
    
    <div class="dash-alert-card critical">
        <div class="dash-alert-top">
            <span class="dash-badge-crit">CRITICAL</span>
            <span class="dash-alert-time">Il y a 2m</span>
        </div>
        <div class="dash-alert-title">Surcharge CPU détectée</div>
        <div class="dash-alert-desc">Switch-Core-01 atteint 98% d'utilisation.</div>
        <div><span class="dash-alert-tag">🖧 NetDevOps</span></div>
    </div>

    <div class="dash-alert-card warning">
        <div class="dash-alert-top">
            <span class="dash-badge-warn">WARNING</span>
            <span class="dash-alert-time">Il y a 15m</span>
        </div>
        <div class="dash-alert-title">Latence réseau anormale</div>
        <div class="dash-alert-desc">Lien vers Datacenter B > 50ms.</div>
        <div><span class="dash-alert-tag">📈 Supervision</span></div>
    </div>

    <div class="dash-alert-card critical">
        <div class="dash-alert-top">
            <span class="dash-badge-crit">CRITICAL</span>
            <span class="dash-alert-time">Il y a 1h</span>
        </div>
        <div class="dash-alert-title">Tentative d'intrusion bloquée</div>
        <div class="dash-alert-desc">IP suspecte détectée sur Firewall-Edge.</div>
        <div><span class="dash-alert-tag">🛡️ Sécurité</span></div>
    </div>

    <div style="text-align:center; margin-top:14px;">
        <a style="font-family: var(--font-mono, monospace); font-size: 11px; font-weight: 600; color: var(--primary, #78d8ba); text-decoration: none; letter-spacing: 0.08em; text-transform: uppercase; cursor: pointer;">
            VOIR TOUTES LES ALERTES
        </a>
    </div>
    """, unsafe_allow_html=True)

st.markdown("<div style='height: 16px;'></div>", unsafe_allow_html=True)

# ── SECTION INFÉRIEURE : STATUT DES ÉQUIPEMENTS + RÉPARTITION DU PARC ────────
col_tbl, col_pie = st.columns([2.1, 1])

# Sparkline rouge pour Switch-Core-01
_sparkline_critical = (
    '<svg width="56" height="20" viewBox="0 0 60 24" style="vertical-align:middle;">'
    '<polyline points="0,20 12,18 24,15 36,13 48,8 60,3"'
    ' fill="none" stroke="var(--error, #ffb4ab)" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>'
    '</svg>'
)

with col_tbl:
    st.markdown(
        """
        <div style="font-family: var(--font-mono, monospace); font-size: 11px; font-weight: 600; letter-spacing: 0.05em; color: var(--on-surface-variant, #bdc9c3); text-transform: uppercase; margin-bottom: 12px;">
            STATUT DES ÉQUIPEMENTS CRITIQUES
        </div>
        """,
        unsafe_allow_html=True
    )
    df = pd.DataFrame([
        {
            "STATUT": '<span style="display:inline-flex;align-items:center;gap:6px;background:rgba(147,0,10,0.3);color:#ffdad6;padding:3px 10px;border-radius:12px;font-family:var(--font-mono);font-size:11px;font-weight:600;"><span style="width:6px;height:6px;border-radius:50%;background:#ffb4ab;"></span>CRITIQUE</span>',
            "ÉQUIPEMENT": "<b>Switch-Core-01</b>",
            "TYPE": "<span style='color:var(--on-surface-variant);'>🖧 Switch</span>",
            "IP / LOCALISATION": mono("10.0.1.1"),
            "TENDANCE (1H)": _sparkline_critical,
        },
        {
            "STATUT": '<span style="display:inline-flex;align-items:center;gap:6px;background:rgba(0,107,85,0.3);color:#78d8ba;padding:3px 10px;border-radius:12px;font-family:var(--font-mono);font-size:11px;font-weight:600;"><span style="width:6px;height:6px;border-radius:50%;background:#78d8ba;"></span>NORMAL</span>',
            "ÉQUIPEMENT": "<b>SRV-AUTH-01</b>",
            "TYPE": "<span style='color:var(--on-surface-variant);'>🖥 Serveur</span>",
            "IP / LOCALISATION": mono("10.0.1.10"),
            "TENDANCE (1H)": "<span style='color:var(--primary, #78d8ba);font-family:var(--font-mono);font-size:11px;font-weight:600;'>→ Stable</span>",
        },
        {
            "STATUT": '<span style="display:inline-flex;align-items:center;gap:6px;background:rgba(102,77,3,0.3);color:#ffe082;padding:3px 10px;border-radius:12px;font-family:var(--font-mono);font-size:11px;font-weight:600;"><span style="width:6px;height:6px;border-radius:50%;background:#ffe082;"></span>WARNING</span>',
            "ÉQUIPEMENT": "<b>RTR-EDGE-01</b>",
            "TYPE": "<span style='color:var(--on-surface-variant);'>📡 Routeur</span>",
            "IP / LOCALISATION": mono("10.0.1.254"),
            "TENDANCE (1H)": "<span style='color:#ffb4ab;font-family:var(--font-mono);font-size:11px;font-weight:600;'>↑ Latence 52ms</span>",
        },
    ])
    st.markdown(
        df.to_html(escape=False, index=False, classes="sentinelle-table"),
        unsafe_allow_html=True
    )

with col_pie:
    st.markdown(
        """
        <div style="font-family: var(--font-mono, monospace); font-size: 11px; font-weight: 600; letter-spacing: 0.05em; color: var(--on-surface-variant, #bdc9c3); text-transform: uppercase; margin-bottom: 8px;">
            RÉPARTITION DU PARC
        </div>
        """,
        unsafe_allow_html=True
    )
    df_d = pd.DataFrame({
        "Type": ["Serveurs", "Switches", "Routeurs", "Pare-feux"],
        "n":    [600, 350, 150, 148]
    })
    fig_d = px.pie(
        df_d, names="Type", values="n", hole=0.72,
        color_discrete_sequence=["#78d8ba", "#81d0f8", "#a7c8ff", "#3da186"]
    )
    fig_d.update_traces(textposition="none", hoverinfo="label+percent+value")
    fig_d.add_annotation(
        text="<b style='font-size:19px;'>1.2k</b><br><span style='font-size:10px;letter-spacing:0.08em;color:#bdc9c3;'>TOTAL</span>",
        x=0.5, y=0.5, showarrow=False,
        font=dict(family="JetBrains Mono", color="#e0e3e6")
    )
    fig_d.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(family="IBM Plex Sans, Inter", color="#e0e3e6", size=12),
        margin=dict(l=0, r=0, t=0, b=0),
        legend=dict(orientation="v", yanchor="middle", y=0.5, xanchor="left", x=1.02, font=dict(size=12, color="#e0e3e6"), bgcolor="rgba(0,0,0,0)"),
        height=240,
    )
    st.plotly_chart(fig_d, use_container_width=True, config={"displayModeBar": False})

