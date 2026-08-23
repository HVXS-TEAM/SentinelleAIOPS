"""
6_Reporting_&_Admin.py — Sentinelle AIOps
Pixel-perfect ref : Ecrans_Reference/Admin & Rapport/code.html + screen.png

Features:
  - Header actions: ⌘ SYNCHRONISER & + NOUVEAU RAPPORT buttons
  - Bento layout: Left column (Users Table & Audit Log), Right column (Reports Library & Notification Config)
  - Notranslate / translate="no" on all Material icons and system strings to prevent Chrome auto-translation bugs
  - st.container(key=...) for modular section wrapping
"""
import os, sys
import streamlit as st

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from page_template import page_bootstrap

# ── 1. BOOTSTRAP ──────────────────────────────────────────────────────────────
# ── Garde d'authentification ─────────────────────────────────────────────────
if not st.session_state.get("authenticated", False):
    st.switch_page("app.py")

page_bootstrap(
    active="Rapports",
    page_title="Administration & Rapports",
    search_placeholder="Rechercher rapports, utilisateurs, logs..."
)

# ── 2. CSS SPÉCIFIQUE AU MODULE ──────────────────────────────────────────────
st.markdown("""<style>
@keyframes pulse-urgent {
    0%, 100% { opacity: 1; transform: scale(1); }
    50% { opacity: 0.8; transform: scale(0.95); }
}
.animate-pulse-urgent { animation: pulse-urgent 1s infinite ease-in-out; }

/* En-tête des cartes */
.admin-card-hdr {
    padding: 14px 20px;
    border-bottom: 1px solid rgba(255,255,255,0.05);
    background: rgba(25, 28, 30, 0.8);
    display: flex;
    justify-content: space-between;
    align-items: center;
}
.admin-card-title {
    font-family: var(--font-mono);
    font-size: 11px;
    font-weight: 700;
    color: var(--primary);
    text-transform: uppercase;
    letter-spacing: 0.08em;
    display: flex;
    align-items: center;
    gap: 8px;
}

/* Cartes Bento */
.admin-bento-card {
    background: #191c1e;
    border: 1px solid rgba(255,255,255,0.05);
    border-radius: 8px;
    overflow: hidden;
    margin-bottom: 24px;
}

/* Tableau Utilisateurs */
.users-table {
    width: 100%;
    border-collapse: collapse;
    font-family: var(--font-body);
    font-size: 13px;
}
.users-table th {
    padding: 10px 16px;
    font-family: var(--font-mono);
    font-size: 10px;
    font-weight: 700;
    color: var(--on-surface-variant);
    text-transform: uppercase;
    letter-spacing: 0.08em;
    background: rgba(25, 28, 30, 0.5);
    border-bottom: 1px solid rgba(255,255,255,0.1);
}
.users-table td {
    padding: 12px 16px;
    border-bottom: 1px solid rgba(255,255,255,0.05);
    vertical-align: middle;
}
.users-table tr:hover { background: rgba(255,255,255,0.03); }

/* Tableau Audit Log */
.audit-table {
    width: 100%;
    border-collapse: collapse;
    font-family: var(--font-mono);
    font-size: 11px;
}
.audit-table th {
    padding: 8px 12px;
    font-weight: 500;
    color: rgba(189, 201, 195, 0.7);
    text-transform: uppercase;
    border-bottom: 1px solid rgba(255,255,255,0.1);
}
.audit-table td {
    padding: 8px 12px;
    border-bottom: 1px solid rgba(255,255,255,0.05);
    color: var(--on-surface-variant);
}
.audit-table tr:hover { background: rgba(255,255,255,0.03); }
.audit-table tr.crit-row { background: rgba(255, 180, 171, 0.05); }

/* Item Rapport */
.report-item {
    background: #1d2022;
    border: 1px solid rgba(255,255,255,0.1);
    border-radius: 6px;
    padding: 12px;
    display: flex;
    justify-content: space-between;
    align-items: center;
    transition: border-color 150ms ease;
}
.report-item:hover { border-color: rgba(129,208,248,0.5); }
.report-btn {
    width: 32px; height: 32px;
    border-radius: 50%;
    background: rgba(255,255,255,0.05);
    display: flex; align-items: center; justify-content: center;
    color: var(--on-surface-variant);
    cursor: pointer;
    transition: all 150ms ease;
}
.report-btn:hover { background: var(--secondary); color: var(--on-secondary); }

/* Toggle Switch CSS */
.switch-wrap {
    position: relative;
    display: inline-block;
    width: 36px;
    height: 20px;
}
.switch-wrap input { opacity: 0; width: 0; height: 0; }
.slider {
    position: absolute; cursor: pointer; top: 0; left: 0; right: 0; bottom: 0;
    background-color: #323538; transition: .3s; border-radius: 20px;
}
.slider:before {
    position: absolute; content: ""; height: 14px; width: 14px; left: 3px; bottom: 3px;
    background-color: white; transition: .3s; border-radius: 50%;
}
input:checked + .slider { background-color: #78d8ba; }
input:checked + .slider:before { transform: translateX(16px); }

/* Boutons Top Header */
.btn-sync {
    padding: 8px 16px; border-radius: 6px; border: 1px solid var(--secondary);
    color: var(--secondary); background: transparent; font-family: var(--font-mono);
    font-size: 11px; font-weight: 600; text-transform: uppercase; letter-spacing: 0.05em;
    display: inline-flex; align-items: center; gap: 8px; cursor: pointer;
}
.btn-new-rep {
    padding: 8px 16px; border-radius: 6px; border: none;
    background: var(--primary); color: var(--on-primary); font-family: var(--font-mono);
    font-size: 11px; font-weight: 700; text-transform: uppercase; letter-spacing: 0.05em;
    display: inline-flex; align-items: center; gap: 8px; cursor: pointer;
}
</style>""", unsafe_allow_html=True)

