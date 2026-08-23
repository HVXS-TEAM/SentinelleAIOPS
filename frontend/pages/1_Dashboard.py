"""
1_Dashboard.py — Sentinelle AIOps
Pixel-perfect ref : Ecrans_Reference/Dashboard/screen.png
Sources : DESIGN.md (tokens) + screen.png (layout, valeurs visuelles)
Corrections appliquées :
  - Boutons "7 DERNIERS JOURS" (ghost) et "+ ACTION" (primary) en HTML snt-btn
  - Graphique : range Y [0-100], tickvals 0/25/50/75/100%, fill tozeroy semi-transparent
  - Tableau : sparkline SVG inline pour Switch-Core-01 dans colonne TENDANCE (1H)
"""
import os, sys
import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from page_template import page_bootstrap
from components import badge, mono, alert_card

# ── Garde d'authentification ─────────────────────────────────────────────────
if not st.session_state.get("authenticated", False):
    st.switch_page("app.py")

page_bootstrap(
    active="Dashboard",
    page_title="Dashboard Opérationnel",
    search_placeholder="Rechercher IP, appareil, alerte..."
)

# ── TITRE + BOUTONS ─────────────────────────────────────────
# Deux boutons en HTML avec les classes snt-btn du design system
# snt-btn-ghost → "7 DERNIERS JOURS" (outline secondary)
# snt-btn-primary → "+ ACTION" (fond teal #78d8ba)
tc, bc = st.columns([3, 1])
with tc:
    st.markdown("## Dashboard Opérationnel")
    st.caption("Vue d'ensemble de l'infrastructure AIOps")
with bc:
    st.markdown("""
    <div style="display:flex;gap:8px;justify-content:flex-end;align-items:center;padding-top:6px;">
        <button class="snt-btn snt-btn-ghost" style="cursor:default;">
            <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor"
                 stroke-width="2" stroke-linecap="round" stroke-linejoin="round"
                 style="flex-shrink:0;">
                <rect x="3" y="4" width="18" height="18" rx="2" ry="2"/>
                <line x1="16" y1="2" x2="16" y2="6"/>
                <line x1="8" y1="2" x2="8" y2="6"/>
                <line x1="3" y1="10" x2="21" y2="10"/>
            </svg>
            7 DERNIERS JOURS
        </button>
        <button class="snt-btn snt-btn-primary" style="cursor:default;">
            + ACTION
        </button>
    </div>
    """, unsafe_allow_html=True)

# ── KPI CARDS ───────────────────────────────────────────────
k1, k2, k3, k4, k5 = st.columns(5)

with k1:
    st.markdown("""
    <div class="snt-card">
        <div class="snt-card-title">APPAREILS SURVEILLÉS</div>
        <div class="snt-card-kpi-value">1,248
            <span class="snt-card-delta up">↗ 2.4%</span>
        </div>
    </div>""", unsafe_allow_html=True)

with k2:
    st.markdown("""
    <div class="snt-card critical">
        <div class="snt-card-title" style="color:var(--error);">
            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5">
                <path d="M10.29 3.86L1.82 18a2 2 0 0 0 1.71 3h16.94a2 2 0 0 0 1.71-3L13.71 3.86a2 2 0 0 0-3.42 0z"/>
                <line x1="12" y1="9" x2="12" y2="13"/>
                <line x1="12" y1="17" x2="12.01" y2="17"/>
            </svg>
            ALERTES CRITIQUES
        </div>
        <div class="snt-card-kpi-value" style="color:var(--error);">3</div>
        <div style="font-size:11px;color:var(--error);margin-top:6px;font-weight:600;">Action requise</div>
    </div>""", unsafe_allow_html=True)

with k3:
    st.markdown("""
    <div class="snt-card">
        <div class="snt-card-title">SCORE DE SANTÉ</div>
        <div class="snt-card-kpi-value" style="color:var(--primary);">94%
            <svg width="64" height="28" viewBox="0 0 64 28" style="vertical-align:middle;margin-left:8px;">
                <polyline points="0,22 10,18 20,12 30,15 40,8 50,6 64,10"
                          fill="none" stroke="#78d8ba" stroke-width="2"/>
            </svg>
        </div>
    </div>""", unsafe_allow_html=True)

with k4:
    st.markdown("""
    <div class="snt-card">
        <div class="snt-card-title">INCIDENTS PRÉDITS</div>
        <div class="snt-card-kpi-value" style="color:var(--secondary);">12
            <span style="font-size:12px;color:var(--on-surface-variant);font-weight:400;
                         font-family:var(--font-body);"> Prochains 7j</span>
        </div>
    </div>""", unsafe_allow_html=True)

