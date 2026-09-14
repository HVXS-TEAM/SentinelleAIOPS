"""
4_NetDevOps.py — Sentinelle AIOps
Pixel-perfect ref : Ecrans_Reference/NetDevOps/code.html + screen.png
Sources : DESIGN.md (tokens) + code.html (DOM & layout) + screen.png (vérification visuelle)
"""
import os, sys
from pathlib import Path
import streamlit as st

_LOGO_PATH = str(Path(__file__).parent.parent / "static" / "logo.png")

st.set_page_config(
    page_title="NetDevOps Automation — Sentinelle AIOps",
    page_icon=_LOGO_PATH,
    layout="wide",
    initial_sidebar_state="expanded",
)

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from page_template import page_bootstrap

# ── Garde d'authentification ─────────────────────────────────────────────────
if not st.session_state.get("authenticated", False):
    st.switch_page("app.py")

page_bootstrap(
    active="NetDevOps",
    page_title="NetDevOps Automation",
    search_placeholder="Cmd+K to search..."
)

# ── STYLES DÉDIÉS NETDEVOPS ──────────────────────────────────────────────────
st.html("""
<style>
/* Cartes conteneurs */
.net-card {
    background-color: var(--surface-container-high, #262b29);
    border: 1px solid rgba(255, 255, 255, 0.08);
    border-radius: 10px;
    padding: 18px;
}

/* Items d'équipement */
.eq-item {
    background-color: var(--surface-container, #1c211e);
    border: 1px solid transparent;
    border-radius: 6px;
    padding: 12px 14px;
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 8px;
    cursor: pointer;
    transition: all 0.15s ease;
}
.eq-item:hover {
    border-color: rgba(255, 255, 255, 0.15);
}
.eq-item.active {
    position: relative;
    border-color: rgba(120, 216, 186, 0.35);
    background-color: var(--surface-container, #1c211e);
    box-shadow: inset 0 0 0 1px rgba(120, 216, 186, 0.5);
}
.eq-item.active::before {
    content: '';
    position: absolute;
    left: 0; top: 0; bottom: 0;
    width: 4px;
    background-color: var(--primary, #78d8ba);
    border-radius: 6px 0 0 6px;
}

/* Badges Score CIS */
.cis-badge-critical {
    background-color: rgba(147, 0, 10, 0.25);
    border: 1px solid rgba(255, 180, 171, 0.3);
    padding: 4px 10px;
    border-radius: 4px;
    display: flex;
    flex-direction: column;
    align-items: flex-end;
}
.cis-badge-healthy {
    background-color: rgba(61, 161, 134, 0.2);
    border: 1px solid rgba(120, 216, 186, 0.3);
    padding: 4px 10px;
    border-radius: 4px;
    display: flex;
    flex-direction: column;
    align-items: flex-end;
}

/* Timeline Historique de Sauvegarde */
.timeline-entry {
    position: relative;
    padding-left: 28px;
    padding-bottom: 16px;
}
.timeline-entry::before {
    content: '';
    position: absolute;
    left: 7px; top: 12px; bottom: -4px;
    width: 1px;
    background: rgba(255, 255, 255, 0.1);
}
.timeline-entry:last-child::before {
    display: none;
}
.timeline-dot {
    position: absolute;
    left: 4px; top: 6px;
    width: 8px; height: 8px;
    border-radius: 50%;
    border: 2px solid var(--surface-container-high);
}

/* Findings Items */
.finding-box {
    padding: 12px;
    border-radius: 6px;
    margin-bottom: 8px;
    cursor: pointer;
    transition: background 0.15s ease;
}
.finding-box.active {
    background-color: var(--surface-container-high);
    border-left: 3px solid var(--error, #ffb4ab);
}
.finding-box:not(.active):hover {
    background-color: var(--surface-container, #1c211e);
}

/* Diff View Côte à Côte */
.diff-container {
    background-color: var(--surface-container-lowest);
    border: 1px solid rgba(255, 255, 255, 0.12);
    border-radius: 6px;
    overflow: hidden;
    display: flex;
    flex-direction: column;
    font-family: var(--font-mono, 'JetBrains Mono', monospace);
    font-size: 12px;
    line-height: 1.5;
    min-width: 0;
    width: 100%;
}
.diff-header {
    display: flex;
    background-color: var(--surface-container, #1c211e);
    border-bottom: 1px solid rgba(255, 255, 255, 0.1);
    font-size: 11px;
}
.diff-body {
    display: flex;
    min-height: 240px;
    overflow-x: auto;
}
.diff-left {
    flex: 1;
    min-width: 0;
    border-right: 1px solid rgba(255, 255, 255, 0.1);
    padding: 12px;
    background-color: rgba(255, 180, 171, 0.03);
    color: var(--on-surface-variant, #bdc9c3);
    white-space: pre-wrap;
    word-break: break-all;
}
.diff-right {
    flex: 1.1;
    min-width: 0;
    padding: 12px;
    background-color: rgba(120, 216, 186, 0.03);
    color: var(--primary);
    white-space: pre-wrap;
    word-break: break-all;
}
.diff-highlight {
    background-color: rgba(120, 216, 186, 0.2);
    color: var(--primary);
    padding: 1px 4px;
    border-radius: 3px;
}

/* Boutons d'action */
.btn-reject {
    padding: 8px 18px;
    border-radius: 6px;
    border: 1px solid var(--outline);
    background: transparent;
    color: var(--on-surface, #dfe4e0);
    font-family: var(--font-body, 'Inter', sans-serif);
    font-size: 13px;
    font-weight: 500;
    cursor: pointer;
    display: inline-flex;
    align-items: center;
    gap: 6px;
    transition: background 0.15s;
}
.btn-reject:hover {
    background: rgba(255, 255, 255, 0.05);
}
.btn-approve {
    padding: 8px 18px;
    border-radius: 6px;
    border: none;
    background: #1F8A70;
    color: #ffffff;
    font-family: var(--font-body, 'Inter', sans-serif);
    font-size: 13px;
    font-weight: 600;
    cursor: pointer;
    display: inline-flex;
    align-items: center;
    gap: 6px;
    box-shadow: 0 2px 10px rgba(31, 138, 112, 0.3);
    transition: background 0.15s;
}
.btn-approve:hover {
    background: #279e82;
}
</style>
""")

