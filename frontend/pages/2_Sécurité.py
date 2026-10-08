"""
2_Sécurité.py — Sentinelle AIOps
Pixel-perfect ref : Ecrans_Reference/Securite/code.html + screen.png
Sources : DESIGN.md (tokens) + code.html (DOM & layout) + screen.png (vérification visuelle)
"""
import os, sys
from pathlib import Path
from datetime import datetime, timezone
import streamlit as st

_LOGO_PATH = str(Path(__file__).parent.parent / "static" / "logo.png")

st.set_page_config(
    page_title="Sécurité Overview — Sentinelle AIOps",
    page_icon=_LOGO_PATH,
    layout="wide",
    initial_sidebar_state="expanded",
)

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from page_template import page_bootstrap
import api_client as api

# ── Garde d'authentification ─────────────────────────────────────────────────
if not st.session_state.get("authenticated", False):
    st.switch_page("app.py")

page_bootstrap(
    active="Sécurité",
    page_title="Sécurité Overview",
    search_placeholder="Search threats, IPs, policies..."
)

# ── Données réelles (API) ─────────────────────────────────────────────────────
events = api.get_security_events(limit=50)
alertes_securite = api.get_alertes()
alertes_securite = [a for a in alertes_securite if a.get("module_origine") == "securite"]
audits = api.get_audits()

nb_critical = sum(1 for e in events if e.get("severite") == "critique")
nb_anomalies = sum(1 for e in events if e.get("severite") == "warning")
ips_critiques = {e["source_ip"] for e in events if e.get("severite") == "critique"}

now = datetime.now(timezone.utc).replace(tzinfo=None)


def _events_per_sec(evts: list, window_seconds: int = 60) -> float:
    """Débit d'événements/seconde sur la dernière fenêtre glissante."""
    count = 0
    for e in evts:
        try:
            dt = datetime.fromisoformat(e["horodatage"])
        except Exception:
            continue
        if (now - dt).total_seconds() <= window_seconds:
            count += 1
    return round(count / window_seconds, 2)


events_per_sec = _events_per_sec(events)

nb_alertes_securite = len(alertes_securite)
nb_alertes_traitees = sum(1 for a in alertes_securite if a.get("statut") != "active")
block_rate = round(100 * nb_alertes_traitees / nb_alertes_securite) if nb_alertes_securite else 100

# CIS Benchmark : 3 règles surveillées, regroupées en 3 catégories (cf.
# netdevops_service.CIS_RULES) pour retrouver l'esprit du radar Identity/
# Network/Data du mockup original, sans inventer de données.
CATEGORIES = {
    "Identity & Access": "CIS-1.1",   # Password Encryption
    "Network Config": "CIS-2.2",      # SNMP v1/v2
    "Data Protection": "CIS-3.1",     # Bannière légale MOTD
}
WEIGHT = {"elevee": 35, "moyenne": 15, "faible": 5}


def _categorie_score(prefix: str) -> int:
    non_corriges = [
        a for a in audits
        if a.get("regle_cis", "").startswith(prefix) and a.get("statut") != "corrige"
    ]
    penalite = sum(WEIGHT.get(a.get("criticite"), 10) for a in non_corriges)
    return max(0, 100 - penalite)


scores_categories = {nom: _categorie_score(prefix) for nom, prefix in CATEGORIES.items()}
cis_compliant_global = round(sum(scores_categories.values()) / len(scores_categories)) if scores_categories else 100

