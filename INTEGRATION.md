# Intégration theme.css / components.py — Sentinelle AIOps

## Fichiers
- `theme.css` — tokens de couleur, typographie, espacement (source : DESIGN.md)
- `components.py` — sidebar_nav(), top_header(), card_start()/card_end(), badge(), mono()

## Étapes à donner à Antigravity

1. Copier `theme.css` et `components.py` à la racine du projet Streamlit
   (même dossier que le fichier principal `app.py` / `Home.py`).

2. Dans **chaque page** (fichier principal + tous les fichiers du dossier
   `pages/`), en tout début de script, après `st.set_page_config(...)` :

   ```python
   from components import load_theme, sidebar_nav, top_header

   load_theme()
   sidebar_nav(active="Assistant IA")  # adapter le label par page
   top_header(search_placeholder="Rechercher entités, requêtes...")
   ```

3. Remplacer les `st.sidebar.markdown("- Dashboard")` etc. existants par
   l'appel unique à `sidebar_nav()` — supprimer toute navigation sidebar
   native restante pour éviter le doublon.

4. Pour les tableaux de statut (ex. historique sauvegardes, alertes) :
   utiliser `badge()` pour la colonne statut au lieu d'un texte brut, et
   `mono()` pour les colonnes hash/timestamp, en les injectant via
   `st.markdown(df.to_html(escape=False), unsafe_allow_html=True)`
   plutôt que `st.dataframe()` qui n'autorise pas le HTML dans les cellules.

5. Pour chaque écran, comparer le rendu obtenu au `screen.png` du zip Stitch
   correspondant. Ajuster `theme.css`/`components.py` si un écart de
   couleur, police ou espacement apparaît — ne pas ajouter de style inline
   ad hoc dans les pages.
