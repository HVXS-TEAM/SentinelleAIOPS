"""
components.py — Composants UI réutilisables pour Sentinelle AIOps.

Source de vérité visuelle : DESIGN.md + screen.png de chaque écran Stitch.

RÈGLE IMPORTANTE (bug corrigé le 10/08) : en Streamlit, on NE PEUT PAS
ouvrir une balise <div> dans un st.markdown() puis la refermer dans un
AUTRE st.markdown() séparé pour "envelopper" du contenu entre les deux —
chaque appel st.* produit un bloc indépendant dans le DOM, ils ne
s'imbriquent pas. Pour un vrai conteneur stylable qui enveloppe du
contenu, utiliser st.container(key="...") : Streamlit génère alors une
vraie classe CSS .st-key-<key> sur le conteneur réel. C'est la seule
technique utilisée ici pour les cartes et la nav — ne pas réintroduire
le pattern div-ouvrante/div-fermante sur deux appels séparés.
"""

from pathlib import Path
from itertools import count
import streamlit as st

THEME_CSS_PATH = Path(__file__).parent / "theme.css"
LOGIN_CSS_PATH = Path(__file__).parent / "login.css"
_card_counter = count()

# SVG inline, style "outline" proche des maquettes Stitch (grille pour
# Dashboard, courbe pour Supervision, bouclier pour Sécurité, etc.).
# Utilise currentColor pour hériter la couleur CSS (gris inactif / teal
# actif) — voir .nav-icon dans theme.css. AUCUNE dépendance de police :
# contrairement à :material/...:, ça ne peut pas échouer selon le réseau
# ou la version de Streamlit (bug connu et documenté de Streamlit).
ICONS = {
    "dashboard": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="3" y="3" width="7" height="9" rx="1"/><rect x="14" y="3" width="7" height="5" rx="1"/><rect x="14" y="12" width="7" height="9" rx="1"/><rect x="3" y="16" width="7" height="5" rx="1"/></svg>',
    "supervision": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polyline points="3,17 9,11 13,15 21,6"/><polyline points="14,6 21,6 21,13"/></svg>',
    "securite": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M12 3l7 3v6c0 4.5-3 7.5-7 9-4-1.5-7-4.5-7-9V6l7-3z"/></svg>',
    "netdevops": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"><circle cx="12" cy="5" r="2.2"/><circle cx="5" cy="19" r="2.2"/><circle cx="19" cy="19" r="2.2"/><line x1="12" y1="7.2" x2="5" y2="16.8"/><line x1="12" y1="7.2" x2="19" y2="16.8"/></svg>',
    "parc": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="3" y="4" width="18" height="4" rx="1"/><path d="M5 8v11a1 1 0 0 0 1 1h12a1 1 0 0 0 1-1V8"/><line x1="10" y1="12" x2="14" y2="12"/></svg>',
    "rapports": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"><line x1="5" y1="20" x2="5" y2="10"/><line x1="12" y1="20" x2="12" y2="4"/><line x1="19" y1="20" x2="19" y2="14"/></svg>',
    "assistant": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="4" y="8" width="16" height="12" rx="2"/><line x1="12" y1="8" x2="12" y2="4"/><circle cx="12" cy="3" r="1" fill="currentColor"/><circle cx="9" cy="14" r="1.2" fill="currentColor"/><circle cx="15" cy="14" r="1.2" fill="currentColor"/></svg>',
    "administration": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="3"/><path d="M19.4 15a1.65 1.65 0 0 0 .33 1.82l.06.06a2 2 0 1 1-2.83 2.83l-.06-.06a1.65 1.65 0 0 0-1.82-.33 1.65 1.65 0 0 0-1 1.51V21a2 2 0 0 1-4 0v-.09A1.65 1.65 0 0 0 9 19.4a1.65 1.65 0 0 0-1.82.33l-.06.06a2 2 0 1 1-2.83-2.83l.06-.06a1.65 1.65 0 0 0 .33-1.82 1.65 1.65 0 0 0-1.51-1H3a2 2 0 0 1 0-4h.09A1.65 1.65 0 0 0 4.6 9a1.65 1.65 0 0 0-.33-1.82l-.06-.06a2 2 0 1 1 2.83-2.83l.06.06a1.65 1.65 0 0 0 1.82.33H9a1.65 1.65 0 0 0 1-1.51V3a2 2 0 0 1 4 0v.09a1.65 1.65 0 0 0 1 1.51 1.65 1.65 0 0 0 1.82-.33l.06-.06a2 2 0 1 1 2.83 2.83l-.06.06a1.65 1.65 0 0 0-.33 1.82V9a1.65 1.65 0 0 0 1.51 1H21a2 2 0 0 1 0 4h-.09a1.65 1.65 0 0 0-1.51 1z"/></svg>',
}