# ── 3. EN-TÊTE PRINCIPAL & ACTIONS ────────────────────────────────────────────
with st.container(key="admin-page-header"):
    col_title, col_btns = st.columns([2, 1])
    with col_title:
        st.markdown('<h2 style="font-size:28px;font-weight:700;margin:0;color:var(--on-surface);">Administration &amp; Rapports</h2>', unsafe_allow_html=True)
        st.markdown('<p style="font-size:14px;color:var(--on-surface-variant);margin:4px 0 20px 0;">Gestion de la plateforme et audits</p>', unsafe_allow_html=True)
    with col_btns:
        st.html("""
        <div style="display:flex;gap:12px;justify-content:flex-end;align-items:center;padding-top:4px;">
            <div class="btn-sync">
                <span class="material-symbols-outlined notranslate" translate="no" style="font-size:18px;">cloud_sync</span>
                <span>⌘ SYNCHRONISER</span>
            </div>
            <div class="btn-new-rep">
                <span class="material-symbols-outlined notranslate" translate="no" style="font-size:18px;">add</span>
                <span>+ NOUVEAU RAPPORT</span>
            </div>
        </div>
        """)

# ── 4. COLONNES BENTO GRID (GAUCHE / DROITE) ───────────────────────────────────
col_left, col_right = st.columns([2.1, 1])

