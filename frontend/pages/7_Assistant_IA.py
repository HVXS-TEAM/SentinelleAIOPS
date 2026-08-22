"""
7_Assistant_IA.py — Sentinelle AIOps
Pixel-perfect ref : Ecrans_Reference/Assistant_IA/code.html + screen.png

CORRECTIF v4 :
  - Protection totale anti-traduction Chrome (notranslate / translate="no") sur toutes les icônes Material Symbols (warning, dns, cleaning_services, analytics, policy, summarize, visibility, attach_file, send, smart_toy).
  - Évite les dédoublements/superpositions de texte causés par la traduction des ligatures d'icônes par le navigateur.
  - Tout est rendu de manière autonome et propre via st.html() et st.container().
"""
import os, sys
import streamlit as st

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from page_template import page_bootstrap

# ── 1. BOOTSTRAP ──────────────────────────────────────────────────────────────
page_bootstrap(
    active="Assistant IA",
    page_title="Assistant IA",
    search_placeholder="Rechercher entités, requêtes..."
)

# ── 2. CSS SPÉCIFIQUE AU MODULE ──────────────────────────────────────────────
st.markdown("""<style>
@keyframes pulse-op { from{opacity:1} to{opacity:0.6} }
.pulse-critical { animation: pulse-op 0.5s infinite alternate; }

.ai-table-wrap { background:var(--surface-container-low); border:1px solid rgba(62,73,69,0.2); border-radius:8px; overflow:hidden; margin-top:16px; }
.ai-table-hdr { display:grid; grid-template-columns:5fr 4fr 3fr; gap:8px; background:var(--surface-container); padding:8px 16px; border-bottom:1px solid rgba(62,73,69,0.1); }
.ai-table-hdr span { font-family:var(--font-mono); font-size:10px; font-weight:700; color:var(--on-surface-variant); text-transform:uppercase; letter-spacing:0.08em; }
.ai-table-hdr .r { text-align:right; }
.ai-table-row { display:grid; grid-template-columns:5fr 4fr 3fr; gap:8px; padding:12px 16px; border-bottom:1px solid rgba(62,73,69,0.05); align-items:center; }
.ai-table-row:last-child { border-bottom:none; }
.ai-table-row.z { background:rgba(25,28,30,0.3); }
.srv { display:flex; align-items:center; gap:8px; font-family:var(--font-mono); font-size:13px; font-weight:600; }
.srv.crit { color:var(--error); }
.srv.prim { color:var(--primary); }
.dt { font-family:var(--font-body); font-size:13px; color:var(--on-surface); }
.pct { font-family:var(--font-mono); font-size:13px; font-weight:700; text-align:right; }
.pct.crit { color:var(--error); }
.pct.prim { color:var(--primary); }

.btn-cleanup { display:inline-flex; align-items:center; gap:8px; background:rgba(31,138,112,0.1); border:1px solid rgba(31,138,112,0.3); color:#1F8A70; font-family:var(--font-mono); font-size:11px; font-weight:700; letter-spacing:0.08em; text-transform:uppercase; padding:8px 16px; border-radius:4px; margin-top:16px; cursor:pointer; }
.snt-chip-ai { display:inline-flex; align-items:center; gap:6px; background:var(--surface-container); border:1px solid rgba(62,73,69,0.4); border-radius:9999px; padding:6px 16px; font-family:var(--font-body); font-size:13px; color:var(--on-surface-variant); white-space:nowrap; }
.ai-chips-row { display:flex; flex-wrap:wrap; gap:8px; margin-bottom:10px; max-width:840px; }

.ai-input-wrap { position:relative; background:var(--surface-container-low); border:1px solid rgba(62,73,69,0.5); border-radius:12px; padding:16px 16px 52px 16px; max-width:840px; min-height:80px; }
.ai-placeholder { font-family:var(--font-body); font-size:16px; color:rgba(189,201,195,0.4); }
.ai-badge { position:absolute; bottom:10px; left:14px; display:inline-flex; align-items:center; gap:5px; background:var(--surface-container-highest); border:1px solid rgba(62,73,69,0.3); border-radius:4px; padding:3px 8px; font-family:var(--font-mono); font-size:10px; color:var(--on-surface-variant); text-transform:uppercase; letter-spacing:0.1em; }
.ai-actions { position:absolute; bottom:8px; right:8px; display:flex; align-items:center; gap:6px; }
.btn-attach { width:38px; height:38px; border-radius:8px; background:transparent; display:flex; align-items:center; justify-content:center; color:var(--on-surface-variant); }
.btn-send { width:38px; height:38px; border-radius:8px; background:#1F8A70; display:flex; align-items:center; justify-content:center; color:#fff; box-shadow:0 2px 8px rgba(31,138,112,0.3); }

.ai-footer { text-align:center; font-family:var(--font-mono); font-size:11px; color:rgba(189,201,195,0.5); margin-top:6px; max-width:840px; }
.user-bubble-wrap { display:flex; justify-content:flex-end; max-width:840px; }
.user-bubble { background:var(--surface-container-highest); border:1px solid rgba(62,73,69,0.2); border-radius:18px 18px 4px 18px; padding:16px 20px; max-width:85%; box-shadow:0 1px 4px rgba(0,0,0,0.2); }
.user-bubble p { font-family:var(--font-body); font-size:16px; color:var(--on-surface); margin:0; line-height:1.5; }

.bot-row { display:flex; gap:16px; align-items:flex-start; max-width:840px; width:100%; margin-top:8px; }
.bot-icon { width:40px; height:40px; border-radius:8px; background:var(--surface-container); border:1px solid rgba(120,216,186,0.2); display:flex; align-items:center; justify-content:center; flex-shrink:0; margin-top:4px; box-shadow:0 0 15px rgba(120,216,186,0.1); }
.bot-card { flex:1; background:var(--surface-container); border:1px solid rgba(62,73,69,0.3); border-radius:4px 18px 18px 18px; padding:20px 24px; box-shadow:0 1px 4px rgba(0,0,0,0.2); }
.bot-intro { font-family:var(--font-body); font-size:16px; color:var(--on-surface); margin:0; line-height:1.6; }
</style>""", unsafe_allow_html=True)