# (label affiché, chemin réel du fichier sous pages/, clé de ICONS ci-dessus)
# ⚠️ ANTIGRAVITY : remplace le champ "page" de chaque tuple par le VRAI
# chemin du fichier correspondant dans le dossier pages/ de ce projet
# (respecte la casse exacte).
NAV_ITEMS = [
    ("Dashboard", "pages/1_Dashboard.py", "dashboard"),
    ("Supervision", "pages/3_Supervision.py", "supervision"),
    ("Sécurité", "pages/2_Sécurité.py", "securite"),
    ("NetDevOps", "pages/4_NetDevOps.py", "netdevops"),
    ("Parc Informatique", "pages/5_Parc_Informatique.py", "parc"),
    ("Rapports & Admin", "pages/6_Reporting_&_Admin.py", "rapports"),
    ("Assistant IA", "pages/7_Assistant_IA.py", "assistant"),
]


import datetime


def _auto_theme() -> str:
    """Retourne 'light' ou 'dark' selon l'heure actuelle du serveur.
    Clair de 6h à 18h, sombre le reste du temps — 100% automatique, sans
    bouton ni préférence manuelle (remplace l'ancien toggle 🌙/☀️)."""
    hour = datetime.datetime.now().hour
    return "light" if 6 <= hour < 18 else "dark"


def load_theme() -> None:
    """Injecte theme.css une seule fois par page, puis applique
    automatiquement la palette claire si l'heure actuelle correspond à
    la tranche "jour" (voir _auto_theme()). À appeler juste après
    st.set_page_config()."""
    css = THEME_CSS_PATH.read_text(encoding="utf-8")
    st.markdown(f"<style>{css}</style>", unsafe_allow_html=True)
    if _auto_theme() == "light":
        st.markdown(f"<style>{LIGHT_MODE_OVERRIDES}</style>", unsafe_allow_html=True)


_LOGIN_LIGHT_OVERRIDES = """
:root {
    --login-bg: #eef1f0;
    --login-dot: #dde3e0;
    --login-glass-bg: rgba(255, 255, 255, 0.75);
    --login-glass-border: rgba(0, 0, 0, 0.08);
    --login-surface-container-highest: #e2e7e5;
    --login-outline-variant: #c5cec9;
    --login-on-surface: #171d1b;
    --login-on-surface-variant: #435048;
    --login-primary-container: #00c9a3;
    --login-primary-fixed: #00e0b4;
    --login-on-primary-fixed: #00281f;
}
"""


def load_login_theme() -> None:
    """Équivalent de load_theme() pour l'écran de connexion (palette
    séparée, login.css) : injecte login.css puis, automatiquement selon
    l'heure (même logique que load_theme() — _auto_theme()), applique la
    variante claire dédiée. À appeler dans le fichier de connexion à la
    place d'une lecture manuelle de login.css."""
    css = LOGIN_CSS_PATH.read_text(encoding="utf-8")
    st.markdown(f"<style>{css}</style>", unsafe_allow_html=True)
    if _auto_theme() == "light":
        st.markdown(f"<style>{_LOGIN_LIGHT_OVERRIDES}</style>", unsafe_allow_html=True)