# ── COLONNE GAUCHE ─────────────────────────────────────────────────────────────
with col_left:

    # ── MODULE 1: GESTION DES UTILISATEURS ────────────────────────────────────
    with st.container(key="users-management-container"):
        st.html("""
        <div class="admin-bento-card">
            <div class="admin-card-hdr">
                <div class="admin-card-title">
                    <span class="material-symbols-outlined notranslate" translate="no" style="font-size:18px;">group</span>
                    <span>Gestion des Utilisateurs</span>
                </div>
                <span class="material-symbols-outlined notranslate" translate="no" style="color:var(--on-surface-variant);cursor:pointer;font-size:20px;">filter_list</span>
            </div>
            <div style="overflow-x:auto;">
                <table class="users-table">
                    <thead>
                        <tr>
                            <th>UTILISATEUR</th>
                            <th>RÔLE</th>
                            <th>ÉTAT MFA</th>
                            <th>DERNIÈRE CONNEXION</th>
                            <th style="text-align:right;">ACTIONS</th>
                        </tr>
                    </thead>
                    <tbody>
                        <tr>
                            <td>
                                <div style="display:flex;align-items:center;gap:12px;">
                                    <div style="width:32px;height:32px;border-radius:4px;background:#3da186;display:flex;align-items:center;justify-content:center;color:#00382b;font-weight:700;font-size:12px;" class="notranslate" translate="no">SC</div>
                                    <div>
                                        <div style="font-weight:600;color:var(--on-surface);" class="notranslate" translate="no">Sarah Connor</div>
                                        <div style="font-size:11px;color:var(--on-surface-variant);" class="notranslate" translate="no">s.connor@sentinelle.io</div>
                                    </div>
                                </div>
                            </td>
                            <td>
                                <span class="snt-badge healthy notranslate" translate="no">ADMINISTRATEUR</span>
                            </td>
                            <td>
                                <span style="display:flex;align-items:center;gap:4px;color:var(--primary);font-size:13px;" class="notranslate" translate="no">
                                    <span class="material-symbols-outlined notranslate" translate="no" style="font-size:16px;font-variation-settings:'FILL' 1;">shield</span> Actif
                                </span>
                            </td>
                            <td style="font-family:var(--font-mono);font-size:12px;color:var(--on-surface-variant);" class="notranslate" translate="no">Aujourd'hui, 08:14</td>
                            <td style="text-align:right;">
                                <span class="material-symbols-outlined notranslate" translate="no" style="font-size:18px;color:var(--on-surface-variant);cursor:pointer;margin-right:8px;">edit</span>
                                <span class="material-symbols-outlined notranslate" translate="no" style="font-size:18px;color:var(--on-surface-variant);cursor:pointer;">delete</span>
                            </td>
                        </tr>
                        <tr>
                            <td>
                                <div style="display:flex;align-items:center;gap:12px;">
                                    <div style="width:32px;height:32px;border-radius:4px;background:#017094;display:flex;align-items:center;justify-content:center;color:#ceedff;font-weight:700;font-size:12px;" class="notranslate" translate="no">DB</div>
                                    <div>
                                        <div style="font-weight:600;color:var(--on-surface);" class="notranslate" translate="no">David Bowman</div>
                                        <div style="font-size:11px;color:var(--on-surface-variant);" class="notranslate" translate="no">d.bowman@sentinelle.io</div>
                                    </div>
                                </div>
                            </td>
                            <td>
                                <span class="snt-badge info notranslate" translate="no">TECHNICIEN</span>
                            </td>
                            <td>
                                <span style="display:flex;align-items:center;gap:4px;color:var(--primary);font-size:13px;" class="notranslate" translate="no">
                                    <span class="material-symbols-outlined notranslate" translate="no" style="font-size:16px;font-variation-settings:'FILL' 1;">shield</span> Actif
                                </span>
                            </td>
                            <td style="font-family:var(--font-mono);font-size:12px;color:var(--on-surface-variant);" class="notranslate" translate="no">Hier, 16:45</td>
                            <td style="text-align:right;">
                                <span class="material-symbols-outlined notranslate" translate="no" style="font-size:18px;color:var(--on-surface-variant);cursor:pointer;margin-right:8px;">edit</span>
                                <span class="material-symbols-outlined notranslate" translate="no" style="font-size:18px;color:var(--on-surface-variant);cursor:pointer;">delete</span>
                            </td>
                        </tr>
                        <tr>
                            <td>
                                <div style="display:flex;align-items:center;gap:12px;">
                                    <div style="width:32px;height:32px;border-radius:4px;background:#323538;display:flex;align-items:center;justify-content:center;color:#bdc9c3;font-weight:700;font-size:12px;" class="notranslate" translate="no">ER</div>
                                    <div>
                                        <div style="font-weight:600;color:var(--on-surface);" class="notranslate" translate="no">Ellen Ripley</div>
                                        <div style="font-size:11px;color:var(--on-surface-variant);" class="notranslate" translate="no">e.ripley@audit.ext</div>
                                    </div>
                                </div>
                            </td>
                            <td>
                                <span class="snt-badge" style="background:var(--surface-container-highest);color:var(--on-surface);" translate="no">VISITEUR</span>
                            </td>
                            <td>
                                <span style="display:flex;align-items:center;gap:4px;color:var(--error);font-size:13px;" class="notranslate" translate="no">
                                    <span class="material-symbols-outlined notranslate" translate="no" style="font-size:16px;">gpp_bad</span> Inactif
                                </span>
                            </td>
                            <td style="font-family:var(--font-mono);font-size:12px;color:var(--on-surface-variant);" class="notranslate" translate="no">02 Mars, 09:00</td>
                            <td style="text-align:right;">
                                <span class="material-symbols-outlined notranslate" translate="no" style="font-size:18px;color:var(--on-surface-variant);cursor:pointer;margin-right:8px;">edit</span>
                                <span class="material-symbols-outlined notranslate" translate="no" style="font-size:18px;color:var(--on-surface-variant);cursor:pointer;">delete</span>
                            </td>
                        </tr>
                    </tbody>
                </table>
            </div>
        </div>
        """)

    # ── MODULE 2: JOURNAL D'AUDIT ──────────────────────────────────────────────
    with st.container(key="audit-log-container"):
        st.html("""
        <div class="admin-bento-card">
            <div class="admin-card-hdr">
                <div class="admin-card-title">
                    <span class="material-symbols-outlined notranslate" translate="no" style="font-size:18px;">terminal</span>
                    <span>Journal d'Audit</span>
                </div>
                <button style="font-size:11px;color:var(--on-surface-variant);padding:4px 10px;background:#1d2022;border:1px solid rgba(255,255,255,0.1);border-radius:4px;cursor:pointer;">Export CSV</button>
            </div>
            <div style="overflow-x:auto;padding:8px;background:rgba(11,15,17,0.5);">
                <table class="audit-table">
                    <thead>
                        <tr>
                            <th>HORODATAGE</th>
                            <th>UTILISATEUR</th>
                            <th>ACTION</th>
                            <th>CIBLE</th>
                            <th>STATUT</th>
                        </tr>
                    </thead>
                    <tbody>
                        <tr>
                            <td style="color:var(--secondary);" class="notranslate" translate="no">2024-03-05T08:15:22Z</td>
                            <td class="notranslate" translate="no">s.connor</td>
                            <td style="color:var(--primary);" class="notranslate" translate="no">AUTH_SUCCESS</td>
                            <td class="notranslate" translate="no">auth.gateway.main</td>
                            <td class="notranslate" translate="no"><span style="width:6px;height:6px;border-radius:50%;background:var(--primary);display:inline-block;margin-right:4px;"></span> 200</td>
                        </tr>
                        <tr>
                            <td style="color:var(--secondary);" class="notranslate" translate="no">2024-03-05T08:18:41Z</td>
                            <td class="notranslate" translate="no">s.connor</td>
                            <td style="color:var(--tertiary);" class="notranslate" translate="no">CONF_UPDATE</td>
                            <td class="notranslate" translate="no">fw-core-eu-west</td>
                            <td class="notranslate" translate="no"><span style="width:6px;height:6px;border-radius:50%;background:var(--primary);display:inline-block;margin-right:4px;"></span> 200</td>
                        </tr>
                        <tr class="crit-row">
                            <td style="color:var(--secondary);" class="notranslate" translate="no">2024-03-05T09:02:11Z</td>
                            <td class="notranslate" translate="no">system.auto</td>
                            <td style="color:var(--error);font-weight:700;" class="notranslate" translate="no">ALERT_TRIGGER</td>
                            <td class="notranslate" translate="no">db-cluster-01.cpu</td>
                            <td style="color:var(--error);" class="animate-pulse-urgent notranslate" translate="no">
                                <span class="material-symbols-outlined notranslate" translate="no" style="font-size:14px;vertical-align:middle;">warning</span> CRIT
                            </td>
                        </tr>
                        <tr>
                            <td style="color:var(--secondary);" class="notranslate" translate="no">2024-03-05T09:05:00Z</td>
                            <td class="notranslate" translate="no">d.bowman</td>
                            <td style="color:var(--primary);" class="notranslate" translate="no">AUTH_SUCCESS</td>
                            <td class="notranslate" translate="no">auth.gateway.vpn</td>
                            <td class="notranslate" translate="no"><span style="width:6px;height:6px;border-radius:50%;background:var(--primary);display:inline-block;margin-right:4px;"></span> 200</td>
                        </tr>
                        <tr>
                            <td style="color:var(--secondary);" class="notranslate" translate="no">2024-03-05T09:12:33Z</td>
                            <td class="notranslate" translate="no">d.bowman</td>
                            <td style="color:var(--tertiary);" class="notranslate" translate="no">SERVICE_RESTART</td>
                            <td class="notranslate" translate="no">db-cluster-01.node-a</td>
                            <td class="notranslate" translate="no"><span style="width:6px;height:6px;border-radius:50%;background:var(--primary);display:inline-block;margin-right:4px;"></span> 200</td>
                        </tr>
                    </tbody>
                </table>
            </div>
        </div>
        """)