with k5:
    st.markdown("""
    <div class="snt-card">
        <div class="snt-card-title">CONFORMITÉ RÉSEAU</div>
        <div class="snt-card-kpi-value">88%
            <span class="snt-card-delta down">↘ 1.2%</span>
        </div>
    </div>""", unsafe_allow_html=True)

# ── GRAPHE + FLUX ALERTES ────────────────────────────────────
col_chart, col_alerts = st.columns([2.2, 1])

with col_chart:
    st.markdown(
        '<div class="snt-card-title" style="padding:0;margin-bottom:8px;">'
        'TENDANCES RESSOURCES &amp; PRÉDICTIONS IA'
        '</div>',
        unsafe_allow_html=True
    )

    # Axe X catégoriel — les deux séries partagent les mêmes catégories
    # pour que fill="tozeroy" fonctionne correctement sans erreurs
    all_days = ["J-7", "J-5", "J-3", "Hier", "Aujourd'hui", "J+1", "J+3"]

    # Données historiques (5 points) + NaN pour les 2 prédictions
    cpu_y    = [34, 42, 58, 48, 68, None, None]
    ram_y    = [50, 54, 44, 49, 59, None, None]
    # Prédictions : NaN pour les 4 points historiques + aujourd'hui de liaison + J+1 + J+3
    pred_y   = [None, None, None, None, 68, 72, 65]

    fig = go.Figure()

    # CPU — ligne + fill semi-transparent (style Grafana)
    fig.add_trace(go.Scatter(
        x=all_days, y=cpu_y,
        name="CPU", mode="lines+markers",
        line=dict(color="#78d8ba", width=2.5),
        marker=dict(size=4),
        fill="tozeroy",
        fillcolor="rgba(120, 216, 186, 0.08)",
        connectgaps=False
    ))

    # RAM — ligne + fill semi-transparent
    fig.add_trace(go.Scatter(
        x=all_days, y=ram_y,
        name="RAM", mode="lines+markers",
        line=dict(color="#81d0f8", width=2.5),
        marker=dict(size=4),
        fill="tozeroy",
        fillcolor="rgba(129, 208, 248, 0.06)",
        connectgaps=False
    ))

    # Prédictions IA — tirets, cercles ouverts
    fig.add_trace(go.Scatter(
        x=all_days, y=pred_y,
        name="Prédictions IA", mode="lines+markers",
        line=dict(color="#78d8ba", width=2, dash="dash"),
        marker=dict(symbol="circle-open", size=6),
        connectgaps=False
    ))

    # Ligne verticale "Aujourd'hui" via add_shape (compatible axe catégoriel)
    fig.add_shape(
        type="line",
        x0="Aujourd'hui", x1="Aujourd'hui",
        y0=0, y1=1, xref="x", yref="paper",
        line=dict(dash="dot", color="#87938e", width=1)
    )
    fig.add_annotation(
        x="Aujourd'hui", y=1.02,
        xref="x", yref="paper",
        text="Aujourd'hui", showarrow=False,
        font=dict(color="#bdc9c3", size=10),
        yanchor="bottom"
    )

    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(family="IBM Plex Sans, Inter, sans-serif", color="#bdc9c3", size=11),
        legend=dict(
            orientation="h", yanchor="top", y=1.12, xanchor="right", x=1,
            font=dict(size=11), bgcolor="rgba(0,0,0,0)"
        ),
        margin=dict(l=4, r=4, t=36, b=4),
        xaxis=dict(
            showgrid=False,
            tickfont=dict(size=10),
            color="#87938e",
            categoryorder="array",
            categoryarray=all_days
        ),
        yaxis=dict(
            showgrid=True,
            gridcolor="rgba(255,255,255,0.05)",
            tickvals=[0, 25, 50, 75, 100],
            ticktext=["0%", "25%", "50%", "75%", "100%"],
            tickfont=dict(size=10),
            color="#87938e",
            range=[0, 100]
        ),
        height=340,
    )
    st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})