LIGHT_MODE_OVERRIDES = """
:root {
    --surface: #f5f7f6;
    --surface-dim: #d5d9d8;
    --surface-bright: #f5f7f6;
    --surface-container-lowest: #ffffff;
    --surface-container-low: #eff3f1;
    --surface-container: #e9edeb;
    --surface-container-high: #e3e7e5;
    --surface-container-highest: #dde1df;
    --on-surface: #171d1b;
    --on-surface-variant: #3f4946;
    --inverse-surface: #2b3230;
    --inverse-on-surface: #ecf2ee;
    --outline: #6f7976;
    --outline-variant: #bfc9c5;
    --surface-tint: #006b55;
    --surface-variant: #dde5e0;
    --background: #f5f7f6;
    --on-background: #171d1b;
    --border-subtle: rgba(0, 0, 0, 0.08);

    --primary: #006b55;
    --on-primary: #ffffff;
    --primary-container: #94f5d6;
    --on-primary-container: #002018;
    --inverse-primary: #78d8ba;

    --secondary: #01677f;
    --on-secondary: #ffffff;
    --secondary-container: #b6eaff;
    --on-secondary-container: #001f28;

    --tertiary: #3f5b8f;
    --on-tertiary: #ffffff;
    --tertiary-container: #d8e2ff;
    --on-tertiary-container: #001a41;

    --error: #ba1a1a;
    --on-error: #ffffff;
    --error-container: #ffdad6;
    --on-error-container: #410002;

    --node-critical: #b03f2e;
    --node-warning: #a15c1f;

    --predictive-accent: #c65d47;
    --on-predictive-accent: #ffffff;

    --status-critical-bg-strong: rgba(186, 26, 26, 0.12);
    --status-critical-bg-medium: rgba(186, 26, 26, 0.10);
    --status-critical-bg-soft: rgba(186, 26, 26, 0.08);
    --status-critical-bg-softer: rgba(186, 26, 26, 0.05);
    --status-critical-border: rgba(186, 26, 26, 0.25);
    --status-critical-shadow: rgba(186, 26, 26, 0.3);
    --status-critical-shadow-soft: rgba(186, 26, 26, 0.08);

    --status-healthy-bg-soft: rgba(0, 107, 85, 0.12);
    --status-healthy-bg-softer: rgba(0, 107, 85, 0.08);

    --status-warning-text: #b45309;
    --status-warning-bg-soft: rgba(180, 83, 9, 0.12);
    --status-warning-border: rgba(180, 83, 9, 0.3);

    --status-info-bg-soft: rgba(1, 103, 127, 0.10);
    --status-info-border: rgba(1, 103, 127, 0.3);

    --node-critical-bg-soft: rgba(180, 60, 45, 0.12);
    --node-critical-border: rgba(180, 60, 45, 0.3);
    --node-warning-bg-soft: rgba(180, 120, 40, 0.12);
    --node-warning-border: rgba(180, 120, 40, 0.3);
}
"""


