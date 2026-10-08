"""
3_Supervision.py — Sentinelle AIOps (étape 5.1 : branchement sur le vrai back-end)

Toutes les données proviennent de l'API (api_client) :
    - la pire prédiction TTF réelle (get_predictions) pilote la carte "Prédiction critique"
      et la liste "Urgence Maintenance" ;
    - les seuils affichés (95 % de saturation, fenêtre d'alerte 48h/24h) sont ceux réellement
      utilisés par supervision_service côté back-end — affichés en lecture seule, non éditables
      ici (le moteur ne les expose pas encore via l'API) ;
    - les 4 graphiques de télémétrie (CPU, RAM, Disque, Réseau) sont tracés à partir des vraies
      métriques de l'équipement sélectionné, avec une projection linéaire (même principe que le
      calcul de TTF côté serveur) pour la partie pointillée.
"""
import os, sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

import numpy as np
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
import api_client as api

# ── Garde d'authentification ─────────────────────────────────────────────────
if not st.session_state.get("authenticated", False):
    st.switch_page("app.py")

page_bootstrap(
    active="Supervision",
    page_title="Supervision & Analyses Prédictives",
    search_placeholder="Search hosts, metrics, logs (Cmd+K)...",
)

# ── Constantes reflétant le moteur de supervision (app/services/supervision_service.py) ──────
CRITICAL_THRESHOLD = 95.0     # % : niveau de saturation utilisé pour extrapoler le TTF
ALERT_HORIZON_H = 48.0        # heures : au-delà, la prédiction n'est plus jugée urgente
CRITICAL_TTF_H = 24.0         # heures : en-dessous, la sévérité est "critique" plutôt que "élevée"
RECENT_WINDOW = timedelta(minutes=10)   # une prédiction plus ancienne n'est plus considérée active

METRIC_TYPES = ["cpu_percent", "ram_percent", "disk_percent", "bandwidth_mbps"]
METRIC_LABELS = {"cpu_percent": "CPU Utilization", "ram_percent": "RAM Usage",
                 "disk_percent": "Disk I/O & Fill", "bandwidth_mbps": "Network Traffic"}
METRIC_COLORS = {"cpu_percent": "#78d8ba", "ram_percent": "#78d8ba",
                 "disk_percent": "#78d8ba", "bandwidth_mbps": "#81d0f8"}


def _fmt_value(metric: str, value: float) -> str:
    return f"{value:.1f} Mbps" if metric == "bandwidth_mbps" else f"{value:.1f}%"


def _fmt_ttf(hours: float) -> str:
    if hours < 1:
        return f"{max(1, round(hours * 60))} min"
    if hours < 24:
        return f"{hours:.1f} h"
    return f"{int(hours // 24)}j {int(hours % 24):02d}h"


def _severity(hours: float) -> tuple[str, str]:
    """(libellé, couleur) — mêmes seuils que la sévérité d'alerte côté back-end, complétés
    par deux paliers d'affichage (moyenne/faible) pour la liste Urgence Maintenance."""
    if hours < CRITICAL_TTF_H:
        return "CRITIQUE", "#ffb4ab"
    if hours < ALERT_HORIZON_H:
        return "ÉLEVÉE", "#d37768"
    if hours < 24 * 7:
        return "MOYENNE", "#81d0f8"
    return "FAIBLE", "rgba(120, 216, 186, 0.9)"


def _latest_predictions(predictions: list[dict], now: datetime) -> list[dict]:
    """Une entrée par (équipement, métrique) — la plus récente — filtrée aux prédictions
    encore fraîches (calculées il y a moins de RECENT_WINDOW), triée par TTF croissant."""
    latest: dict[tuple, dict] = {}
    for p in predictions:
        key = (p["equipement_id"], p["metrique"])
        if key not in latest or p["date_calcul"] > latest[key]["date_calcul"]:
            latest[key] = p
    fresh = []
    for p in latest.values():
        try:
            calc = datetime.fromisoformat(p["date_calcul"])
        except (KeyError, ValueError):
            continue
        if now - calc <= RECENT_WINDOW:
            fresh.append(p)
    return sorted(fresh, key=lambda p: p["ttf_estime"])


def _series(equipement_id: int, metric: str, limit: int = 60) -> list[float]:
    rows = api.get_metrics(equipement_id=equipement_id, type_metrique=metric, limit=limit)
    rows = sorted(rows, key=lambda m: m["horodatage"])   # l'API renvoie du plus récent au plus ancien
    return [m["valeur"] for m in rows]