# ── STYLES DÉDIÉS SÉCURITÉ ───────────────────────────────────────────────────
st.html("""
<style>
/* Animation de pulsation pour la cible critique */
@keyframes pulse-critical {
    0%, 100% { opacity: 1; box-shadow: 0 0 8px 0 rgba(255, 180, 171, 0.5); }
    50% { opacity: 0.7; box-shadow: 0 0 18px 4px rgba(255, 180, 171, 0.9); }
}
.pulse-critical {
    animation: pulse-critical 2s cubic-bezier(0.4, 0, 0.6, 1) infinite;
}

/* Boutons d'en-tête */
.sec-btn-isolate {
    display: inline-flex;
    align-items: center;
    gap: 8px;
    background: transparent;
    border: 1px solid var(--secondary, #81d0f8);
    color: var(--secondary, #81d0f8);
    font-family: var(--font-mono, 'JetBrains Mono', monospace);
    font-size: 11px;
    font-weight: 700;
    letter-spacing: 0.05em;
    padding: 8px 18px;
    border-radius: 6px;
    cursor: pointer;
    text-transform: uppercase;
}
.sec-btn-scan {
    display: inline-flex;
    align-items: center;
    gap: 8px;
    background: var(--primary, #78d8ba);
    border: none;
    color: var(--on-primary, #00382b);
    font-family: var(--font-mono, 'JetBrains Mono', monospace);
    font-size: 11px;
    font-weight: 700;
    letter-spacing: 0.05em;
    padding: 8px 20px;
    border-radius: 6px;
    cursor: pointer;
    box-shadow: 0 0 15px rgba(120, 216, 186, 0.25);
    text-transform: uppercase;
}

/* Carte Radar Hero */
.radar-container {
    position: relative;
    background-color: var(--surface-container, #1d2022);
    border: 1px solid var(--border-subtle, rgba(255, 255, 255, 0.08));
    border-radius: 12px;
    overflow: hidden;
    height: 420px;
    display: flex;
    flex-direction: column;
    justify-content: space-between;
}
.radar-header {
    position: relative;
    z-index: 10;
    padding: 14px 18px;
    border-bottom: 1px solid var(--border-subtle, rgba(255, 255, 255, 0.08));
    background: var(--surface-container);
    backdrop-filter: blur(4px);
    display: flex;
    justify-content: space-between;
    align-items: center;
}
.radar-canvas-area {
    position: absolute;
    top: 0; left: 0; right: 0; bottom: 0;
    display: flex;
    align-items: center;
    justify-content: center;
    overflow: hidden;
}
.radar-grid-bg {
    position: absolute;
    inset: 0;
    opacity: 0.25;
    background-image: radial-gradient(circle at center, #1F8A70 2px, transparent 2.5px);
    background-size: 32px 32px;
    background-position: center;
}
.radar-ring-1 {
    position: absolute;
    width: 600px; height: 600px;
    border-radius: 50%;
    border: 1px solid rgba(120, 216, 186, 0.15);
}
.radar-ring-2 {
    position: absolute;
    width: 400px; height: 400px;
    border-radius: 50%;
    border: 1px solid rgba(120, 216, 186, 0.25);
}
.radar-ring-3 {
    position: absolute;
    width: 200px; height: 200px;
    border-radius: 50%;
    border: 1px solid rgba(120, 216, 186, 0.35);
}
.blip-critical {
    position: absolute;
    top: 30%; left: 60%;
    width: 12px; height: 12px;
    background-color: var(--error, #ffb4ab);
    border-radius: 50%;
    box-shadow: 0 0 10px rgba(255, 180, 171, 0.8);
}
.blip-anomaly-1 {
    position: absolute;
    top: 60%; left: 20%;
    width: 8px; height: 8px;
    background-color: var(--secondary, #81d0f8);
    border-radius: 50%;
    box-shadow: 0 0 8px rgba(129, 208, 248, 0.8);
}
.blip-anomaly-2 {
    position: absolute;
    top: 45%; left: 35%;
    width: 8px; height: 8px;
    background-color: var(--secondary, #81d0f8);
    border-radius: 50%;
    box-shadow: 0 0 8px rgba(129, 208, 248, 0.8);
}
.radar-hud {
    position: relative;
    z-index: 10;
    padding: 16px 20px;
    background: linear-gradient(180deg, transparent 0%, var(--surface-container) 40%, var(--surface-container) 100%);
    display: grid;
    grid-template-columns: 1fr 1fr 1fr;
    gap: 16px;
}
.hud-tile {
    background: var(--surface-container-high);
    backdrop-filter: blur(4px);
    border: 1px solid rgba(255, 255, 255, 0.08);
    border-radius: 8px;
    padding: 12px 14px;
}
.hud-label {
    font-family: var(--font-mono, 'JetBrains Mono', monospace);
    font-size: 11px;
    font-weight: 500;
    color: var(--on-surface-variant, #bdc9c3);
    text-transform: uppercase;
    letter-spacing: 0.05em;
    margin-bottom: 4px;
}
.hud-value {
    font-family: var(--font-mono, 'JetBrains Mono', monospace);
    font-size: 28px;
    font-weight: 600;
    line-height: 1.1;
}

/* Carte Benchmarks */
.bench-card {
    background-color: var(--surface-container, #1d2022);
    border: 1px solid var(--border-subtle, rgba(255, 255, 255, 0.08));
    border-radius: 12px;
    padding: 20px;
    height: 420px;
    display: flex;
    flex-direction: column;
    justify-content: space-between;
}
.progress-bar-bg {
    width: 100%;
    height: 6px;
    background-color: rgba(255, 255, 255, 0.08);
    border-radius: 9999px;
    overflow: hidden;
    margin-top: 6px;
}

/* Tableau d'incidents */
.incidents-card {
    background-color: var(--surface-container, #1d2022);
    border: 1px solid var(--border-subtle, rgba(255, 255, 255, 0.08));
    border-radius: 12px;
    overflow: hidden;
}
.incidents-header {
    padding: 14px 20px;
    border-bottom: 1px solid var(--border-subtle, rgba(255, 255, 255, 0.08));
    background: var(--surface-container-low);
    display: flex;
    justify-content: space-between;
    align-items: center;
}
.sec-table {
    width: 100%;
    border-collapse: collapse;
    font-family: var(--font-body, 'Inter', sans-serif);
    font-size: 13px;
}
.sec-table th {
    padding: 12px 18px;
    font-family: var(--font-mono, 'JetBrains Mono', monospace);
    font-size: 11px;
    font-weight: 600;
    color: var(--on-surface-variant, #bdc9c3);
    text-transform: uppercase;
    letter-spacing: 0.05em;
    background: var(--surface-container-high);
    border-bottom: 1px solid var(--border-subtle, rgba(255, 255, 255, 0.08));
    text-align: left;
}
.sec-table td {
    padding: 14px 18px;
    border-bottom: 1px solid rgba(255, 255, 255, 0.04);
    vertical-align: middle;
    color: var(--on-surface, #e0e3e6);
}
.sec-table tr.critical-row {
    background: rgba(147, 0, 10, 0.12);
    border-left: 3px solid var(--error, #ffb4ab);
}
.sec-table tr:hover:not(.critical-row) {
    background: rgba(255, 255, 255, 0.02);
}
.btn-investigate {
    padding: 5px 14px;
    background: var(--surface, #101416);
    border: 1px solid rgba(255, 255, 255, 0.15);
    border-radius: 4px;
    color: var(--on-surface, #e0e3e6);
    font-family: var(--font-mono, monospace);
    font-size: 11px;
    font-weight: 500;
    cursor: pointer;
}
.btn-investigate:hover {
    border-color: var(--primary, #78d8ba);
    color: var(--primary, #78d8ba);
}
</style>
""")