def sidebar_nav(active: str) -> None:
    """Navigation NATIVE Streamlit (st.page_link) enveloppée dans de vrais
    st.container(key=...), avec icône SVG inline à gauche du label (pas
    d'icône native page_link — on affiche notre propre SVG via st.markdown
    dans une sous-colonne étroite, à côté du st.page_link qui ne porte que
    le label). `active` doit correspondre à un label de NAV_ITEMS.

    La sidebar se réduit automatiquement en mode "icônes seules" (72px)
    quand la souris n'est pas dessus, et s'élargit (240px) au survol —
    comportement 100% CSS (voir theme.css), aucun JS. Le bouton 📌 permet
    de l'épingler en position ouverte en permanence (utile en navigation
    au clavier/tactile, où il n'y a pas de survol)."""
    with st.sidebar:
        if "sidebar_pinned" not in st.session_state:
            st.session_state.sidebar_pinned = False

        with st.container(key="sentinelle-logo"):
            col_logo, col_pin = st.columns([5, 1])
            with col_logo:
                st.markdown(
                    """
                    <div style="display:flex;align-items:center;gap:8px;">
                        <img src="app/static/logo.png" alt="Sentinelle"
                             class="sentinelle-logo-mark"
                             style="width:28px;height:28px;object-fit:contain;flex-shrink:0;">
                        <div class="sentinelle-logo-text">
                            <div style="font-family:var(--font-display);font-weight:700;
                                        font-size:18px;letter-spacing:0.02em;color:var(--on-surface);
                                        white-space:nowrap;">
                                SENTINELLE
                            </div>
                            <div style="font-family:var(--font-mono);font-size:11px;
                                        color:var(--on-surface-variant);letter-spacing:0.05em;
                                        white-space:nowrap;">
                                AIOPS COMMAND
                            </div>
                        </div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )
            with col_pin:
                if st.button("\u00a0", key="sidebar_pin_btn", help="Épingler la sidebar ouverte"):
                    st.session_state.sidebar_pinned = not st.session_state.sidebar_pinned
                    st.rerun()

        if st.session_state.sidebar_pinned:
            st.markdown('<div class="sidebar-pinned-marker"></div>', unsafe_allow_html=True)

        for i, (label, page_path, icon_key) in enumerate(NAV_ITEMS):
            is_active = label == active
            key = f"navitem-{i}-active" if is_active else f"navitem-{i}"

            with st.container(key=key):
                col_icon, col_label = st.columns([1, 5], vertical_alignment="center")
                with col_icon:
                    st.markdown(
                        f'<div class="nav-icon">{ICONS.get(icon_key, "")}</div>',
                        unsafe_allow_html=True,
                    )
                with col_label:
                    st.page_link(page_path, label=label)


def top_header(
    search_placeholder: str = "Rechercher...",
    page_title: str | None = None,
    notifications: list[str] | None = None,
    on_notification_click=None,
) -> None:
    """Barre supérieure : recherche + notifications (popover réel, items
    RÉELLEMENT cliquables — cf. correction du 03/09, les items étaient
    avant du texte statique en liste à puces).
    Le thème clair/sombre est désormais 100% automatique selon l'heure
    (voir _auto_theme()/load_theme()) — plus de bouton manuel ici.
    Enveloppée dans un vrai st.container(key=...) pour que le style
    sticky/flex de theme.css s'applique réellement au bon élément.
    page_title (optionnel) : affiche un titre centré dans le bandeau
    (ex. "Sentinelle AIOps") — à ne passer QUE sur les écrans dont le
    screen.png de référence montre effectivement ce titre centré dans le
    header.
    on_notification_click (optionnel) : fonction callback appelée avec
    le texte de la notification cliquée, ex.
    on_notification_click=lambda text: st.switch_page("pages/3_Supervision.py")
    Si non fourni, le clic affiche un st.toast() de confirmation en
    attendant qu'une vraie action soit branchée."""
    with st.container(key="sentinelle-header"):
        if page_title:
            col_search, col_title, col_icons = st.columns([2, 2, 1])
        else:
            col_search, col_icons = st.columns([4, 1])
        with col_search:
            st.text_input(
                "Recherche",
                placeholder=f"🔍  {search_placeholder}",
                label_visibility="collapsed",
                key="sentinelle_header_search",
            )
        if page_title:
            with col_title:
                st.markdown(
                    f'<div style="text-align:center;font-weight:700;font-size:16px;'
                    f'color:var(--on-surface);">{page_title}</div>',
                    unsafe_allow_html=True,
                )
        with col_icons:
            with st.popover("🔔", width="content"):
                st.markdown("**Notifications**")
                items = notifications or ["Aucune nouvelle notification."]
                for i, item in enumerate(items):
                    if st.button(item, key=f"notif_item_{i}", width="stretch"):
                        if on_notification_click:
                            on_notification_click(item)
                        else:
                            st.toast(f"Notification sélectionnée : {item}")


def card(title: str | None = None, key: str | None = None):
    """Retourne un st.container(key=...) stylé en carte — À UTILISER EN
    CONTEXT MANAGER :

        with card(title="Historique"):
            st.write(...)

    Ne pas utiliser card_start()/card_end() (supprimés : ils ne
    fonctionnaient pas, cf. note en haut de fichier)."""
    if key is None:
        key = f"card-{next(_card_counter)}"
    container = st.container(key=key)
    if title:
        with container:
            st.markdown(f'<div class="card-header">{title}</div>', unsafe_allow_html=True)
    return container


def badge(text: str, status: str = "healthy") -> str:
    """Retourne le HTML d'un badge pill à insérer dans une table (ex. via
    df.to_html(escape=False)) ou un st.markdown. status ∈ {"healthy",
    "warning", "critical"}. Symboles Unicode simples — pas de dépendance
    de police, jamais traduits."""
    icon = {"healthy": "✓", "warning": "⚠", "critical": "✕"}.get(status, "•")
    return f'<span class="badge badge-{status}">{icon} {text}</span>'


def score_badge(value_text, sub_label: str, level: str = "critical", critical: bool | None = None) -> str:
    """Badge rectangulaire deux lignes pour un score (ex. "82%" /
    "CIS SCORE"). level ∈ {"critical", "healthy"} — rouge sombre si non
    conforme, vert si conforme. `critical` (bool) est accepté en alias :
    critical=True -> level="critical", critical=False -> level="healthy"
    (utile car certains appels utilisent ce nom au lieu de level=).
    value_text peut être un nombre (ex. 82) — sera converti en "82%".
    Retourne du HTML à insérer via st.markdown(..., unsafe_allow_html=True)."""
    if critical is not None:
        level = "critical" if critical else "healthy"
    if isinstance(value_text, (int, float)):
        value_text = f"{value_text}%"
    return (
        f'<div class="score-badge score-badge-{level}">'
        f'<div class="score-badge-value">{value_text}</div>'
        f'<div class="score-badge-label">{sub_label}</div>'
        f'</div>'
    )


def finding_item(title: str, subtitle: str, level: str = "critical", active: bool = False) -> str:
    """Bloc de finding d'audit avec bordure gauche colorée (ex. "Plaintext
    password detected" / "CIS 1.1.1 ..."). level ∈ {"critical", "warning",
    "neutral"}. active=True ajoute une légère mise en avant (fond
    légèrement plus clair) pour le finding actuellement sélectionné/le
    plus important. Retourne du HTML à insérer via st.markdown(unsafe_allow_html=True)."""
    active_class = " finding-active" if active else ""
    return (
        f'<div class="finding finding-{level}{active_class}">'
        f'<div class="finding-title">{title}</div>'
        f'<div class="finding-subtitle">{subtitle}</div>'
        f'</div>'
    )


def code_diff(lines: list[tuple[str, str | None]]) -> None:
    """Affiche un bloc de code monospace avec coloration diff optionnelle
    par ligne. `lines` = liste de tuples (texte, classe) où classe ∈
    {None, "removed", "added"}. Exemple :

        code_diff([
            ("line vty 0 4", None),
            (" login", None),
            (" password cisco", "removed"),
            ("snmp-server community public RO", "removed"),
        ])
    """
    rows = ""
    for text, cls in lines:
        css_class = f"code-line-{cls}" if cls else "code-line"
        # échappement minimal pour éviter la casse du HTML par le contenu
        safe = text.replace("<", "&lt;").replace(">", "&gt;")
        rows += f'<div class="{css_class}">{safe}</div>'
    st.markdown(f'<div class="code-diff-block">{rows}</div>', unsafe_allow_html=True)


def topology_graph(
    nodes: list[dict],
    edges: list[tuple[str, str]],
    view_w: int = 1000,
    view_h: int = 480,
    width: int | None = None,
    height: int | None = None,
) -> None:
    """Graphe de topologie réseau statique en SVG.
    nodes: liste de dict {id, label, x, y, status} — x/y en coordonnées
    du viewBox (0..view_w / 0..view_h), status ∈ {"healthy","warning","critical"}.
    edges: liste de tuples (id_a, id_b) reliés par une ligne.
    width/height sont acceptés en alias de view_w/view_h (certains appels
    utilisent ces noms). Les positions sont à fixer à la main pour
    correspondre à screen.png — ce n'est pas un layout algorithmique,
    juste un rendu fidèle d'un graphe fixe."""
    if width is not None:
        view_w = width
    if height is not None:
        view_h = height
    pos = {n["id"]: n for n in nodes}
    radius_map = {"critical": 34, "warning": 26, "healthy": 22}
    color_map = {
        "critical": "var(--node-critical)",
        "warning": "var(--node-warning)",
        "healthy": "var(--node-healthy)",
    }
    lines_svg = "".join(
        f'<line x1="{pos[a]["x"]}" y1="{pos[a]["y"]}" x2="{pos[b]["x"]}" y2="{pos[b]["y"]}" '
        f'stroke="var(--outline-variant)" stroke-width="2"/>'
        for a, b in edges if a in pos and b in pos
    )
    nodes_svg = ""
    for n in nodes:
        r = radius_map.get(n["status"], 22)
        color = color_map.get(n["status"], "var(--node-healthy)")
        ring = (
            f'<circle cx="{n["x"]}" cy="{n["y"]}" r="{r + 6}" fill="none" '
            f'stroke="{color}" stroke-width="1" opacity="0.4"/>'
            if n["status"] == "critical" else ""
        )
        nodes_svg += (
            f'{ring}<circle cx="{n["x"]}" cy="{n["y"]}" r="{r}" fill="{color}"/>'
            f'<text x="{n["x"]}" y="{n["y"] + r + 20}" text-anchor="middle" '
            f'class="topo-label">{n["label"]}</text>'
        )
    st.markdown(
        f'<svg viewBox="0 0 {view_w} {view_h}" class="topology-svg" '
        f'xmlns="http://www.w3.org/2000/svg">{lines_svg}{nodes_svg}</svg>',
        unsafe_allow_html=True,
    )


def mini_bar_chart(values: list[float], colors: list[str] | None = None, height: int = 40) -> None:
    """Petit graphique en barres (ex. CPU/Mémoire sur 24h). values : liste
    de hauteurs relatives 0-100. colors : couleur par barre (sinon
    couleur automatique teal/orange/rouge selon le seuil de la valeur)."""
    bars = ""
    for i, v in enumerate(values):
        h = max(4, min(100, v))
        if colors and i < len(colors):
            color = colors[i]
        else:
            color = (
                "var(--node-healthy)" if v < 60
                else "var(--node-warning)" if v < 85
                else "var(--node-critical)"
            )
        bars += f'<div class="mini-bar" style="height:{h}%;background:{color};"></div>'
    st.markdown(f'<div class="mini-bar-chart" style="height:{height}px;">{bars}</div>', unsafe_allow_html=True)


def alert_item(icon: str, title: str, subtitle: str) -> str:
    """Item d'alerte/anomalie avec icône, titre et sous-texte (ex. "DDoS
    Suspecté (Port 443)" / "Il y a 15 min - ..."). Retourne du HTML à
    insérer via st.markdown(unsafe_allow_html=True)."""
    return (
        f'<div class="alert-item">'
        f'<div class="alert-icon">{icon}</div>'
        f'<div><div class="alert-title">{title}</div>'
        f'<div class="alert-subtitle">{subtitle}</div></div>'
        f'</div>'
    )


def alert_card(icon: str, title: str, subtitle: str) -> str:
    """Carte d'alerte (utilisée sur le Dashboard). Implémentation
    provisoire identique à alert_item() en attendant le screen.png du
    Dashboard pour vérifier le rendu exact attendu — signale-le si le
    style diffère de la maquette une fois comparé. Retourne du HTML à
    insérer via st.markdown(unsafe_allow_html=True)."""
    return alert_item(icon, title, subtitle)


def field(label: str, value: str, mono_value: bool = False) -> str:
    """Paire label/valeur pour une grille d'identification (ex. "Modèle"
    / "PA-3220"). mono_value=True affiche la valeur en police JetBrains
    Mono (utile pour un numéro de série, une IP, un hash). Retourne du
    HTML à insérer via st.markdown(unsafe_allow_html=True)."""
    value_html = mono(str(value)) if mono_value else value
    return f'<div class="field-label">{label}</div><div class="field-value">{value_html}</div>'


def radar_map(points: list[dict], view_w: int = 1000, view_h: int = 460, width: int | None = None, height: int | None = None) -> None:
    """Carte radar (anneaux concentriques + points colorés) pour la vue
    menaces globales. points: liste de dict {x, y, status} avec x/y en
    coordonnées du viewBox et status ∈ {"critical", "anomaly"}.
    width/height sont acceptés en alias de view_w/view_h (certains appels
    utilisent ces noms)."""
    if width is not None:
        view_w = width
    if height is not None:
        view_h = height
    cx, cy = view_w / 2, view_h / 2
    max_r = min(view_w, view_h) / 2 - 10
    rings_svg = "".join(
        f'<circle cx="{cx}" cy="{cy}" r="{max_r * f}" fill="none" '
        f'stroke="var(--outline-variant)" stroke-width="1"/>'
        for f in (0.35, 0.65, 1.0)
    )
    color_map = {"critical": "var(--node-critical)", "anomaly": "var(--secondary)"}
    dots_svg = "".join(
        f'<circle cx="{p["x"]}" cy="{p["y"]}" r="7" fill="{color_map.get(p["status"], "var(--secondary)")}"/>'
        for p in points
    )
    svg = (
        f'<svg viewBox="0 0 {view_w} {view_h}" class="radar-svg" '
        f'xmlns="http://www.w3.org/2000/svg">{rings_svg}{dots_svg}</svg>'
    )
    st.markdown(f'<div class="radar-wrap">{svg}</div>', unsafe_allow_html=True)


def stat_tile(label: str, value: str, color: str = "var(--on-surface)") -> str:
    """Petite tuile statistique (ex. "ACTIVE VECTORS" / "4"). Retourne du
    HTML à insérer via st.markdown(unsafe_allow_html=True)."""
    return (
        f'<div class="stat-tile"><div class="stat-tile-label">{label}</div>'
        f'<div class="stat-tile-value" style="color:{color};">{value}</div></div>'
    )


def donut_gauge(percent: float, label: str, size: int = 180, stroke: int = 14, color: str = "var(--primary)") -> None:
    """Jauge circulaire (ex. "85% / CIS COMPLIANT")."""
    import math
    r = (size - stroke) / 2
    circumference = 2 * math.pi * r
    offset = circumference * (1 - percent / 100)
    cx = cy = size / 2
    svg = (
        f'<svg viewBox="0 0 {size} {size}" class="donut-svg" xmlns="http://www.w3.org/2000/svg">'
        f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="none" stroke="var(--surface-container-high)" stroke-width="{stroke}"/>'
        f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="none" stroke="{color}" stroke-width="{stroke}" '
        f'stroke-dasharray="{circumference}" stroke-dashoffset="{offset}" stroke-linecap="round" '
        f'transform="rotate(-90 {cx} {cy})"/></svg>'
    )
    st.markdown(
        f'<div class="donut-wrap" style="width:{size}px;height:{size}px;">{svg}'
        f'<div class="donut-center"><div class="donut-value">{percent}%</div>'
        f'<div class="donut-label">{label}</div></div></div>',
        unsafe_allow_html=True,
    )


def progress_row(label: str, percent: float, color: str = "var(--primary)") -> None:
    """Ligne label + pourcentage + barre de progression horizontale (ex.
    "Identity & Access" / 92%)."""
    st.markdown(
        f'<div class="progress-row">'
        f'<div class="progress-row-top"><span>{label}</span><span>{percent}%</span></div>'
        f'<div class="progress-track"><div class="progress-fill" '
        f'style="width:{percent}%;background:{color};"></div></div></div>',
        unsafe_allow_html=True,
    )


def severity_pill(text: str, level: str = "medium") -> str:
    """Badge de sévérité (CRITICAL/HIGH/MEDIUM). level ∈ {"critical",
    "high", "medium"}. Retourne du HTML à insérer via
    st.markdown(unsafe_allow_html=True)."""
    icon = {"critical": "⏱", "high": "⚠", "medium": "ℹ"}.get(level, "ℹ")
    return f'<span class="severity-pill severity-{level}">{icon} {text}</span>'


def trend_chart(
    history: list[float],
    forecast: list[float],
    color: str = "var(--primary)",
    threshold: float | None = None,
    threshold_label: str | None = None,
    view_w: int = 400,
    view_h: int = 140,
) -> None:
    """Mini graphique de tendance : ligne pleine (historique) qui se
    prolonge en ligne pointillée saumon (zone de prédiction), avec une
    ligne verticale pointillée à la jonction et un fond légèrement plus
    clair sur la zone de prédiction. threshold : ligne horizontale de
    référence optionnelle (ex. 100 pour "100% Saturation")."""
    all_vals = history + forecast + ([threshold] if threshold is not None else [])
    vmin, vmax = min(all_vals), max(all_vals)
    vmax = vmax if vmax > vmin else vmin + 1
    n_hist = len(history)
    n_all = n_hist + len(forecast)

    def sx(i: int) -> float:
        return (i / (n_all - 1)) * view_w if n_all > 1 else 0

    def sy(v: float) -> float:
        return view_h - ((v - vmin) / (vmax - vmin)) * (view_h - 20) - 10

    hist_pts = " ".join(f"{sx(i)},{sy(v)}" for i, v in enumerate(history))
    fc_pts = " ".join(
        f"{sx(n_hist - 1 + i)},{sy(v)}" for i, v in enumerate([history[-1]] + forecast)
    )
    split_x = sx(n_hist - 1)

    zone_rect = (
        f'<rect x="{split_x}" y="0" width="{view_w - split_x}" height="{view_h}" '
        f'fill="var(--surface-container-high)" opacity="0.5"/>'
    )
    divider = (
        f'<line x1="{split_x}" y1="0" x2="{split_x}" y2="{view_h}" '
        f'stroke="var(--on-surface)" stroke-width="1" stroke-dasharray="3,3" opacity="0.6"/>'
    )
    threshold_svg = ""
    if threshold is not None:
        ty = sy(threshold)
        threshold_svg = (
            f'<line x1="0" y1="{ty}" x2="{view_w}" y2="{ty}" '
            f'stroke="var(--predictive-accent)" stroke-width="1" stroke-dasharray="4,4"/>'
        )
        if threshold_label:
            threshold_svg += (
                f'<text x="4" y="{ty - 4}" class="trend-threshold-label">{threshold_label}</text>'
            )

    svg = (
        f'<svg viewBox="0 0 {view_w} {view_h}" class="trend-svg" xmlns="http://www.w3.org/2000/svg">'
        f'{zone_rect}{threshold_svg}'
        f'<polyline points="{hist_pts}" fill="none" stroke="{color}" stroke-width="2.5"/>'
        f'<polyline points="{fc_pts}" fill="none" stroke="var(--predictive-accent)" '
        f'stroke-width="2" stroke-dasharray="5,4"/>'
        f'{divider}</svg>'
    )
    st.markdown(svg, unsafe_allow_html=True)


def maintenance_item(name: str, severity_label: str, description: str, eta: str, color: str = "var(--predictive-accent)") -> str:
    """Item de la liste "Urgence Maintenance" : bordure gauche colorée,
    nom + badge de sévérité, description, ETA. Retourne du HTML à insérer
    via st.markdown(unsafe_allow_html=True)."""
    return (
        f'<div class="maint-item" style="border-left-color:{color};">'
        f'<div class="maint-item-top"><span class="maint-item-name">{name}</span>'
        f'<span class="maint-item-severity" style="color:{color};border-color:{color};">{severity_label}</span></div>'
        f'<div class="maint-item-desc">{description}</div>'
        f'<div class="maint-item-eta">⏱ {eta}</div>'
        f'</div>'
    )


def mono(text: str) -> str:
    """Enveloppe une valeur (timestamp, hash, métrique) dans la police
    JetBrains Mono, conformément à DESIGN.md."""
    return f'<span class="mono">{text}</span>'
