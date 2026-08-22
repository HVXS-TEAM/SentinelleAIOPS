"""
page_template.py — SQUELETTE OBLIGATOIRE pour toute page Sentinelle AIOps.

RÈGLE : pour créer ou corriger un écran, copier ce fichier, renommer, puis
ne modifier QUE la section "CONTENU DE LA PAGE". Ne jamais réécrire les
sections load_theme / sidebar_nav / top_header à la main — c'est précisément
ce qui provoque le nav dupliqué et le HTML mal injecté.

`active=` doit correspondre EXACTEMENT à un label de NAV_ITEMS dans
components.py (ex: "Dashboard", "Assistant IA", "NetDevOps"...).
"""

import streamlit as st
from components import load_theme, sidebar_nav, top_header, card, badge, mono

# ============================================================
# BOILERPLATE — NE PAS MODIFIER, NE PAS DUPLIQUER LA LOGIQUE À LA MAIN
# ============================================================
st.set_page_config(page_title="Sentinelle AIOps", layout="wide", initial_sidebar_state="expanded")
load_theme()
sidebar_nav(active="REMPLACER_PAR_LE_LABEL_DE_CET_ECRAN")
top_header(search_placeholder="Rechercher entités, requêtes...")
# ============================================================


# ============================================================
# CONTENU DE LA PAGE — seule section à modifier
# ============================================================

# Exemple carte avec badge + valeur mono (cf. screen.png de l'écran concerné
# avant d'écrire quoi que ce soit — la structure DOIT correspondre)
# Exemple carte avec badge + valeur mono (cf. screen.png de l'écran concerné
# avant d'écrire quoi que ce soit — la structure DOIT correspondre)
with card(title="TITRE DE LA CARTE"):
    st.markdown(
        f"Exemple de ligne avec un statut {badge('Critique', 'critical')} "
        f"et une valeur {mono('88.4%')}.",
        unsafe_allow_html=True,
    )

# ============================================================
# FIN CONTENU
# ============================================================


# ============================================================
# CHECKLIST DE VALIDATION — à vérifier avant de considérer l'écran terminé
# (ne pas supprimer ce bloc de commentaire, il sert de rappel à l'agent)
# ============================================================
# [ ] Un seul bloc de navigation visible (pas de doublon en haut de sidebar)
# [ ] Toutes les icônes s'affichent en glyphes, jamais en texte ("search" etc.)
# [ ] Aucun tag HTML brut visible à l'écran (```<div``` etc.) — si ça arrive,
#     l'appel est passé par st.write()/st.text() au lieu de
#     st.markdown(..., unsafe_allow_html=True)
# [ ] Le header ne chevauche pas la barre d'outils Streamlit (Deploy/menu)
# [ ] Couleurs/polices/espacements identiques au screen.png du dossier Ecrans
#     correspondant à cet écran — comparer côte à côte avant de valider
# ============================================================