def _forecast(values: list[float], metric: str, n: int = 5) -> list[float]:
    """Prolonge la série par régression linéaire (même principe que supervision_service.calculate_ttf)."""
    if len(values) < 5:
        return []
    xs = np.arange(len(values), dtype=float)
    slope, intercept = np.polyfit(xs, values, 1)
    upper = 100.0 if metric != "bandwidth_mbps" else 1000.0
    return [max(0.0, min(upper, slope * (len(values) - 1 + i) + intercept)) for i in range(1, n + 1)]


# ── Données ───────────────────────────────────────────────────────────────────
equipements = api.get_equipements()
names = {e["id"]: e["nom"] for e in equipements}
now = datetime.now(timezone.utc).replace(tzinfo=None)
predictions = _latest_predictions(api.get_predictions(), now)
worst = predictions[0] if predictions else None

# ── STYLES DÉDIÉS SUPERVISION ────────────────────────────────────────────────
st.html("""
<style>
.sup-card-critical, .sup-card-nominal {
    background-color: var(--surface-container, #1c211e);
    border-radius: 12px; padding: 24px; position: relative; overflow: hidden;
    display: flex; flex-direction: column; justify-content: space-between; min-height: 230px;
}
.sup-card-critical { border: 1px solid var(--error, #ffb4ab); box-shadow: 0 0 15px rgba(255, 180, 171, 0.15); }
.sup-card-nominal { border: 1px solid var(--primary, #78d8ba); box-shadow: 0 0 15px rgba(120, 216, 186, 0.12); }
.sup-glow-bg { position: absolute; top: -40px; right: -40px; width: 160px; height: 160px; border-radius: 50%; filter: blur(40px); pointer-events: none; }
.sup-glow-critical { background: rgba(255, 180, 171, 0.18); }
.sup-glow-nominal { background: rgba(120, 216, 186, 0.16); }
.sup-card-config { background-color: var(--surface-container, #1c211e); border: 1px solid rgba(255,255,255,0.08); border-radius: 12px; padding: 20px; display: flex; flex-direction: column; justify-content: space-between; min-height: 230px; }
.config-header, .urgency-header { font-family: var(--font-headline, 'Inter', sans-serif); font-size: 15px; font-weight: 600; color: var(--on-surface, #dfe4e0); display: flex; align-items: center; gap: 8px; padding-bottom: 12px; border-bottom: 1px solid rgba(255,255,255,0.08); margin-bottom: 16px; }
.sup-card-projections { background-color: var(--surface-container, #1c211e); border: 1px solid rgba(255,255,255,0.08); border-radius: 12px; padding: 20px; }
.chart-box, .chart-box-critical { background-color: var(--surface-container-low, #181d1b); border-radius: 8px; padding: 14px; display: flex; flex-direction: column; }
.chart-box { border: 1px solid rgba(255,255,255,0.08); }
.chart-box-critical { border: 1px solid rgba(255, 180, 171, 0.4); box-shadow: inset 0 0 20px rgba(255, 180, 171, 0.05); }
.sup-card-urgency { background-color: var(--surface-container, #1c211e); border: 1px solid rgba(255,255,255,0.08); border-radius: 12px; padding: 20px; display: flex; flex-direction: column; height: 100%; }
.urgency-item { background-color: var(--surface-container-high, #262b29); border-radius: 0 8px 8px 0; padding: 12px 14px; margin-bottom: 10px; }
.threshold-row { display: flex; justify-content: space-between; align-items: center; font-size: 12px; margin-bottom: 6px; }
.threshold-bar { position: relative; width: 100%; height: 4px; background: var(--surface-container-highest); border-radius: 2px; margin-bottom: 14px; }
.threshold-fill { position: absolute; left: 0; top: 0; height: 100%; border-radius: 2px; }
</style>
""")

# ── EN-TÊTE DE PAGE ──────────────────────────────────────────────────────────
st.html("""
<div style="margin-bottom: 20px;">
    <div style="display: flex; align-items: center; gap: 6px; font-family: var(--font-body); font-size: 12px; color: var(--on-surface-variant, #bdc9c3); margin-bottom: 6px;">
        <span>Home</span>
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
""")

col_main, col_side = st.columns([2.8, 1.0])