# ── EN-TÊTE DE PAGE + ACTIONS ────────────────────────────────────────────────
tc, bc = st.columns([3, 1])
with tc:
    st.html(
        """
        <div style="margin-bottom: 20px;">
            <div style="font-family: var(--font-display, 'IBM Plex Sans'); font-size: 28px; font-weight: 600; color: var(--on-surface, #e0e3e6); line-height: 1.2;">
                Sécurité Overview
            </div>
            <div style="font-family: var(--font-body, 'Inter'); font-size: 14px; color: var(--on-surface-variant, #bdc9c3); margin-top: 4px;">
                Real-time threat detection and posture analysis.
            </div>
        </div>
        """
    )
with bc:
    st.html(
        """
        <div style="display: flex; gap: 12px; justify-content: flex-end; align-items: center; padding-top: 6px;">
            <button class="sec-btn-isolate">
                <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5">
                    <path d="M10.29 3.86L1.82 18a2 2 0 0 0 1.71 3h16.94a2 2 0 0 0 1.71-3L13.71 3.86a2 2 0 0 0-3.42 0z"/>
                    <line x1="12" y1="9" x2="12" y2="13"/>
                    <line x1="12" y1="17" x2="12.01" y2="17"/>
                </svg>
                ISOLATE DEVICE
            </button>
            <button class="sec-btn-scan">
                <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5">
                    <circle cx="12" cy="12" r="10"/>
                    <circle cx="12" cy="12" r="6"/>
                    <circle cx="12" cy="12" r="2"/>
                </svg>
                RUN FULL SCAN
            </button>
        </div>
        """
    )