# ── EN-TÊTE DE PAGE ──────────────────────────────────────────────────────────
st.html(
    """
    <div style="margin-bottom: 20px;">
        <div style="font-family: var(--font-headline, 'Inter'); font-size: 28px; font-weight: 700; color: var(--on-surface, #dfe4e0); line-height: 1.2;">
            NetDevOps Automation
        </div>
        <div style="font-family: var(--font-body, 'Inter'); font-size: 14px; color: var(--on-surface-variant, #bdc9c3); margin-top: 4px;">
            Audit de conformité CIS &amp; Suggestions d'automatisation IA
        </div>
    </div>
    """
)

# ── DISPOSITION EN 2 COLONNES (4/12 et 8/12) ─────────────────────────────────
col_left, col_right = st.columns([1.2, 2.0])

with col_left:
    # ── CARTE 1 : ÉQUIPEMENTS RÉSEAU ──────────────────────────────────────────
    st.html(
        """
        <div class="net-card" style="margin-bottom: 16px;">
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 14px;">
                <div style="font-family: var(--font-headline); font-size: 16px; font-weight: 600; color: var(--on-surface, #dfe4e0);">
                    Équipements Réseau
                </div>
                <span style="font-family: var(--font-mono); font-size: 11px; color: var(--on-surface-variant); background: var(--surface-container-lowest, #0a0f0d); padding: 2px 8px; border-radius: 4px; border: 1px solid rgba(255, 255, 255, 0.08);">
                    35 total
                </span>
            </div>

            <!-- Item 1: CORE-RTR-01 -->
            <div class="eq-item">
                <div style="display: flex; align-items: center; gap: 10px;">
                    <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="#87938e" stroke-width="2">
                        <rect x="2" y="6" width="20" height="12" rx="2"/>
                        <circle cx="6" cy="12" r="1"/>
                        <circle cx="10" cy="12" r="1"/>
                        <circle cx="14" cy="12" r="1"/>
                    </svg>
                    <div>
                        <div style="font-family: var(--font-mono); font-size: 13px; font-weight: 700; color: var(--on-surface, #dfe4e0);">CORE-RTR-01</div>
                        <div style="display: flex; align-items: center; gap: 6px; font-size: 12px; color: var(--on-surface-variant); margin-top: 2px;">
                            <span style="width: 6px; height: 6px; border-radius: 50%; background-color: var(--error, #ffb4ab);"></span>
                            <span>2 findings</span>
                        </div>
                    </div>
                </div>
                <div class="cis-badge-critical">
                    <span style="font-family: var(--font-mono); font-size: 13px; font-weight: 700; color: var(--error, #ffb4ab);">82%</span>
                    <span style="font-size: 9px; text-transform: uppercase; color: var(--on-surface-variant); letter-spacing: 0.05em;">CIS SCORE</span>
                </div>
            </div>

            <!-- Item 2: DIST-SW-A (ACTIVE) -->
            <div class="eq-item active">
                <div style="display: flex; align-items: center; gap: 10px; padding-left: 4px;">
                    <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="#78d8ba" stroke-width="2">
                        <rect x="2" y="4" width="20" height="16" rx="2"/>
                        <line x1="6" y1="9" x2="6" y2="9.01"/>
                        <line x1="10" y1="9" x2="10" y2="9.01"/>
                        <line x1="14" y1="9" x2="14" y2="9.01"/>
                        <line x1="18" y1="9" x2="18" y2="9.01"/>
                        <line x1="6" y1="15" x2="6" y2="15.01"/>
                        <line x1="10" y1="15" x2="10" y2="15.01"/>
                        <line x1="14" y1="15" x2="14" y2="15.01"/>
                        <line x1="18" y1="15" x2="18" y2="15.01"/>
                    </svg>
                    <div>
                        <div style="font-family: var(--font-mono); font-size: 13px; font-weight: 700; color: var(--primary, #78d8ba);">DIST-SW-A</div>
                        <div style="display: flex; align-items: center; gap: 6px; font-size: 12px; color: var(--on-surface-variant); margin-top: 2px;">
                            <span style="width: 6px; height: 6px; border-radius: 50%; background-color: var(--error, #ffb4ab);"></span>
                            <span>5 findings</span>
                        </div>
                    </div>
                </div>
                <div class="cis-badge-critical">
                    <span style="font-family: var(--font-mono); font-size: 13px; font-weight: 700; color: var(--error, #ffb4ab);">65%</span>
                    <span style="font-size: 9px; text-transform: uppercase; color: var(--on-surface-variant); letter-spacing: 0.05em;">CIS SCORE</span>
                </div>
            </div>

            <!-- Item 3: FW-EXT-02 -->
            <div class="eq-item">
                <div style="display: flex; align-items: center; gap: 10px;">
                    <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="#87938e" stroke-width="2">
                        <path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/>
                    </svg>
                    <div>
                        <div style="font-family: var(--font-mono); font-size: 13px; font-weight: 700; color: var(--on-surface, #dfe4e0);">FW-EXT-02</div>
                        <div style="display: flex; align-items: center; gap: 6px; font-size: 12px; color: var(--on-surface-variant); margin-top: 2px;">
                            <span style="width: 6px; height: 6px; border-radius: 50%; background-color: var(--primary, #78d8ba);"></span>
                            <span style="color: var(--primary, #78d8ba);">Compliant</span>
                        </div>
                    </div>
                </div>
                <div class="cis-badge-healthy">
                    <span style="font-family: var(--font-mono); font-size: 13px; font-weight: 700; color: var(--primary, #78d8ba);">100%</span>
                    <span style="font-size: 9px; text-transform: uppercase; color: var(--on-surface-variant); letter-spacing: 0.05em;">CIS SCORE</span>
                </div>
            </div>
        </div>

        <!-- ── CARTE 2 : HISTORIQUE DE SAUVEGARDE ─────────────────────────────── -->
        <div class="net-card">
            <div style="display: flex; align-items: center; gap: 8px; margin-bottom: 14px;">
                <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                    <circle cx="12" cy="12" r="10"/>
                    <polyline points="12 6 12 12 16 14"/>
                </svg>
                <div style="font-family: var(--font-headline); font-size: 15px; font-weight: 600; color: var(--on-surface, #dfe4e0);">
                    Historique de sauvegarde
                </div>
            </div>

            <!-- Timeline Entry 1 -->
            <div class="timeline-entry">
                <div class="timeline-dot" style="background-color: var(--primary, #78d8ba);"></div>
                <div style="display: flex; justify-content: space-between; align-items: flex-start;">
                    <div>
                        <div style="font-size: 13px; font-weight: 500; color: var(--on-surface, #dfe4e0);">Aujourd'hui 02:00</div>
                        <div style="font-family: var(--font-mono); font-size: 10px; color: var(--on-surface-variant, #bdc9c3); margin-top: 2px;">Hash: 8f9a2b...</div>
                    </div>
                    <a style="font-family: var(--font-body); font-size: 12px; font-weight: 600; color: var(--primary, #78d8ba); cursor: pointer; text-decoration: none; display: flex; align-items: center; gap: 4px;">
                        <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><path d="M3 12a9 9 0 1 0 9-9 9.75 9.75 0 0 0-6.74 2.74L3 8"/><path d="M3 3v5h5"/></svg>
                        Restore
                    </a>
                </div>
            </div>

            <!-- Timeline Entry 2 -->
            <div class="timeline-entry">
                <div class="timeline-dot" style="background-color: #87938e;"></div>
                <div style="display: flex; justify-content: space-between; align-items: flex-start;">
                    <div>
                        <div style="font-size: 13px; color: var(--on-surface-variant, #bdc9c3);">Hier 02:00</div>
                        <div style="font-family: var(--font-mono); font-size: 10px; color: rgba(189, 201, 195, 0.5); margin-top: 2px;">Hash: 3c1d4e...</div>
                    </div>
                    <a style="font-family: var(--font-body); font-size: 12px; color: var(--on-surface-variant, #bdc9c3); cursor: pointer; text-decoration: none; display: flex; align-items: center; gap: 4px;">
                        <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><path d="M3 12a9 9 0 1 0 9-9 9.75 9.75 0 0 0-6.74 2.74L3 8"/><path d="M3 3v5h5"/></svg>
                        Restore
                    </a>
                </div>
            </div>
        </div>
        """
    )