with col_main:
    c_hero, c_conf = st.columns([1.8, 1.0])

    with c_hero:
        if worst is not None:
            eq_nom = names.get(worst["equipement_id"], f"#{worst['equipement_id']}")
            metric_lbl = METRIC_LABELS.get(worst["metrique"], worst["metrique"])
            st.html(f"""
            <div class="sup-card-critical">
                <div class="sup-glow-bg sup-glow-critical"></div>
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
                        {eq_nom} : saturation {metric_lbl.lower()} estimée
                    </div>
                    <div style="font-family: var(--font-body); font-size: 13px; color: var(--on-surface-variant, #bdc9c3); line-height: 1.4;">
                        La tendance de télémétrie indique un remplissage à {CRITICAL_THRESHOLD:.0f}% imminent. Action requise.
                    </div>
                </div>
                <div style="position: relative; z-index: 10; border-top: 1px solid rgba(255, 180, 171, 0.2); padding-top: 14px; margin-top: 16px;">
                    <div style="font-family: var(--font-body); font-size: 12px; color: var(--on-surface-variant, #bdc9c3); margin-bottom: 2px;">
                        Time-To-Failure Estimé
                    </div>
                    <div style="font-family: var(--font-mono, 'IBM Plex Sans'); font-size: 28px; font-weight: 700; color: var(--error, #ffb4ab); line-height: 1.1;">
                        {_fmt_ttf(worst["ttf_estime"])}
                    </div>
                </div>
            </div>
            """)
        else:
            st.html("""
            <div class="sup-card-nominal">
                <div class="sup-glow-bg sup-glow-nominal"></div>
                <div style="position: relative; z-index: 10;">
                    <div style="display: flex; align-items: center; gap: 6px; margin-bottom: 6px;">
                        <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="#78d8ba" stroke-width="2.5"><path d="M20 6 9 17l-5-5"/></svg>
                        <span style="font-family: var(--font-mono); font-size: 11px; font-weight: 700; color: var(--primary, #78d8ba); letter-spacing: 0.08em; text-transform: uppercase;">
                            SITUATION NOMINALE
                        </span>
                    </div>
                    <div style="font-family: var(--font-headline); font-size: 20px; font-weight: 700; color: var(--on-surface, #dfe4e0); margin-bottom: 4px;">
                        Aucune saturation critique prévue
                    </div>
                    <div style="font-family: var(--font-body); font-size: 13px; color: var(--on-surface-variant, #bdc9c3); line-height: 1.4;">
                        La tendance de télémétrie est stable sur l'ensemble du parc supervisé (horizon 48h).
                    </div>
                </div>
            </div>
            """)

    with c_conf:
        st.html(f"""
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
            <div>
                <div class="threshold-row">
                    <span style="color: var(--on-surface-variant, #bdc9c3);">Seuil de saturation</span>
                    <span style="font-family: var(--font-mono); font-size: 11px; font-weight: 700; color: #ffb4ab; background: rgba(255,180,171,0.15); padding: 1px 6px; border-radius: 4px; border: 1px solid rgba(255,180,171,0.3);">{CRITICAL_THRESHOLD:.0f}%</span>
                </div>
                <div class="threshold-bar"><div class="threshold-fill" style="width: {CRITICAL_THRESHOLD:.0f}%; background: #ffb4ab;"></div></div>
                <div class="threshold-row">
                    <span style="color: var(--on-surface-variant, #bdc9c3);">Fenêtre d'alerte préventive</span>
                    <span style="font-family: var(--font-mono); font-size: 11px; font-weight: 700; color: #d37768; background: rgba(211,119,104,0.15); padding: 1px 6px; border-radius: 4px; border: 1px solid rgba(211,119,104,0.3);">{ALERT_HORIZON_H:.0f}h</span>
                </div>
                <div style="font-size: 11px; color: var(--on-surface-variant, #bdc9c3); margin-bottom: 4px;">Sévérité CRITIQUE si TTF &lt; {CRITICAL_TTF_H:.0f}h</div>
            </div>
            <div style="text-align: right; padding-top: 10px; border-top: 1px solid rgba(255,255,255,0.08); margin-top: 10px;">
                <span style="font-family: var(--font-body); font-size: 11px; color: var(--on-surface-variant, #bdc9c3);">
                    Valeurs du moteur de supervision (lecture seule)
                </span>
            </div>
        </div>
        """)

    st.html("<div style='height: 16px;'></div>")

    st.html("""
    <div class="sup-card-projections">
        <div style="display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 12px; margin-bottom: 16px;">
            <div style="font-family: var(--font-headline); font-size: 16px; font-weight: 600; color: var(--on-surface, #dfe4e0);">
                Projections des Télémétries Systèmes
            </div>
            <div style="display: flex; align-items: center; gap: 16px; font-size: 12px;">
                <div style="display: flex; align-items: center; gap: 6px; color: var(--on-surface-variant, #bdc9c3);">
                    <span style="width: 14px; height: 2px; background: var(--primary, #78d8ba); border-radius: 1px;"></span> Historique
                </div>
                <div style="display: flex; align-items: center; gap: 6px; color: var(--on-surface-variant, #bdc9c3);">
                    <span style="width: 14px; height: 0px; border-top: 2px dashed #d37768;"></span> Zone de prédiction
                </div>
            </div>
        </div>
    """)

    if equipements:
        options = [e["id"] for e in equipements]
        default_id = worst["equipement_id"] if worst else options[0]
        sel_id = st.selectbox(
            "Équipement", options=options, index=options.index(default_id),
            format_func=lambda i: names.get(i, f"#{i}"), key="sup_selected_eq", label_visibility="collapsed",
        )

        rows = [(0, 0), (0, 1), (1, 0), (1, 1)]
        grid_cols = [st.columns(2), None]
        grid_cols[0:1] = [st.columns(2), st.columns(2)]
        for (r, c), metric in zip([(0, 0), (0, 1), (1, 0), (1, 1)], METRIC_TYPES):
            container = grid_cols[r][c]
            with container:
                values = _series(sel_id, metric)
                forecast = _forecast(values, metric)
                current = _fmt_value(metric, values[-1]) if values else "—"
                is_critical = metric == "disk_percent" and values and values[-1] >= 90
                box_class = "chart-box-critical" if is_critical else "chart-box"
                color = "#ffb4ab" if is_critical else METRIC_COLORS[metric]
                st.html(f"""
                <div class="{box_class}">
                    <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 6px;">
                        <span style="font-family: var(--font-body); font-size: 13px; font-weight: 600; color: var(--on-surface, #dfe4e0);">{METRIC_LABELS[metric]}</span>
                        <span style="font-family: var(--font-mono); font-size: 12px; font-weight: 700; color: {color};">{current}</span>
                    </div>
                """)
                if values:
                    hist = values[-15:]
                    kwargs = {}
                    if metric == "disk_percent":
                        kwargs = {"threshold": 100, "threshold_label": "100% Saturation"}
                    trend_chart(history=hist, forecast=forecast, color=METRIC_COLORS[metric], view_w=350, view_h=110, **kwargs)
                else:
                    st.caption("Pas encore assez de télémétrie collectée — réessayez dans quelques secondes.")
                st.html("</div>")
            if r == 1 and c == 1:
                pass
    else:
        st.info("Aucun équipement enregistré dans l'inventaire.")

    st.html("</div>")