# ── COLONNE DROITE ─────────────────────────────────────────────────────────────
with col_right:

    # ── MODULE 3: BIBLIOTHÈQUE DE RAPPORTS ────────────────────────────────────
    with st.container(key="reports-library-container"):
        st.html("""
        <div class="admin-bento-card">
            <div class="admin-card-hdr">
                <div class="admin-card-title">
                    <span class="material-symbols-outlined notranslate" translate="no" style="font-size:18px;">library_books</span>
                    <span>Bibliothèque de Rapports</span>
                </div>
            </div>
            <div style="padding:16px;display:flex;flex-direction:column;gap:12px;">

                <div class="report-item">
                    <div>
                        <div style="font-size:14px;font-weight:500;color:var(--on-surface);">Audit Sécurité Hebdomadaire</div>
                        <div style="font-size:11px;color:var(--on-surface-variant);margin-top:4px;display:flex;align-items:center;gap:6px;" class="notranslate" translate="no">
                            <span class="material-symbols-outlined notranslate" translate="no" style="font-size:14px;">calendar_today</span>
                            04 Mars 2024 • S9 (Fév 26 - Mar 03)
                        </div>
                    </div>
                    <div class="report-btn" title="Télécharger">
                        <span class="material-symbols-outlined notranslate" translate="no" style="font-size:18px;">download</span>
                    </div>
                </div>

                <div class="report-item">
                    <div>
                        <div style="font-size:14px;font-weight:500;color:var(--on-surface);">Synthèse Perf. Mensuelle</div>
                        <div style="font-size:11px;color:var(--on-surface-variant);margin-top:4px;display:flex;align-items:center;gap:6px;" class="notranslate" translate="no">
                            <span class="material-symbols-outlined notranslate" translate="no" style="font-size:14px;">calendar_today</span>
                            01 Mars 2024 • Février 2024
                        </div>
                    </div>
                    <div class="report-btn" title="Télécharger">
                        <span class="material-symbols-outlined notranslate" translate="no" style="font-size:18px;">download</span>
                    </div>
                </div>

                <div class="report-item">
                    <div>
                        <div style="font-size:14px;font-weight:500;color:var(--on-surface);">Inventaire Parc Actif</div>
                        <div style="font-size:11px;color:var(--on-surface-variant);margin-top:4px;display:flex;align-items:center;gap:6px;" class="notranslate" translate="no">
                            <span class="material-symbols-outlined notranslate" translate="no" style="font-size:14px;">calendar_today</span>
                            01 Mars 2024 • T1 - Ad Hoc
                        </div>
                    </div>
                    <div class="report-btn" title="Télécharger">
                        <span class="material-symbols-outlined notranslate" translate="no" style="font-size:18px;">download</span>
                    </div>
                </div>

            </div>
        </div>
        """)

    # ── MODULE 4: CONFIGURATION NOTIFICATIONS ────────────────────────────────
    with st.container(key="notification-config-container"):
        st.html("""
        <div class="admin-bento-card">
            <div class="admin-card-hdr">
                <div class="admin-card-title">
                    <span class="material-symbols-outlined notranslate" translate="no" style="font-size:18px;">notifications_active</span>
                    <span>Configuration Notifications</span>
                </div>
            </div>
            <div style="padding:20px;display:flex;flex-direction:column;gap:20px;">

                <!-- CANAUX DE DIFFUSION -->
                <div>
                    <div style="font-family:var(--font-mono);font-size:10px;color:var(--on-surface-variant);text-transform:uppercase;letter-spacing:0.08em;padding-bottom:6px;border-bottom:1px solid rgba(255,255,255,0.1);margin-bottom:12px;">CANAUX DE DIFFUSION</div>

                    <div style="display:flex;flex-direction:column;gap:12px;">
                        <div style="display:flex;align-items:center;justify-content:space-between;">
                            <div style="display:flex;align-items:center;gap:10px;">
                                <span class="material-symbols-outlined notranslate" translate="no" style="color:var(--on-surface-variant);font-size:18px;">mail</span>
                                <span style="font-size:13px;color:var(--on-surface);">Email (SMTP Interne)</span>
                            </div>
                            <label class="switch-wrap">
                                <input type="checkbox" checked/>
                                <span class="slider"></span>
                            </label>
                        </div>

                        <div style="display:flex;align-items:center;justify-content:space-between;">
                            <div style="display:flex;align-items:center;gap:10px;">
                                <span class="material-symbols-outlined notranslate" translate="no" style="color:var(--on-surface-variant);font-size:18px;">send</span>
                                <span style="font-size:13px;color:var(--on-surface);">Telegram (Bot API)</span>
                            </div>
                            <label class="switch-wrap">
                                <input type="checkbox" checked/>
                                <span class="slider"></span>
                            </label>
                        </div>

                        <div style="display:flex;align-items:center;justify-content:space-between;">
                            <div style="display:flex;align-items:center;gap:10px;">
                                <span class="material-symbols-outlined notranslate" translate="no" style="color:var(--on-surface-variant);font-size:18px;">forum</span>
                                <span style="font-size:13px;color:var(--on-surface);">Discord (Webhook)</span>
                            </div>
                            <label class="switch-wrap">
                                <input type="checkbox"/>
                                <span class="slider"></span>
                            </label>
                        </div>
                    </div>
                </div>

                <!-- RÈGLES DE ROUTAGE -->
                <div>
                    <div style="font-family:var(--font-mono);font-size:10px;color:var(--on-surface-variant);text-transform:uppercase;letter-spacing:0.08em;padding-bottom:6px;border-bottom:1px solid rgba(255,255,255,0.1);margin-bottom:12px;">RÈGLES DE ROUTAGE</div>

                    <div style="display:flex;flex-direction:column;gap:8px;">
                        <div style="background:#1d2022;padding:10px 12px;border-radius:6px;border:1px solid rgba(255,255,255,0.05);display:flex;align-items:center;justify-content:space-between;">
                            <div style="display:flex;align-items:center;gap:8px;">
                                <span style="width:8px;height:8px;border-radius:50%;background:var(--error);" class="animate-pulse-urgent"></span>
                                <span style="font-family:var(--font-mono);font-size:12px;font-weight:600;" class="notranslate" translate="no">Critical</span>
                            </div>
                            <span style="font-size:11px;color:var(--on-surface-variant);background:#191c1e;padding:2px 8px;border-radius:4px;">Tous les canaux</span>
                        </div>

                        <div style="background:#1d2022;padding:10px 12px;border-radius:6px;border:1px solid rgba(255,255,255,0.05);display:flex;align-items:center;justify-content:space-between;">
                            <div style="display:flex;align-items:center;gap:8px;">
                                <span style="width:8px;height:8px;border-radius:50%;background:var(--secondary);"></span>
                                <span style="font-family:var(--font-mono);font-size:12px;font-weight:600;" class="notranslate" translate="no">Warning</span>
                            </div>
                            <span style="font-size:11px;color:var(--on-surface-variant);background:#191c1e;padding:2px 8px;border-radius:4px;">Email &amp; Telegram</span>
                        </div>

                        <div style="background:#1d2022;padding:10px 12px;border-radius:6px;border:1px solid rgba(255,255,255,0.05);display:flex;align-items:center;justify-content:space-between;">
                            <div style="display:flex;align-items:center;gap:8px;">
                                <span style="width:8px;height:8px;border-radius:50%;background:var(--outline-variant);"></span>
                                <span style="font-family:var(--font-mono);font-size:12px;font-weight:600;" class="notranslate" translate="no">Info</span>
                            </div>
                            <span style="font-size:11px;color:var(--on-surface-variant);background:#191c1e;padding:2px 8px;border-radius:4px;">Email Uniquement</span>
                        </div>
                    </div>
                </div>

            </div>
        </div>
        """)