with col_right:
    # ── VOLET AUDIT DÉTAILLÉ & DIFF VIEW ───────────────────────────────────────
    st.html(
        """
        <div class="net-card" style="display: flex; flex-direction: column; justify-content: space-between;">
            <!-- Header du volet -->
            <div style="display: flex; justify-content: space-between; align-items: flex-start; padding-bottom: 14px; border-bottom: 1px solid rgba(255, 255, 255, 0.08); margin-bottom: 16px;">
                <div>
                    <div style="font-family: var(--font-headline); font-size: 18px; font-weight: 700; color: var(--primary, #78d8ba); display: flex; align-items: baseline; gap: 6px;">
                        DIST-SW-A <span style="color: var(--on-surface-variant, #bdc9c3); font-weight: 400; font-size: 15px;">| Détail de l'audit</span>
                    </div>
                    <div style="font-family: var(--font-body); font-size: 12px; color: var(--on-surface-variant, #bdc9c3); margin-top: 2px;">
                        CIS Cisco IOS 15 Benchmark v4.0.0
                    </div>
                </div>
                <div>
                    <span style="background-color: rgba(147, 0, 10, 0.25); color: var(--error, #ffb4ab); border: 1px solid rgba(255, 180, 171, 0.3); padding: 4px 10px; border-radius: 4px; font-family: var(--font-body); font-size: 12px; font-weight: 600; display: inline-flex; align-items: center; gap: 6px;">
                        <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5">
                            <path d="M10.29 3.86L1.82 18a2 2 0 0 0 1.71 3h16.94a2 2 0 0 0 1.71-3L13.71 3.86a2 2 0 0 0-3.42 0z"/>
                            <line x1="12" y1="9" x2="12" y2="13"/>
                            <line x1="12" y1="17" x2="12.01" y2="17"/>
                        </svg>
                        5 Critical Findings
                    </span>
                </div>
            </div>

            <!-- Grille interne : Findings (35%) + Suggestions IA (65%) -->
            <div style="display: grid; grid-template-columns: 1fr 1.9fr; gap: 16px; align-items: stretch;">
                <!-- Colonne Gauche : Liste des Findings -->
                <div style="display: flex; flex-direction: column; gap: 8px; border-right: 1px solid rgba(255, 255, 255, 0.08); padding-right: 12px;">
                    <!-- Finding 1 (ACTIVE) -->
                    <div class="finding-box active">
                        <div style="font-family: var(--font-body); font-size: 13px; font-weight: 600; color: var(--on-surface, #dfe4e0); margin-bottom: 2px;">
                            Plaintext password detected
                        </div>
                        <div style="font-size: 11px; color: var(--on-surface-variant, #bdc9c3); line-height: 1.3;">
                            CIS 1.1.1 Ensure 'service password-encryption' is enabled
                        </div>
                    </div>

                    <!-- Finding 2 -->
                    <div class="finding-box">
                        <div style="font-family: var(--font-body); font-size: 13px; font-weight: 500; color: var(--on-surface-variant, #bdc9c3); margin-bottom: 2px;">
                            SNMP v1 active
                        </div>
                        <div style="font-size: 11px; color: rgba(189, 201, 195, 0.6); line-height: 1.3;">
                            CIS 4.2.1 Disable SNMPv1/v2c
                        </div>
                    </div>

                    <!-- Finding 3 -->
                    <div class="finding-box">
                        <div style="font-family: var(--font-body); font-size: 13px; font-weight: 500; color: var(--on-surface-variant, #bdc9c3); margin-bottom: 2px;">
                            Default VLAN active
                        </div>
                        <div style="font-size: 11px; color: rgba(189, 201, 195, 0.6); line-height: 1.3;">
                            CIS 2.1.2 Ensure default VLAN is disabled
                        </div>
                    </div>
                </div>

                <!-- Colonne Droite : Suggestions IA & Double Panneau Diff -->
                <div style="display: flex; flex-direction: column; gap: 10px;">
                    <div style="display: flex; align-items: center; gap: 6px; font-family: var(--font-body); font-size: 13px; font-weight: 600; color: var(--on-surface, #dfe4e0);">
                        <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="#78d8ba" stroke-width="2">
                            <path d="M12 2a7 7 0 0 0-7 7c0 2.38 1.19 4.47 3 5.74V17a2 2 0 0 0 2 2h4a2 2 0 0 0 2-2v-2.26c1.81-1.27 3-3.36 3-5.74a7 7 0 0 0-7-7z"/>
                            <line x1="9" y1="21" x2="15" y2="21"/>
                        </svg>
                        Suggestions d'automatisation IA
                    </div>

                    <!-- Double Panneau Diff Side-by-Side -->
                    <div class="diff-container">
                        <div class="diff-header">
                            <div style="flex: 1; padding: 6px 12px; color: var(--on-surface-variant); border-right: 1px solid rgba(255, 255, 255, 0.1);">
                                Current Config (Running)
                            </div>
                            <div style="flex: 1; padding: 6px 12px; color: var(--primary, #78d8ba); background: rgba(120, 216, 186, 0.05);">
                                AI Suggested Correction
                            </div>
                        </div>
                        <div class="diff-body">
                            <div class="diff-left">line vty 0 4
 login
 password cisco
!
snmp-server community public RO
snmp-server community private RW</div>
                            <div class="diff-right">line vty 0 4
 login local
 <span class="diff-highlight">! Removed: password cisco</span>
<span class="diff-highlight">transport input ssh</span>
!
<span class="diff-highlight">no snmp-server community public RO</span>
<span class="diff-highlight">no snmp-server community private RW</span>
<span class="diff-highlight">snmp-server group v3group v3 priv</span></div>
                        </div>
                    </div>
                </div>
            </div>

            <!-- Barre d'actions inférieure -->
            <div style="display: flex; justify-content: flex-end; gap: 12px; margin-top: 18px; padding-top: 14px; border-top: 1px solid rgba(255, 255, 255, 0.08);">
                <button class="btn-reject">
                    <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5">
                        <line x1="18" y1="6" x2="6" y2="18"/>
                        <line x1="6" y1="6" x2="18" y2="18"/>
                    </svg>
                    Reject
                </button>
                <button class="btn-approve">
                    <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5">
                        <path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"/>
                        <polyline points="22 4 12 14.01 9 11.01"/>
                    </svg>
                    Approve &amp; Apply
                </button>
            </div>
        </div>
        """
    )