with col_alerts:
    st.markdown("""
    <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:12px;">
        <div class="snt-card-title" style="padding:0;margin:0;">FLUX D'ALERTES ACTIVES</div>
        <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="#87938e" stroke-width="2">
            <line x1="21" y1="10" x2="3" y2="10"/>
            <line x1="21" y1="6" x2="3" y2="6"/>
            <line x1="21" y1="14" x2="3" y2="14"/>
            <line x1="21" y1="18" x2="3" y2="18"/>
        </svg>
    </div>""", unsafe_allow_html=True)

    st.markdown(alert_card(
        "🔴",
        "Surcharge CPU détectée",
        "Il y a 2m — Switch-Core-01 atteint 98% d'utilisation (NetDevOps)"
    ), unsafe_allow_html=True)

    st.markdown(alert_card(
        "⚠️",
        "Latence réseau anormale",
        "Il y a 15m — Lien vers Datacenter B > 50ms (Supervision)"
    ), unsafe_allow_html=True)

    st.markdown(alert_card(
        "🛡️",
        "Tentative d'intrusion bloquée",
        "Il y a 1h — IP suspecte détectée sur Firewall-Edge (Sécurité)"
    ), unsafe_allow_html=True)

    st.markdown("""
    <div style="text-align:center;margin-top:12px;">
        <a style="font-family:var(--font-mono);font-size:10px;color:var(--primary);
           text-decoration:none;letter-spacing:0.08em;text-transform:uppercase;cursor:pointer;">
           VOIR TOUTES LES ALERTES →
        </a>
    </div>""", unsafe_allow_html=True)

st.markdown('<hr class="snt-divider"/>', unsafe_allow_html=True)

# ── TABLEAU ÉQUIPEMENTS + DONUT ──────────────────────────────
col_tbl, col_pie = st.columns([2, 1])

# Sparkline SVG inline pour Switch-Core-01 (ligne rouge montante, reflète CPU 98%)
_sparkline_critical = (
    '<svg width="60" height="24" viewBox="0 0 60 24" style="vertical-align:middle;">'
    '<polyline points="0,20 10,18 20,16 30,14 40,10 50,6 60,2"'
    ' fill="none" stroke="var(--error)" stroke-width="1.8" stroke-linejoin="round"/>'
    '</svg>'
)

with col_tbl:
    st.markdown(
        '<div class="snt-card-title" style="padding:0;margin-bottom:10px;">'
        'STATUT DES ÉQUIPEMENTS CRITIQUES'
        '</div>',
        unsafe_allow_html=True
    )
    df = pd.DataFrame([
        {
            "STATUT": badge("● CRITIQUE", "critical"),
            "ÉQUIPEMENT": "<b>Switch-Core-01</b>",
            "TYPE": "Switch",
            "IP / LOCALISATION": mono("10.0.1.1"),
            "TENDANCE (1H)": _sparkline_critical,
        },
        {
            "STATUT": badge("● NORMAL", "healthy"),
            "ÉQUIPEMENT": "<b>SRV-AUTH-01</b>",
            "TYPE": "Serveur",
            "IP / LOCALISATION": mono("10.0.1.10"),
            "TENDANCE (1H)": "<span style='color:var(--primary);font-weight:600;'>→ Stable</span>",
        },
        {
            "STATUT": badge("● WARNING", "warning"),
            "ÉQUIPEMENT": "<b>RTR-EDGE-01</b>",
            "TYPE": "Routeur",
            "IP / LOCALISATION": mono("10.0.1.254"),
            "TENDANCE (1H)": "<span style='color:#d37768;font-weight:600;'>↑ Latence 52ms</span>",
        },
    ])
    st.markdown(
        df.to_html(escape=False, index=False, classes="sentinelle-table"),
        unsafe_allow_html=True
    )

with col_pie:
    st.markdown(
        '<div class="snt-card-title" style="padding:0;margin-bottom:8px;">RÉPARTITION DU PARC</div>',
        unsafe_allow_html=True
    )
    df_d = pd.DataFrame({
        "Type": ["Serveurs", "Switches", "Routeurs", "Pare-feux"],
        "n":    [600, 350, 150, 148]
    })
    fig_d = px.pie(
        df_d, names="Type", values="n", hole=0.66,
        color_discrete_sequence=["#78d8ba", "#81d0f8", "#a7c8ff", "#3da186"]
    )
    fig_d.update_traces(textposition="none")
    fig_d.add_annotation(
        text="1.2k<br>TOTAL", x=0.5, y=0.5, showarrow=False,
        font=dict(family="JetBrains Mono", size=18, color="#e0e3e6")
    )
    fig_d.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(family="IBM Plex Sans", color="#bdc9c3"),
        margin=dict(l=0, r=0, t=0, b=0),
        legend=dict(orientation="v", font=dict(size=11), bgcolor="rgba(0,0,0,0)"),
        height=260,
    )
    st.plotly_chart(fig_d, use_container_width=True, config={"displayModeBar": False})
