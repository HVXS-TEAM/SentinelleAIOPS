"""
4_NetDevOps.py — Sentinelle AIOps
Pixel-perfect ref : Ecrans_Reference/NetDevOps/code.html + screen.png

Features:
  - Header: NetDevOps Automation (h1 IBM Plex Sans) + Subtitle
  - 2-column layout [2, 3]:
    - Left: Network Equipment List (with CIS scores & active item DIST-SW-A) + Backup History timeline
    - Right: Audit Detail for DIST-SW-A (5 Critical Findings badge, findings list, AI automation suggestions with config diff, Reject/Approve buttons)
"""
import os, sys
import streamlit as st

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from page_template import page_bootstrap
from components import score_badge, finding_item, code_diff, card

# ── 1. BOOTSTRAP ──────────────────────────────────────────────────────────────
page_bootstrap(
    active="NetDevOps",
    page_title="NetDevOps Automation",
    search_placeholder="Rechercher IP, équipements, CIS benchmarks..."
)

# ── 2. CSS SPÉCIFIQUE AU MODULE ──────────────────────────────────────────────
st.markdown("""<style>
/* Equipment List Items */
.eq-item {
    background: var(--surface-container);
    border: 1px solid transparent;
    border-radius: 6px;
    padding: 12px 14px;
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 8px;
    transition: all 150ms ease;
}
.eq-item.active {
    border-color: rgba(120, 216, 186, 0.4);
    border-left: 4px solid var(--primary);
    background: rgba(61, 161, 134, 0.08);
}
.eq-name {
    font-family: var(--font-mono);
    font-size: 13px;
    font-weight: 700;
    color: var(--on-surface);
}
.eq-item.active .eq-name { color: var(--primary); }

/* Timeline Backup */
.timeline-item {
    position: relative;
    padding-left: 24px;
    padding-bottom: 12px;
    border-left: 1px solid rgba(62, 73, 69, 0.3);
    margin-left: 8px;
}
.timeline-item:last-child { border-left-color: transparent; }
.timeline-dot {
    position: absolute;
    left: -5px;
    top: 4px;
    width: 9px;
    height: 9px;
    border-radius: 50%;
    background: var(--primary);
}
.timeline-dot.old { background: var(--outline-variant); }

/* Custom Action Buttons */
.btn-reject {
    padding: 8px 18px;
    border-radius: 6px;
    border: 1px solid var(--outline-variant);
    background: transparent;
    color: var(--on-surface);
    font-family: var(--font-ui);
    font-size: 13px;
    font-weight: 600;
    cursor: pointer;
    display: inline-flex;
    align-items: center;
    gap: 6px;
}
.btn-approve {
    padding: 8px 18px;
    border-radius: 6px;
    border: none;
    background: #1F8A70;
    color: #ffffff;
    font-family: var(--font-ui);
    font-size: 13px;
    font-weight: 600;
    cursor: pointer;
    display: inline-flex;
    align-items: center;
    gap: 6px;
    box-shadow: 0 2px 10px rgba(31, 138, 112, 0.3);
}
</style>""", unsafe_allow_html=True)

# ── 3. EN-TÊTE DE PAGE ────────────────────────────────────────────────────────
with st.container(key="netdevops-header"):
    st.markdown('<h1 style="font-size:28px;font-weight:700;margin:0;color:var(--on-surface);font-family:\'IBM Plex Sans\', sans-serif;">NetDevOps Automation</h1>', unsafe_allow_html=True)
    st.markdown('<p style="font-size:14px;color:var(--on-surface-variant);margin:4px 0 20px 0;">Audit de conformité CIS &amp; Suggestions d\'automatisation IA</p>', unsafe_allow_html=True)

# ── 4. LAYOUT 2 COLONNES ──────────────────────────────────────────────────────
col_left, col_right = st.columns([2, 3])