# ── 3. MESSAGE UTILISATEUR ────────────────────────────────────────────────────
with st.container(key="user-msg-container"):
    st.html("""
    <div class="user-bubble-wrap">
        <div class="user-bubble">
            <p>Quels serveurs risquent une saturation disque cette semaine ?</p>
        </div>
    </div>
    """)

# ── 4. RÉPONSE IA ─────────────────────────────────────────────────────────────
with st.container(key="ai-bot-container"):
    st.html("""
    <div class="bot-row">
        <div class="bot-icon">
            <span class="material-symbols-outlined notranslate" translate="no" style="color:var(--primary);font-size:22px;font-variation-settings:'FILL' 1;">smart_toy</span>
        </div>
        <div class="bot-card">
            <p class="bot-intro">D'après l'analyse prédictive des tendances de consommation, 3 serveurs présentent un risque élevé de saturation disque (&gt;90%) d'ici la fin de la semaine&nbsp;:</p>
            <div class="ai-table-wrap">
                <div class="ai-table-hdr">
                    <span>Serveur</span>
                    <span>Date Prévue</span>
                    <span class="r">Usage Actuel</span>
                </div>
                <div class="ai-table-row">
                    <div class="srv crit">
                        <span class="material-symbols-outlined pulse-critical notranslate" translate="no" style="font-size:16px;">warning</span>
                        <span class="notranslate" translate="no">APP-SRV-01</span>
                    </div>
                    <div class="dt">Jeu. 14 Nov, 02:00</div>
                    <div class="pct crit notranslate" translate="no">88.4%</div>
                </div>
                <div class="ai-table-row z">
                    <div class="srv prim">
                        <span class="material-symbols-outlined notranslate" translate="no" style="font-size:16px;color:var(--primary);">dns</span>
                        <span class="notranslate" translate="no">DB-CLUSTER-M1</span>
                    </div>
                    <div class="dt">Ven. 15 Nov, 18:30</div>
                    <div class="pct prim notranslate" translate="no">86.1%</div>
                </div>
                <div class="ai-table-row">
                    <div class="srv prim">
                        <span class="material-symbols-outlined notranslate" translate="no" style="font-size:16px;color:var(--primary);">dns</span>
                        <span class="notranslate" translate="no">STO-NODE-04</span>
                    </div>
                    <div class="dt">Sam. 16 Nov, 09:15</div>
                    <div class="pct prim notranslate" translate="no">85.0%</div>
                </div>
            </div>
            <div class="btn-cleanup">
                <span class="material-symbols-outlined notranslate" translate="no" style="font-size:16px;">cleaning_services</span>
                <span>PROPOSER NETTOYAGE</span>
            </div>
        </div>
    </div>
    """)

# ── 5. SEPARATEUR ─────────────────────────────────────────────────────────────
st.markdown('<hr class="snt-divider" style="max-width:840px;"/>', unsafe_allow_html=True)

# ── 6. CHIPS + ZONE DE SAISIE ─────────────────────────────────────────────────
with st.container(key="ai-input-container"):
    st.html("""
    <div class="ai-chips-row">
        <div class="snt-chip-ai">
            <span class="material-symbols-outlined notranslate" translate="no" style="font-size:14px;">analytics</span>
            <span>Analyser le trafic réseau</span>
        </div>
        <div class="snt-chip-ai">
            <span class="material-symbols-outlined notranslate" translate="no" style="font-size:14px;">policy</span>
            <span>Vérifier la conformité</span>
        </div>
        <div class="snt-chip-ai">
            <span class="material-symbols-outlined notranslate" translate="no" style="font-size:14px;">summarize</span>
            <span>Résumé des alertes critiques</span>
        </div>
    </div>

    <div class="ai-input-wrap">
        <div class="ai-placeholder">Demander à Sentinelle IA...</div>
        <div class="ai-badge">
            <span class="material-symbols-outlined notranslate" translate="no" style="font-size:12px;">visibility</span>
            <span>LECTURE SEULE</span>
        </div>
        <div class="ai-actions">
            <div class="btn-attach" title="Joindre un fichier">
                <span class="material-symbols-outlined notranslate" translate="no" style="font-size:20px;">attach_file</span>
            </div>
            <div class="btn-send" title="Envoyer">
                <span class="material-symbols-outlined notranslate" translate="no" style="font-size:20px;font-variation-settings:'FILL' 1;">send</span>
            </div>
        </div>
    </div>

    <div class="ai-footer">
        L'IA peut faire des erreurs. Vérifiez les informations critiques dans les dashboards principaux.
    </div>
    """)
