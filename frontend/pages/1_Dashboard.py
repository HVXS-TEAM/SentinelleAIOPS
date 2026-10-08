"""
1_Dashboard.py — Sentinelle AIOps
Pixel-perfect ref : Ecrans_Reference/Dashboard/screen.png
Sources : DESIGN.md (tokens) + screen.png (layout, valeurs visuelles)
"""
import os, sys
from pathlib import Path
import streamlit as st

_LOGO_PATH = str(Path(__file__).parent.parent / "static" / "logo.png")

st.set_page_config(
    page_title="Dashboard Opérationnel — Sentinelle AIOps",
    page_icon=_LOGO_PATH,
    layout="wide",
    initial_sidebar_state="expanded",
)

import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
import numpy as np
from datetime import datetime, timezone

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from page_template import page_bootstrap
from components import badge, mono
import api_client as api

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

# ── Données réelles (API) ─────────────────────────────────────────────────────
equipements = api.get_equipements()
alertes_actives = api.get_alertes(statut="active")
predictions = api.get_predictions()
audits = api.get_audits()

nb_equipements = len(equipements)
nb_alertes_critiques = sum(1 for a in alertes_actives if a.get("severite") == "critique")
score_sante_moyen = round(sum(e["health_score"] for e in equipements) / nb_equipements) if nb_equipements else 0
nb_incidents_predits = sum(1 for p in predictions if p.get("ttf_estime", 9999) <= 168)  # horizon 7 jours
audits_non_corriges = sum(1 for a in audits if a.get("statut") != "corrige")
conformite_reseau = max(0, 100 - audits_non_corriges * 5)