# ── COLONNE GAUCHE ─────────────────────────────────────────────────────────────
with col_left:

    # 4a. Carte Équipements Réseau
    with card(key="equipment-card"):
        st.html("""
        <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:12px;">
            <div class="snt-card-title notranslate" translate="no" style="margin:0;">Équipements Réseau</div>
            <span class="notranslate" translate="no" style="font-family:var(--font-mono);font-size:11px;background:var(--surface-container-lowest);padding:2px 8px;border-radius:4px;border:1px solid rgba(62,73,69,0.3);color:var(--on-surface-variant);">35 total</span>
        </div>

        <!-- Item 1: CORE-RTR-01 -->
        <div class="eq-item">
            <div style="display:flex;align-items:center;gap:10px;">
                <span class="material-symbols-outlined notranslate" translate="no" style="color:var(--on-surface-variant);font-size:20px;">router</span>
                <div>
                    <div class="eq-name notranslate" translate="no">CORE-RTR-01</div>
                    <div style="display:flex;align-items:center;gap:6px;font-size:12px;color:var(--on-surface-variant);margin-top:2px;">
                        <span style="width:6px;height:6px;border-radius:50%;background:var(--error);display:inline-block;"></span>
                        <span>2 findings</span>
                    </div>
                </div>
            </div>
            """ + score_badge(82, "CIS SCORE", critical=True) + """
        </div>

        <!-- Item 2: DIST-SW-A (ACTIVE) -->
        <div class="eq-item active">
            <div style="display:flex;align-items:center;gap:10px;">
                <span class="material-symbols-outlined notranslate" translate="no" style="color:var(--primary);font-size:20px;">switch</span>
                <div>
                    <div class="eq-name notranslate" translate="no">DIST-SW-A</div>
                    <div style="display:flex;align-items:center;gap:6px;font-size:12px;color:var(--on-surface-variant);margin-top:2px;">
                        <span style="width:6px;height:6px;border-radius:50%;background:var(--error);display:inline-block;"></span>
                        <span>5 findings</span>
                    </div>
                </div>
            </div>
            """ + score_badge(65, "CIS SCORE", critical=True) + """
        </div>

        <!-- Item 3: FW-EXT-02 -->
        <div class="eq-item">
            <div style="display:flex;align-items:center;gap:10px;">
                <span class="material-symbols-outlined notranslate" translate="no" style="color:var(--on-surface-variant);font-size:20px;">security</span>
                <div>
                    <div class="eq-name notranslate" translate="no">FW-EXT-02</div>
                    <div style="display:flex;align-items:center;gap:6px;font-size:12px;color:var(--on-surface-variant);margin-top:2px;">
                        <span style="width:6px;height:6px;border-radius:50%;background:var(--primary);display:inline-block;"></span>
                        <span style="color:var(--primary);">Compliant</span>
                    </div>
                </div>
            </div>
            """ + score_badge(100, "CIS SCORE", critical=False) + """
        </div>
        """)

    # 4b. Carte Historique de Sauvegarde
    with card(key="backup-history-card"):
        st.html("""
        <div style="display:flex;align-items:center;gap:8px;margin-bottom:14px;">
            <span class="material-symbols-outlined notranslate" translate="no" style="color:var(--on-surface-variant);font-size:18px;">history</span>
            <div class="snt-card-title notranslate" translate="no" style="margin:0;">Historique de sauvegarde</div>
        </div>

        <div style="padding-top:4px;">
            <!-- Timeline Item 1 -->
            <div class="timeline-item">
                <div class="timeline-dot"></div>
                <div style="display:flex;justify-content:space-between;align-items:flex-start;">
                    <div>
                        <div style="font-size:12px;color:var(--on-surface);font-weight:500;">Aujourd'hui 02:00</div>
                        <div style="font-family:var(--font-mono);font-size:10px;color:var(--on-surface-variant);margin-top:2px;" class="notranslate" translate="no">Hash: 8f9a2b...</div>
                    </div>
                    <div style="color:var(--primary);font-size:12px;font-weight:600;cursor:pointer;display:flex;align-items:center;gap:4px;">
                        <span class="material-symbols-outlined notranslate" translate="no" style="font-size:14px;">settings_backup_restore</span>
                        <span>Restore</span>
                    </div>
                </div>
            </div>

            <!-- Timeline Item 2 -->
            <div class="timeline-item">
                <div class="timeline-dot old"></div>
                <div style="display:flex;justify-content:space-between;align-items:flex-start;">
                    <div>
                        <div style="font-size:12px;color:var(--on-surface-variant);">Hier 02:00</div>
                        <div style="font-family:var(--font-mono);font-size:10px;color:rgba(189,201,195,0.5);margin-top:2px;" class="notranslate" translate="no">Hash: 3c1d4e...</div>
                    </div>
                    <div style="color:var(--on-surface-variant);font-size:12px;cursor:pointer;display:flex;align-items:center;gap:4px;">
                        <span class="material-symbols-outlined notranslate" translate="no" style="font-size:14px;">settings_backup_restore</span>
                        <span>Restore</span>
                    </div>
                </div>
            </div>
        </div>
        """)