with col_side:
    items_html = "".join(
        f"""
        <div class="urgency-item" style="border-left: 4px solid {_severity(p['ttf_estime'])[1]};">
            <div style="display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 2px;">
                <span style="font-family: var(--font-mono); font-size: 13px; font-weight: 600; color: #dfe4e0;">{names.get(p['equipement_id'], f"#{p['equipement_id']}")}</span>
                <span style="font-family: var(--font-mono); font-size: 10px; font-weight: 700; color: {_severity(p['ttf_estime'])[1]}; background: rgba(0,0,0,0.15); padding: 1px 6px; border-radius: 4px; border: 1px solid {_severity(p['ttf_estime'])[1]}; letter-spacing: 0.05em;">{_severity(p['ttf_estime'])[0]}</span>
            </div>
            <div style="font-family: var(--font-body); font-size: 12px; color: var(--on-surface-variant, #bdc9c3); margin-bottom: 6px;">
                Saturation {METRIC_LABELS.get(p['metrique'], p['metrique']).lower()} prévue
            </div>
            <div style="display: flex; align-items: center; gap: 4px; font-family: var(--font-mono); font-size: 12px; color: {_severity(p['ttf_estime'])[1]};">
                <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><circle cx="12" cy="12" r="10"/><polyline points="12 6 12 12 16 14"/></svg>
                <span>{_fmt_ttf(p['ttf_estime'])}</span>
            </div>
        </div>
        """
        for p in predictions[:6]
    )
    if not items_html:
        items_html = """
        <div style="text-align: center; padding: 24px 8px; color: var(--on-surface-variant, #bdc9c3); font-size: 13px;">
            ✅ Aucune maintenance urgente prévue.
        </div>
        """
    st.html(f"""
    <div class="sup-card-urgency">
        <div class="urgency-header">
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="#ffb4ab" stroke-width="2.5">
                <circle cx="12" cy="12" r="10"/><line x1="12" y1="8" x2="12" y2="12"/><line x1="12" y1="16" x2="12.01" y2="16"/>
            </svg>
            Urgence Maintenance
        </div>
        <div style="display: flex; flex-direction: column; gap: 10px;">
            {items_html}
        </div>
    </div>
    """)