# ── SECTION CENTRALE : RADAR (8 COLS) + BENCHMARKS (4 COLS) ──────────────────
col_radar, col_bench = st.columns([2.3, 1.1])

with col_radar:
    st.html(
        f"""
        <div class="radar-container">
            <div class="radar-header">
                <div style="display: flex; align-items: center; gap: 8px;">
                    <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="#78d8ba" stroke-width="2">
                        <circle cx="12" cy="12" r="10"/>
                        <line x1="2" y1="12" x2="22" y2="12"/>
                        <path d="M12 2a15.3 15.3 0 0 1 4 10 15.3 15.3 0 0 1-4 10 15.3 15.3 0 0 1-4-10 15.3 15.3 0 0 1 4-10z"/>
                    </svg>
                    <span style="font-family: var(--font-mono); font-size: 11px; font-weight: 600; letter-spacing: 0.05em; color: var(--on-surface); text-transform: uppercase;">
                        GLOBAL THREAT MAP
                    </span>
                </div>
                <div style="display: flex; gap: 16px; align-items: center; font-family: var(--font-mono); font-size: 11px;">
                    <div style="display: flex; align-items: center; gap: 6px;">
                        <span style="width: 8px; height: 8px; border-radius: 50%; background: #ffb4ab;"></span>
                        <span style="color: var(--on-surface-variant);">Critical ({nb_critical})</span>
                    </div>
                    <div style="display: flex; align-items: center; gap: 6px;">
                        <span style="width: 8px; height: 8px; border-radius: 50%; background: #81d0f8;"></span>
                        <span style="color: var(--on-surface-variant);">Anomalies ({nb_anomalies})</span>
                    </div>
                </div>
            </div>

            <div class="radar-canvas-area">
                <div class="radar-grid-bg"></div>
                <div class="radar-ring-1"></div>
                <div class="radar-ring-2"></div>
                <div class="radar-ring-3"></div>
                {'<div class="blip-critical pulse-critical"></div>' if nb_critical > 0 else ''}
                {'<div class="blip-anomaly-1"></div>' if nb_anomalies > 0 else ''}
                {'<div class="blip-anomaly-2"></div>' if nb_anomalies > 1 else ''}
            </div>

            <div class="radar-hud">
                <div class="hud-tile">
                    <div class="hud-label">ACTIVE VECTORS</div>
                    <div class="hud-value" style="color: var(--error, #ffb4ab);">{len(ips_critiques)}</div>
                </div>
                <div class="hud-tile">
                    <div class="hud-label">EVENTS/SEC</div>
                    <div class="hud-value" style="color: var(--primary, #78d8ba);">{events_per_sec}</div>
                </div>
                <div class="hud-tile">
                    <div class="hud-label">BLOCK RATE</div>
                    <div class="hud-value" style="color: var(--secondary, #81d0f8);">{block_rate}%</div>
                </div>
            </div>
        </div>
        """
    )