# ── COLONNE DROITE ─────────────────────────────────────────────────────────────
with col_right:

    with card(key="audit-detail-card"):
        # Header de la carte
        st.html("""
        <div style="display:flex;justify-content:space-between;align-items:flex-start;padding-bottom:12px;border-bottom:1px solid rgba(62,73,69,0.2);margin-bottom:16px;">
            <div>
                <h3 style="font-size:18px;font-weight:700;color:var(--primary);margin:0;display:flex;align-items:center;gap:6px;" class="notranslate" translate="no">
                    DIST-SW-A <span style="color:var(--on-surface-variant);font-weight:400;font-size:15px;">| Détail de l'audit</span>
                </h3>
                <p style="font-size:12px;color:var(--on-surface-variant);margin:4px 0 0 0;">CIS Cisco IOS 15 Benchmark v4.0.0</p>
            </div>
            <div>
                <span class="notranslate" translate="no" style="background:rgba(255,180,171,0.15);color:var(--error);border:1px solid rgba(255,180,171,0.3);padding:4px 10px;border-radius:4px;font-size:12px;font-weight:600;display:flex;align-items:center;gap:6px;">
                    <span class="material-symbols-outlined notranslate" translate="no" style="font-size:16px;">warning</span>
                    5 Critical Findings
                </span>
            </div>
        </div>
        """)

        # Sous-colonnes pour Findings et Suggestions IA
        c_findings, c_diff = st.columns([1, 1.4])

        with c_findings:
            st.html("""
            <div style="padding-right:8px;">
                <div style="font-family:var(--font-mono);font-size:10px;font-weight:700;color:var(--on-surface-variant);text-transform:uppercase;letter-spacing:0.08em;margin-bottom:10px;">Audit Findings</div>
                """ + finding_item(
                    "Plaintext password detected",
                    "CIS 1.1.1 Ensure 'service password-encryption' is enabled",
                    level="critical", active=True
                ) + finding_item(
                    "SNMP v1 active",
                    "CIS 4.2.1 Disable SNMPv1/v2c",
                    level="warning", active=False
                ) + finding_item(
                    "Default VLAN active",
                    "CIS 2.1.2 Ensure default VLAN is disabled",
                    level="neutral", active=False
                ) + """
            </div>
            """)

        with c_diff:
            st.html("""
            <div style="font-size:13px;font-weight:600;color:var(--on-surface);display:flex;align-items:center;gap:6px;margin-bottom:10px;">
                <span class="material-symbols-outlined notranslate" translate="no" style="color:var(--primary);font-size:18px;">psychology</span>
                <span>Suggestions d'automatisation IA</span>
            </div>
            """)

            tab_curr, tab_sugg = st.tabs(["Current Config (Running)", "AI Suggested Correction"])

            orig_lines = [
                "line vty 0 4",
                " login",
                " password cisco",
                "!",
                "snmp-server community public RO",
                "snmp-server community private RW"
            ]

            sugg_lines = [
                "line vty 0 4",
                " login local",
                "! Removed: password cisco",
                "transport input ssh",
                "!",
                "no snmp-server community public RO",
                "no snmp-server community private RW",
                "snmp-server group v3group v3 priv"
            ]

            with tab_curr:
                st.code("\n".join(orig_lines), language="cisco")

            with tab_sugg:
                st.code("\n".join(sugg_lines), language="cisco")

        # Boutons d'action en bas
        st.html("""
        <div style="display:flex;justify-content:flex-end;gap:12px;margin-top:20px;padding-top:12px;border-top:1px solid rgba(62,73,69,0.2);">
            <div class="btn-reject">
                <span class="material-symbols-outlined notranslate" translate="no" style="font-size:16px;">close</span>
                <span>Reject</span>
            </div>
            <div class="btn-approve">
                <span class="material-symbols-outlined notranslate" translate="no" style="font-size:16px;">check_circle</span>
                <span>Approve &amp; Apply</span>
            </div>
        </div>
        """)