def _time_ago(iso_str: str) -> str:
    """Convertit un horodatage ISO (naïf, UTC) en libellé relatif court."""
    try:
        dt = datetime.fromisoformat(iso_str)
    except Exception:
        return ""
    seconds = (datetime.now(timezone.utc).replace(tzinfo=None) - dt).total_seconds()
    if seconds < 60:
        return "À l'instant"
    minutes = int(seconds // 60)
    if minutes < 60:
        return f"Il y a {minutes}m"
    hours = int(minutes // 60)
    if hours < 24:
        return f"Il y a {hours}h"
    return f"Il y a {int(hours // 24)}j"


def _resample_avg(metrics: list) -> list:
    """Regroupe les métriques de plusieurs équipements par horodatage tronqué
    à la dizaine de secondes (cadence du scheduler Phase 1) et moyenne les
    valeurs pour obtenir une seule courbe agrégée du parc."""
    buckets = {}
    for m in metrics:
        try:
            ts = datetime.fromisoformat(m["horodatage"])
        except Exception:
            continue
        bucket = ts.replace(microsecond=0, second=(ts.second // 10) * 10)
        buckets.setdefault(bucket, []).append(m["valeur"])
    return sorted(
        [(ts, sum(vals) / len(vals)) for ts, vals in buckets.items()],
        key=lambda x: x[0]
    )


def _linear_forecast(series: list, n_forecast: int = 5) -> list:
    """Prolonge une courbe par régression linéaire simple (même principe que
    supervision_service côté back-end), pour l'overlay 'Prédictions IA'."""
    if len(series) < 2:
        return []
    t0 = series[0][0]
    xs = np.array([(t - t0).total_seconds() for t, _ in series])
    ys = np.array([v for _, v in series])
    slope, intercept = np.polyfit(xs, ys, 1)
    step = xs[-1] - xs[-2] if len(xs) >= 2 and xs[-1] != xs[-2] else 10.0
    forecast = []
    for i in range(1, n_forecast + 1):
        t_future = series[-1][0] + pd.Timedelta(seconds=step * i)
        x_future = (t_future - t0).total_seconds()
        y_future = max(0.0, min(100.0, slope * x_future + intercept))
        forecast.append((t_future, y_future))
    return forecast


def _trend_arrow(equipement_id: int) -> str:
    """Petite flèche de tendance CPU basée sur les 2 derniers points connus."""
    pts = api.get_metrics(equipement_id=equipement_id, type_metrique="cpu_percent", limit=2)
    if len(pts) < 2:
        return "<span style='color:var(--on-surface-variant);font-family:var(--font-mono);font-size:11px;'>→ Stable</span>"
    delta = pts[0]["valeur"] - pts[1]["valeur"]
    if delta > 2:
        return f"<span style='color:#ffb4ab;font-family:var(--font-mono);font-size:11px;font-weight:600;'>↑ CPU +{delta:.0f}%</span>"
    if delta < -2:
        return f"<span style='color:#78d8ba;font-family:var(--font-mono);font-size:11px;font-weight:600;'>↓ CPU {delta:.0f}%</span>"
    return "<span style='color:var(--primary, #78d8ba);font-family:var(--font-mono);font-size:11px;font-weight:600;'>→ Stable</span>"


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
            <span class="dash-btn-ghost" style="display:inline-flex;align-items:center;gap:6px;">
                <span style="width:6px;height:6px;border-radius:50%;background:#78d8ba;display:inline-block;"></span>
                DONNÉES EN DIRECT
            </span>
        </div>
        """,
        unsafe_allow_html=True
    )

# ── 5 CARTES KPI SUPÉRIEURES (données réelles) ───────────────────────────────
k1, k2, k3, k4, k5 = st.columns(5)

with k1:
    st.markdown(f"""
    <div class="dash-kpi-card">
        <div class="dash-kpi-title">APPAREILS SURVEILLÉS</div>
        <div class="dash-kpi-value-row">
            <span class="dash-kpi-val">{nb_equipements}</span>
        </div>
    </div>""", unsafe_allow_html=True)

with k2:
    kpi2_class = "dash-kpi-card critical" if nb_alertes_critiques > 0 else "dash-kpi-card"
    kpi2_note = "Action requise" if nb_alertes_critiques > 0 else "Aucune alerte active"
    kpi2_color = "var(--error, #ffb4ab)" if nb_alertes_critiques > 0 else "var(--primary, #78d8ba)"
    st.markdown(f"""
    <div class="{kpi2_class}">
        <div class="dash-kpi-title" style="color: {kpi2_color};">
            <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5">
                <path d="M10.29 3.86L1.82 18a2 2 0 0 0 1.71 3h16.94a2 2 0 0 0 1.71-3L13.71 3.86a2 2 0 0 0-3.42 0z"/>
                <line x1="12" y1="9" x2="12" y2="13"/>
                <line x1="12" y1="17" x2="12.01" y2="17"/>
            </svg>
            ALERTES CRITIQUES
        </div>
        <div class="dash-kpi-value-row">
            <span class="dash-kpi-val" style="color: {kpi2_color};">{nb_alertes_critiques}</span>
        </div>
        <div style="font-family: var(--font-body); font-size: 11px; color: {kpi2_color}; margin-top: 6px; font-weight: 500;">
            {kpi2_note}
        </div>
    </div>""", unsafe_allow_html=True)

with k3:
    st.markdown(f"""
    <div class="dash-kpi-card">
        <div class="dash-kpi-title">SCORE DE SANTÉ MOYEN</div>
        <div class="dash-kpi-value-row">
            <span class="dash-kpi-val" style="color: var(--primary, #78d8ba);">{score_sante_moyen}%</span>
        </div>
    </div>""", unsafe_allow_html=True)

with k4:
    st.markdown(f"""
    <div class="dash-kpi-card">
        <div class="dash-kpi-title">INCIDENTS PRÉDITS</div>
        <div class="dash-kpi-value-row">
            <span class="dash-kpi-val" style="color: var(--secondary, #81d0f8);">{nb_incidents_predits}</span>
            <span style="font-family: var(--font-body); font-size: 11px; color: var(--on-surface-variant, #bdc9c3);">Prochains 7j</span>
        </div>
    </div>""", unsafe_allow_html=True)

with k5:
    st.markdown(f"""
    <div class="dash-kpi-card">
        <div class="dash-kpi-title">CONFORMITÉ RÉSEAU</div>
        <div class="dash-kpi-value-row">
            <span class="dash-kpi-val">{conformite_reseau}%</span>
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

    cpu_metrics = api.get_metrics(type_metrique="cpu_percent", limit=200)
    ram_metrics = api.get_metrics(type_metrique="ram_percent", limit=200)
    cpu_series = _resample_avg(cpu_metrics)[-15:]
    ram_series = _resample_avg(ram_metrics)[-15:]

    if not cpu_series and not ram_series:
        st.info("Pas encore assez de télémétrie collectée par le scheduler — réessayez dans quelques secondes.")
    else:
        fig = go.Figure()

        if cpu_series:
            fig.add_trace(go.Scatter(
                x=[t for t, _ in cpu_series], y=[v for _, v in cpu_series],
                name="CPU", mode="lines",
                line=dict(color="#78d8ba", width=2.5),
                fill="tozeroy", fillcolor="rgba(120, 216, 186, 0.08)",
                showlegend=False
            ))

        if ram_series:
            fig.add_trace(go.Scatter(
                x=[t for t, _ in ram_series], y=[v for _, v in ram_series],
                name="RAM", mode="lines",
                line=dict(color="#81d0f8", width=2.5),
                fill="tozeroy", fillcolor="rgba(129, 208, 248, 0.06)",
                showlegend=False
            ))

        cpu_forecast = _linear_forecast(cpu_series)
        if cpu_series and cpu_forecast:
            fx = [cpu_series[-1][0]] + [t for t, _ in cpu_forecast]
            fy = [cpu_series[-1][1]] + [v for _, v in cpu_forecast]
            fig.add_trace(go.Scatter(
                x=fx, y=fy, name="Prédictions IA", mode="lines+markers",
                line=dict(color="#78d8ba", width=2, dash="dash"),
                marker=dict(symbol="circle-open", size=6, color="#78d8ba"),
                showlegend=False
            ))
            fig.add_shape(
                type="line",
                x0=cpu_series[-1][0], x1=cpu_series[-1][0],
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
                tickformat="%H:%M:%S",
                tickfont=dict(size=10, family="JetBrains Mono"),
                color="#87938e",
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
        st.plotly_chart(fig, width="stretch", config={"displayModeBar": False})

with col_alerts:
    st.markdown("""
    <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:12px;">
        <div style="font-family: var(--font-mono, monospace); font-size: 11px; font-weight: 600; letter-spacing: 0.05em; color: var(--on-surface-variant, #bdc9c3); text-transform: uppercase;">
            FLUX D'ALERTES ACTIVES
        </div>
    </div>
    """, unsafe_allow_html=True)

    icones_module = {"securite": "🛡️ Sécurité", "supervision": "📈 Supervision", "netdevops": "🖧 NetDevOps", "parc": "🖥️ Parc"}

    if not alertes_actives:
        st.markdown("""
        <div class="dash-alert-card">
            <div class="dash-alert-title">Aucune alerte active</div>
            <div class="dash-alert-desc">Le parc est actuellement dans un état nominal.</div>
        </div>
        """, unsafe_allow_html=True)
    else:
        alert_cards_html = ""
        for a in alertes_actives[:5]:
            severite = a.get("severite", "info")
            css_class = "critical" if severite == "critique" else ("warning" if severite == "warning" else "")
            badge_class = "dash-badge-crit" if severite == "critique" else "dash-badge-warn"
            badge_label = severite.upper()
            tag = icones_module.get(a.get("module_origine", ""), a.get("module_origine", ""))
            alert_cards_html += f"""
            <div class="dash-alert-card {css_class}">
                <div class="dash-alert-top">
                    <span class="{badge_class}">{badge_label}</span>
                    <span class="dash-alert-time">{_time_ago(a.get("date_creation", ""))}</span>
                </div>
                <div class="dash-alert-title">{a.get("type", "")}</div>
                <div class="dash-alert-desc">{a.get("message", "")}</div>
                <div><span class="dash-alert-tag">{tag}</span></div>
            </div>
            """
        st.markdown(alert_cards_html, unsafe_allow_html=True)

st.markdown("<div style='height: 16px;'></div>", unsafe_allow_html=True)

# ── SECTION INFÉRIEURE : STATUT DES ÉQUIPEMENTS + RÉPARTITION DU PARC ────────
col_tbl, col_pie = st.columns([2.1, 1])

TYPE_ICONS = {"Switch": "🖧 Switch", "Routeur": "📡 Routeur", "Serveur": "🖥 Serveur", "Workstation": "💻 Poste"}

with col_tbl:
    st.markdown(
        """
        <div style="font-family: var(--font-mono, monospace); font-size: 11px; font-weight: 600; letter-spacing: 0.05em; color: var(--on-surface-variant, #bdc9c3); text-transform: uppercase; margin-bottom: 12px;">
            STATUT DES ÉQUIPEMENTS (LES PLUS DÉGRADÉS D'ABORD)
        </div>
        """,
        unsafe_allow_html=True
    )

    if not equipements:
        st.info("Aucun équipement en base pour le moment.")
    else:
        equipements_tries = sorted(equipements, key=lambda e: e["health_score"])[:5]
        rows = []
        for e in equipements_tries:
            score = e["health_score"]
            if score < 60:
                statut_html = '<span style="display:inline-flex;align-items:center;gap:6px;background:rgba(147,0,10,0.3);color:#ffdad6;padding:3px 10px;border-radius:12px;font-family:var(--font-mono);font-size:11px;font-weight:600;"><span style="width:6px;height:6px;border-radius:50%;background:#ffb4ab;"></span>CRITIQUE</span>'
            elif score < 85:
                statut_html = '<span style="display:inline-flex;align-items:center;gap:6px;background:rgba(102,77,3,0.3);color:#ffe082;padding:3px 10px;border-radius:12px;font-family:var(--font-mono);font-size:11px;font-weight:600;"><span style="width:6px;height:6px;border-radius:50%;background:#ffe082;"></span>WARNING</span>'
            else:
                statut_html = '<span style="display:inline-flex;align-items:center;gap:6px;background:rgba(0,107,85,0.3);color:#78d8ba;padding:3px 10px;border-radius:12px;font-family:var(--font-mono);font-size:11px;font-weight:600;"><span style="width:6px;height:6px;border-radius:50%;background:#78d8ba;"></span>NORMAL</span>'

            rows.append({
                "STATUT": statut_html,
                "ÉQUIPEMENT": f"<b>{e['nom']}</b>",
                "TYPE": f"<span style='color:var(--on-surface-variant);'>{TYPE_ICONS.get(e['type'], e['type'])}</span>",
                "IP / LOCALISATION": mono(e["ip"]),
                "TENDANCE": _trend_arrow(e["id"]),
            })
        df = pd.DataFrame(rows)
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
    if not equipements:
        st.info("Aucun équipement en base pour le moment.")
    else:
        from collections import Counter
        type_counts = Counter(e["type"] for e in equipements)
        df_d = pd.DataFrame({"Type": list(type_counts.keys()), "n": list(type_counts.values())})
        fig_d = px.pie(
            df_d, names="Type", values="n", hole=0.72,
            color_discrete_sequence=["#78d8ba", "#81d0f8", "#a7c8ff", "#3da186", "#c65d47"]
        )
        fig_d.update_traces(textposition="none", hoverinfo="label+percent+value")
        fig_d.add_annotation(
            text=f"<b style='font-size:19px;'>{nb_equipements}</b><br><span style='font-size:10px;letter-spacing:0.08em;color:#bdc9c3;'>TOTAL</span>",
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
        st.plotly_chart(fig_d, width="stretch", config={"displayModeBar": False})