with col_bench:
    id_access = scores_categories["Identity & Access"]
    net_config = scores_categories["Network Config"]
    data_protect = scores_categories["Data Protection"]

    def _bench_color(score: int) -> str:
        if score >= 85:
            return "var(--primary, #78d8ba)"
        if score >= 70:
            return "var(--secondary, #81d0f8)"
        return "var(--error, #ffb4ab)"

    st.html(
        f"""
        <div class="bench-card">
            <div style="display: flex; align-items: center; gap: 8px;">
                <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="#81d0f8" stroke-width="2">
                    <polyline points="9 11 12 14 22 4"/>
                    <path d="M21 12v7a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h11"/>
                </svg>
                <span style="font-family: var(--font-mono); font-size: 11px; font-weight: 600; letter-spacing: 0.05em; color: var(--on-surface); text-transform: uppercase;">
                    SECURITY BENCHMARKS
                </span>
            </div>

            <div style="width: 140px; height: 140px; border-radius: 50%; background: conic-gradient(var(--primary, #78d8ba) 0% {cis_compliant_global}%, #272a2d {cis_compliant_global}% 100%); display: flex; align-items: center; justify-content: center; margin: 10px auto; padding: 8px;">
                <div style="width: 100%; height: 100%; border-radius: 50%; background-color: var(--surface-container, #1d2022); display: flex; flex-direction: column; align-items: center; justify-content: center;">
                    <div style="font-family: var(--font-mono); font-size: 28px; font-weight: 600; color: var(--on-surface, #e0e3e6); line-height: 1;">
                        {cis_compliant_global}<span style="font-size: 18px; font-weight: 500;">%</span>
                    </div>
                    <div style="font-family: var(--font-mono); font-size: 10px; color: var(--primary, #78d8ba); font-weight: 700; text-transform: uppercase; letter-spacing: 0.05em; margin-top: 4px;">
                        CIS COMPLIANT
                    </div>
                </div>
            </div>

            <div style="display: flex; flex-direction: column; gap: 14px;">
                <div>
                    <div style="display: flex; justify-content: space-between; font-family: var(--font-mono); font-size: 11px;">
                        <span style="color: var(--on-surface-variant);">Identity & Access</span>
                        <span style="color: {_bench_color(id_access)}; font-weight: 600;">{id_access}%</span>
                    </div>
                    <div class="progress-bar-bg">
                        <div style="width: {id_access}%; height: 100%; background-color: {_bench_color(id_access)}; border-radius: 9999px;"></div>
                    </div>
                </div>
                <div>
                    <div style="display: flex; justify-content: space-between; font-family: var(--font-mono); font-size: 11px;">
                        <span style="color: var(--on-surface-variant);">Network Config</span>
                        <span style="color: {_bench_color(net_config)}; font-weight: 600;">{net_config}%</span>
                    </div>
                    <div class="progress-bar-bg">
                        <div style="width: {net_config}%; height: 100%; background-color: {_bench_color(net_config)}; border-radius: 9999px;"></div>
                    </div>
                </div>
                <div>
                    <div style="display: flex; justify-content: space-between; font-family: var(--font-mono); font-size: 11px;">
                        <span style="color: var(--on-surface-variant);">Data Protection</span>
                        <span style="color: {_bench_color(data_protect)}; font-weight: 600;">{data_protect}%</span>
                    </div>
                    <div class="progress-bar-bg">
                        <div style="width: {data_protect}%; height: 100%; background-color: {_bench_color(data_protect)}; border-radius: 9999px;"></div>
                    </div>
                </div>
            </div>
        </div>
        """
    )

st.html("<div style='height: 18px;'></div>")

# ── SECTION INFÉRIEURE : RECENT SECURITY INCIDENTS (PLEINE LARGEUR) ───────────
def _fmt_ts(iso_str: str) -> str:
    try:
        return datetime.fromisoformat(iso_str).strftime("%H:%M:%S UTC")
    except Exception:
        return "—"


SEVERITY_BADGE = {
    "critique": ('rgba(147, 0, 10, 0.4)', 'rgba(255, 180, 171, 0.3)', '#ffdad6', '#ffb4ab', 'CRITICAL'),
    "warning": ('rgba(102, 77, 3, 0.4)', 'rgba(255, 204, 128, 0.3)', '#ffe082', '#ffe082', 'HIGH'),
    "info": ('rgba(1, 112, 148, 0.25)', 'rgba(129, 208, 248, 0.3)', '#81d0f8', '#81d0f8', 'MEDIUM'),
}

if not events:
    incidents_rows_html = """
    <tr>
        <td colspan="6" style="text-align:center; padding: 24px; color: var(--on-surface-variant);">
            Aucun événement de sécurité détecté pour le moment.
        </td>
    </tr>
    """
else:
    incidents_rows_html = ""
    for e in sorted(events, key=lambda x: x.get("horodatage", ""), reverse=True)[:10]:
        severite = e.get("severite", "info")
        bg, border, color, dot, label = SEVERITY_BADGE.get(severite, SEVERITY_BADGE["info"])
        row_class = "critical-row" if severite == "critique" else ""
        if severite == "critique":
            action_html = '<button class="btn-investigate">Investigate</button>'
        else:
            action_html = """
            <span style="font-family: var(--font-mono); font-size: 12px; font-weight: 600; color: var(--primary, #78d8ba); display: inline-flex; align-items: center; gap: 4px;">
                <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5">
                    <polyline points="20 6 9 17 4 12"/>
                </svg>
                Blocked
            </span>
            """
        incidents_rows_html += f"""
        <tr class="{row_class}">
            <td>
                <span style="display: inline-flex; align-items: center; gap: 6px; padding: 3px 8px; border-radius: 4px; background: {bg}; border: 1px solid {border}; color: {color}; font-family: var(--font-mono); font-size: 10px; font-weight: 700; letter-spacing: 0.05em;">
                    <span style="width: 6px; height: 6px; border-radius: 50%; background: {dot};"></span>
                    {label}
                </span>
            </td>
            <td style="font-family: var(--font-mono); font-size: 12px; color: var(--on-surface-variant);">{_fmt_ts(e.get("horodatage", ""))}</td>
            <td style="font-weight: 600; color: var(--on-surface);">{e.get("type_evenement", "")}</td>
            <td style="font-family: var(--font-mono); font-size: 12px; color: var(--on-surface-variant);">{e.get("source_ip", "")}</td>
            <td style="color: var(--on-surface-variant);">{e.get("utilisateur") or "—"}</td>
            <td style="text-align: right;">{action_html}</td>
        </tr>
        """

st.html(
    f"""
    <div class="incidents-card">
        <div class="incidents-header">
            <div style="display: flex; align-items: center; gap: 8px;">
                <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="#ffb4ab" stroke-width="2.5">
                    <path d="M10.29 3.86L1.82 18a2 2 0 0 0 1.71 3h16.94a2 2 0 0 0 1.71-3L13.71 3.86a2 2 0 0 0-3.42 0z"/>
                    <line x1="12" y1="9" x2="12" y2="13"/>
                    <line x1="12" y1="17" x2="12.01" y2="17"/>
                </svg>
                <span style="font-family: var(--font-mono); font-size: 11px; font-weight: 600; letter-spacing: 0.05em; color: var(--on-surface); text-transform: uppercase;">
                    RECENT SECURITY INCIDENTS
                </span>
            </div>
            <span style="font-family: var(--font-mono); font-size: 11px; color: var(--on-surface-variant);">
                {len(events)} événement(s) au total
            </span>
        </div>

        <div style="overflow-x: auto;">
            <table class="sec-table">
                <thead>
                    <tr>
                        <th>SEVERITY</th>
                        <th>TIMESTAMP</th>
                        <th>TYPE</th>
                        <th>SOURCE IP</th>
                        <th>TARGET</th>
                        <th style="text-align: right;">ACTION</th>
                    </tr>
                </thead>
                <tbody>
                    {incidents_rows_html}
                </tbody>
            </table>
        </div>
    </div>
    """
)
