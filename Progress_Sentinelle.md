# Progress_Sentinelle â€” Feuille de Route Sentinelle AIOps

> **Date de crÃ©ation :** 08/10/2026
> **Objet :** Rendre le backend fonctionnel nativement, moderniser le front-end Streamlit,
> et ranger le dÃ©pÃ´t aprÃ¨s les Ã©tapes 1â†’5. Document de suivi : mettre Ã  jour l'avancement
> au fil de l'eau (colonnes Statut / Date).

---

## 1. Ã‰tat des lieux (au 08/10/2026)

### Ce qui fonctionne
| Composant | Ã‰tat | Preuve |
| :--- | :--- | :--- |
| Backend FastAPI (SQLite, scheduler, 6 services) | âœ… | Lancement uvicorn OK, scheduler dÃ©marrÃ© (tÃ©lÃ©mÃ©trie 10s / TTF 30s / santÃ© 60s) |
| Suite de tests back-end | âœ… | `pytest -q` â†’ **39 passed, 0 failed** (54.7s) |
| Ã‰tapes de remise en Ã©tat 1 â†’ 5 | âœ… validÃ©es | IntÃ©gritÃ© des patches vÃ©rifiÃ©e (hash) ; `verif_etape1..4.py` OK ; `verif_etape5_supervision.py` â†’ **TOUT EST OK** (13/13) |
| Front Streamlit (7 pages, auth MFA, panneau dÃ©mo 1-clic, auto-refresh 5s) | âœ… | RaccordÃ© Ã  l'API via `api_client.py`, mode hors-ligne gÃ©rÃ© |

### Points faibles identifiÃ©s
1. **Aucun script de dÃ©marrage natif** : pas de `.bat`/`.ps1`, le README dÃ©crit des commandes
   qui n'ont jamais Ã©tÃ© validÃ©es de bout en bout (`py -m uvicorn backend.main:app`, `py scripts/init_db.py`).
2. **`streamlit-autorefresh` est abandonnÃ©** (derniÃ¨re release : juin 2023) â€” alors que Streamlit
   intÃ¨gre depuis le refresh natif via `st.fragment(run_every=...)`.
3. **Streamlit 1.61.1 installÃ© / 1.65.0 disponible** â€” mise Ã  jour possible.
4. **Docker Compose non fonctionnel / non validÃ©** (hÃ´te `database` erronÃ© dans `DATABASE_URL`,
   jamais lancÃ©) alors que le README le prÃ©sente comme mode de dÃ©ploiement.
5. **DÃ©pÃ´t encombrÃ©** : dossiers `_patch_etape1..5`, `_backup_etape3..5`, `*.bak_etape*`,
   `*.zip` d'Ã©tapes, doublons de PDF â€” et **aucun commit depuis l'Ã©tape 1**
   (26 fichiers modifiÃ©s non commitÃ©s + une trentaine de fichiers non suivis).
6. **DÃ©prÃ©ciations Python** : `datetime.utcnow()` utilisÃ© dans plusieurs fichiers
   (`admin.py`, `reporting_service.py`, `3_Supervision.py`â€¦) â†’ futurs warnings/ruptures.

---

## 2. DÃ©cisions arrÃªtÃ©es (08/10/2026)

| # | Sujet | DÃ©cision retenue | Alternative Ã©cartÃ©e |
| :---: | :--- | :--- | :--- |
| D1 | StratÃ©gie front-end | **A â€” Moderniser Streamlit** : passage en 1.65.0, remplacement de `streamlit-autorefresh` par les fragments natifs `st.fragment(run_every=...)`, correction des dÃ©prÃ©ciations. Tout le travail existant (7 pages, thÃ¨me, MFA, panneau dÃ©mo) est conservÃ©. | B (Jinja2/HTMX), C (SPA React/Vue), D (double front) â€” rÃ©Ã©cutions trop lourdes pour le gain |
| D2 | Backend Â« nativement Â» | **A â€” Natif complet sans Docker** : venv unique, scripts de dÃ©marrage `.bat`/`.ps1` (backend + frontend), README Ã  jour, SQLite conservÃ©. Docker reste en documentation secondaire. | B (rÃ©parer Docker), C (service Windows) |
| D3 | Artefacts des Ã©tapes 1-5 | **A â€” Commit + suppression** : committer l'avancement validÃ©, puis supprimer `_patch_etape*`, `_backup_etape*`, `*.bak_etape*`, `*.zip` d'Ã©tapes (la base validÃ©e reste dans git). | B (commit seul), C (laisser tel quel) |

**Piste Â« autre frontend Â» (idÃ©e ouverte, non retenue pour l'instant) :** consignÃ©e en Â§6 comme
Ã©volution future â€” une console HTML/Jinja lÃ©gÃ¨re servie par FastAPI (un seul port, un seul
processus) resterait le candidat naturel si un second front est un jour nÃ©cessaire (ex. dÃ©mo sans
installer Streamlit). Ã€ rÃ©Ã©valuer aprÃ¨s la modernisation de D1.

---


## 3. Feuille de route

### Ã‰tape 0 â€” Rangements & gel de l'avancement âœ… TERMINÃ‰E (08/10/2026)
> Objectif : partir d'un dÃ©pÃ´t propre et traÃ§able.

- [x] Commit complet de l'Ã©tat validÃ© (Ã©tapes 1â†’5) : `3369df9`
      `feat: etapes 1-5 â€” maintenance, auth MFA, rapports PDF, supervision dynamisee` (45 fichiers)
- [x] Backup de `backend/sentinelle_aiops.db` â†’ `backup/sentinelle_aiops_20261008_1715.db`
      (dossier `backup/` ajoutÃ© au `.gitignore`).
- [x] `.gitignore` enrichi : `_patch_etape*/`, `_backup_etape*/`, `*.bak_*`, `backup/`,
      `verif*_out.txt`, `verif*_err.txt`, `pytest_out.txt`, `pytest_err.txt`, `backend_uvicorn_*.txt`.
- [x] SupprimÃ© du disque : `_patch_etape1..5/`, `_backup_etape3..5/`, `*.bak_etape1..3`,
      `*.db.bak_*`, `etape*_patch.zip`, `files.zip`, `test_output.pdf`.
- [x] `git rm` des doublons suivis : `Resume_sentinelle.pdf`, `RÃ©sumÃ©_Sentinelle.pdf`
      (copies identiques de `docs/`), `frontend/files.zip` â€” commit `7269b8f`.
- [x] `git status` propre ; **`pytest -q` â†’ 39 passed** aprÃ¨s nettoyage.

**Validation :** âœ… `git status` sans artefact ; âœ… `pytest -q` = 39 passed.

### Ã‰tape 1 â€” Backend fonctionnel nativement (D2) âœ… TERMINÃ‰E (08/10/2026)
> Objectif : Â« un clone + un script = le backend tourne Â».

- [x] `scripts/start_backend.ps1` + `scripts/start_frontend.ps1` : crÃ©ation auto du venv
      si absent, installation des dÃ©pendances au 1er lancement, vÃ©rification du port,
      lancement uvicorn/streamlit. **TestÃ©s** : backend UP (200), frontend UP (200).
- [x] `scripts/start_all.ps1` : prÃ©flight â†’ backend (fenÃªtre dÃ©diÃ©e) â†’ attente /docs â†’
      frontend (fenÃªtre dÃ©diÃ©e) â†’ bandeau URLs. **TestÃ© de bout en bout** : 8000 UP + 8501 UP.
- [x] `scripts/check_env.ps1` : Python â‰¥ 3.11, venv, dÃ©pendances critiques, base SQLite,
      ports libres. **TestÃ© en positif** (ENVIRONNEMENT PRÃŠT, exit 0) **et en nÃ©gatif**
      (blocage de start_all quand une dÃ©pendance critique manque, exit 1).
      `scikit-learn` traitÃ© en **avertissement non bloquant** (repli statistique dans
      `security_service` : `HAS_SKLEARN` + scoring de repli).
- [x] Wrappers double-clic : `demarrer_backend.bat`, `demarrer_frontend.bat`, `demarrer_tout.bat`
      (commentaires ASCII, `%~dp0` quotÃ© pour supporter les chemins Ã  espaces).
- [x] README : section Â« mode natif Â» rÃ©Ã©crite (tableau de dÃ©marrage, commandes manuelles,
      avertissement `init_db.py` destructif, `SECRET_KEY`), Docker relÃ©guÃ© en option
      secondaire non maintenu, section scripts de vÃ©rification ajoutÃ©e.
- [x] Corrections de robustesse : BOM UTF-8 sur les `.ps1` (lecture PowerShell 5.1),
      quotation des chemins Ã  espaces dans `Start-Process -ArgumentList`,
      `$ErrorActionPreference="Continue"` dans `check_env.ps1` (tracebacks non bloquants).

**Point ouvert :** `scikit-learn` n'est **pas encore installÃ©** dans le venv (Python 3.14
nÃ©cessite le wheel `cp314`, tÃ©lÃ©chargement Ã©chouÃ© Ã  cause du rÃ©seau PyPI instable pendant
les tests). L'app fonctionne en mode repli (scores de dÃ©mo identiques : `-0.85`), mais
`pip install scikit-learn` est **Ã  refaire avant une soutenance** pour activer l'Isolation
Forest rÃ©el. `check_env.ps1` le signale Ã  chaque prÃ©flight.

**Validation :** âœ… `check_env` exit 0 ; âœ… `start_all` â†’ 8000 UP + 8501 UP ; âœ… arrÃªt propre.

---

### Ã‰tape 2 â€” Modernisation du front Streamlit (D1)
> Objectif : base technique Ã  jour, zÃ©ro dÃ©pendance abandonnÃ©e.

- [x] Passer `streamlit` 1.61.1 â†’ **1.65.0** (`frontend/requirements.txt` + venv via
      wheel offline `streamlit-1.65.0-py3-none-any.whl`, wheel supprimÃ© aprÃ¨s install) ;
      dÃ©marrage de l'app + page de connexion OK (8000 UP + 8501 UP via `start_all`).
- [x] **Supprimer `streamlit-autorefresh`** (abandonnÃ©, juin 2023, `requirements.txt` nettoyÃ©)
      et le remplacer par un **fragment natif** `@st.fragment(run_every=5)` dans
      `page_template.py` (`_auto_refresh_tick()`) : Ã©quivalent fidÃ¨le du full rerun 5 s
      (pattern officiel `st.rerun()` depuis un fragment), **garde anti-boucle**
      `time.monotonic()` (le corps d'un fragment s'exÃ©cute aussi Ã  chaque run complet),
      bouton pause soutenance conservÃ© (fragment non rendu â†’ timer annulÃ©), fragment
      dÃ©sarmÃ© sous AppTest (`streamlit.testing` dÃ©tectÃ© + `demo_autorefresh_paused=True`
      dans les scripts `verif_*`) pour laisser les vÃ©rifs se terminer.
      â†’ Cartographie : `st_autorefresh` n'Ã©tait utilisÃ© **que** dans `page_template.py`
      (socle commun des 7 pages) â€” aucune des 7 pages n'avait de modernisation Ã  subir.
- [x] Remplacer les `datetime.utcnow()` dÃ©prÃ©ciÃ©s par le helper **`utcnow_naive()`**
      (`backend/app/core/time_utils.py`) : **17 sites back** (services, endpoints,
      maintenance, scheduler, security, tous les `default=` des modÃ¨les, tests,
      `verif_etape2.py`, `init_db.py`) + **3 sites front** (`1_Dashboard.py`,
      `2_SÃ©curitÃ©.py`, `3_Supervision.py`). NaÃ¯f conservÃ© volontairement (colonnes
      SQLite sans fuseau, comparaisons naÃ¯f/naÃ¯f partout â€” passer en aware casserait
      les soustractions) ; imports `datetime` morts nettoyÃ©s.
- [x] Traiter les warnings : migration **`use_container_width` â†’ `width`**
      (`True`â†’`"stretch"`, `False`â†’`"content"`, 5 sites : `app.py`, `components.py` Ã—2,
      `page_template.py` Ã—2, `1_Dashboard.py` Ã—2) car Streamlit 1.65 Ã©met un
      DeprecationWarning (suppression annoncÃ©e aprÃ¨s le 31/12/2025) ; `ScriptRunContext`
      bÃ©nins ignorÃ©s comme prÃ©vu.
- [ ] Mettre Ã  jour les dÃ©pendances front mineures (`plotly`, `pandas`â€¦) si compatible ;
      ne pas toucher Ã  `python-telegram-bot` sans besoin. (**ReportÃ©** : rÃ©seau PyPI
      instable â€” `scikit-learn` reste Ã  installer, `check_env` le signale en `[ATTN]`.)

**Validation :** âœ… `verif_etape5_supervision.py` â†’ **TOUT EST OK** (13/13, backend lancÃ©,
Streamlit 1.65.0) ; âœ… `pytest -q` â†’ 39 passed ; âœ… `check_env` exit 0 avec contrÃ´le
`streamlit >= 1.65` ; âœ… `pip show streamlit` â†’ 1.65.0 ;
âœ… zÃ©ro rÃ©fÃ©rence `streamlit_autorefresh` / `st_autorefresh` / `use_container_width` /
`utcnow()` dans le code projet. Commit `5277f3d` (26 fichiers).

---


### Ã‰tape 3 â€” Recette globale & soutenance
> Objectif : preuve de bout en bout.

- [x] `pytest -q` â†’ 39 passed minimum (rÃ©gression nulle).
- [x] Parcours manuel des 6 actes de dÃ©mo via le panneau 1-clic :
      bruteforce â†’ score santÃ© chute ; stress disque â†’ courbe 88% + TTF ; faille CIS â†’
      3 non-conformitÃ©s ; reset â†’ nominal. (`verif_etape4.py` pour le PDF.)
      â†’ Script rejouable `recette_6actes.ps1` : **6/6 OK** (PDF validÃ© 68 Ko, magic `%PDF`).
- [x] VÃ©rifier le mode hors-ligne (API coupÃ©e) sur toutes les pages : bandeau, pas d'Ã©cran rouge.
      â†’ Nouveau `frontend/verif_hors_ligne_pages.py` : **14/14 OK** (7 pages, aucune exception,
      bandeau d'avertissement partout). Seuls les `ScriptRunContext` bÃ©nins ignorÃ©s.
- [x] VÃ©rifier MFA TOTP (login admin) + rÃ´les (visiteur/technicien/administrateur).
      â†’ `frontend/verif_etape3_front.py` : **TOUT EST OK (16/16)** (MFA, rÃ´les, hors-ligne, session expirÃ©e).
- [x] Mettre Ã  jour `ETAT_SITUATION_BACKEND.md` : statuts finaux.

**Validation :** âœ… checklist complÃ¨te cochÃ©e ; rien n'a Ã©chouÃ©.
pytest 39 passed Â· verif_etape3 16/16 Â· verif_etape5 13/13 Â· hors-ligne 7 pages 14/14 Â·
6 actes dÃ©mo 6/6. Base sauvegardÃ©e dans `backup/`.

### Ã‰tape 4 â€” Documentation
- [x] README : instructions natives (scripts), section Docker secondaire, versions rÃ©elles
      (Python 3.14, Streamlit 1.65, FastAPI, SQLite), identifiants dÃ©mo Ã  jour. Section
      Â« Scripts de vÃ©rification Â» complÃ©tÃ©e (7 scripts verif_* + recette_6actes.ps1 rejouable).
- [x] Ce fichier `Progress_Sentinelle.md` : statuts/dates renseignÃ©s au fil de l'eau.

**Validation :** âœ… README relu de bout en bout â€” versions conformes au venv rÃ©el, aucune
rÃ©fÃ©rence orpheline, section recette alignÃ©e sur les scripts prÃ©sents. Toutes les Ã©tapes 0â†’4
sont dÃ©sormais terminÃ©es.

---

## 4. Ordre d'exÃ©cution & estimation

| Ordre | Ã‰tape | Effort estimÃ© | DÃ©pend de |
| :---: | :--- | :--- | :--- |
| 1 | Ã‰tape 0 â€” Commit + rangements | â±ï¸ court (30 min) | â€” |
| 2 | Ã‰tape 1 â€” Scripts natifs + README | â±ï¸ moyen (1-2 h) | Ã‰tape 0 |
| 3 | Ã‰tape 2 â€” Modernisation Streamlit | â±ï¸ moyen-plus (2-4 h) | Ã‰tape 1 (pour valider en rÃ©el) |
| 4 | Ã‰tape 3 â€” Recette globale | â±ï¸ court (1 h) | Ã‰tapes 1+2 |
| 5 | Ã‰tape 4 â€” Documentation | â±ï¸ court (30 min) | Ã‰tape 3 |

**RÃ¨gle de sÃ©curitÃ© :** sauvegarder `backend/sentinelle_aiops.db` **avant** l'Ã©tape 0
(une fois les `.bak` supprimÃ©s, le seul repli est git â€” et la base n'y est pas versionnable
en l'Ã©tat).

---

## 5. Risques identifiÃ©s

| Risque | Impact | Parade |
| :--- | :---: | :--- |
| Migration Streamlit 1.61 â†’ 1.65 casse un composant (thÃ¨me, `AppTest`, proto `st.html`) | Moyen | Rejouer `verif_etape5_supervision.py` + `verif_etape3_front.py` aprÃ¨s mise Ã  jour ; rollback venv possible |
| `st.fragment` change le comportement de rafraÃ®chissement (session state, callbacks) | Moyen | Refactor page par page, validation intermÃ©diaire Ã  chaque page |
| Suppression des artefacts = perte d'une source de vÃ©ritÃ© | Fort | **Commit d'abord** (D3) ; backup base de donnÃ©es avant |
| `init_db.py` exÃ©cutÃ© par erreur â†’ perte des donnÃ©es dÃ©mo | Fort | Le documenter clairement dans le README comme destructif |
| `pytest` Ã©choue aprÃ¨s mise Ã  jour des dÃ©pendances | Moyen | Fixer les versions dans requirements, comparer avant/aprÃ¨s |

---

## 6. Ã‰volution future (hors pÃ©rimÃ¨tre actuel)

- **Second front lÃ©ger** (idÃ©e ouverte, Ã©cartÃ©e en D1 pour l'instant) : console HTML/Jinja2/HTMX
  servie par FastAPI sur le port 8000 â€” un seul processus Ã  dÃ©montrer, utile si Streamlit devient
  un frein (dÃ©mo sans installation lourde). Ã€ rÃ©Ã©valuer aprÃ¨s l'Ã©tape 2.
- Phase 4 du plan d'origine (`ETAT_SITUATION_BACKEND.md`) : hardening & couverture de tests accrue.
- RÃ©paration du `docker-compose.yml` si le dÃ©ploiement conteneurisÃ© redevient un objectif
  (hÃ´te `database` erronÃ© dans `DATABASE_URL`, jamais validÃ©).

---

## 7. Journal des mises Ã  jour

| Date | Ã‰vÃ©nement |
| :--- | :--- |
| 08/10/2026 | CrÃ©ation du document. DÃ©cisions D1 (Streamlit modernisÃ©), D2 (natif sans Docker), D3 (commit + nettoyage) arrÃªtÃ©es. Validation des Ã©tapes 1â†’5 confirmÃ©e (39 tests OK, verif_etape5 TOUT EST OK). |
| 08/10/2026 | **Ã‰tape 0 terminÃ©e** : commits `3369df9` (Ã©tat validÃ©, 45 fichiers) + `7269b8f` (suppression artefacts), backup base `backup/sentinelle_aiops_20261008_1715.db`, `.gitignore` enrichi, pytest 39 passed aprÃ¨s nettoyage. |
| 08/10/2026 | **Ã‰tape 1 terminÃ©e** : scripts natifs `check_env/start_backend/start_frontend/start_all` (.ps1) + 3 wrappers `.bat`, README rÃ©Ã©crit (mode natif, Docker secondaire), tests positif/nÃ©gatif OK, `start_all` validÃ© de bout en bout (8000+8501 UP). Point ouvert : installation `scikit-learn` Ã  refaire (rÃ©seau PyPI instable). |
| 08/10/2026 | **Ã‰tape 2 terminÃ©e** : Streamlit 1.65.0 (wheel offline), `streamlit-autorefresh` supprimÃ© â†’ fragment natif `@st.fragment(run_every=5)` avec garde anti-boucle + pause soutenance + dÃ©sarmement AppTest, `utcnow()` â†’ helper `utcnow_naive()` (17 sites back + 3 front), `use_container_width` â†’ `width`. Validations : verif_etape5 TOUT EST OK (13/13), pytest 39 passed, check_env exit 0. Commit `5277f3d` (26 fichiers). Reste reportÃ© : dÃ©pendances mineures + `scikit-learn` (rÃ©seau PyPI instable). |
| 08/10/2026 | **Ã‰tape 3 terminÃ©e** : recette globale validÃ©e sans Ã©chec â€” pytest 39 passed, verif_etape3 (MFA/rÃ´les/hors-ligne/session) 16/16, verif_etape5 (TTF) 13/13, **nouveau** `verif_hors_ligne_pages.py` 14/14 (7 pages), 6 actes dÃ©mo 6/6 (PDF validÃ© `%PDF`, 68 Ko). Base sauvegardÃ©e `backup/sentinelle_aiops_20261008_2225.db`. Suivi `Progress_Sentinelle.md` + `ETAT_SITUATION_BACKEND.md` mis Ã  jour (Phase 3 â†’ TERMINÃ‰, Â§5 note de recette). Reste : Ã©tape 4 (doc finale). |
| 08/10/2026 | **Ã‰tape 4 terminÃ©e** : README finalisÃ© (en-tÃªte tech rÃ©el : Python 3.14 / Streamlit 1.65 / FastAPI / SQLite ; section Â« Scripts de vÃ©rification Â» complÃ©tÃ©e avec les 7 scripts `verif_*` + `recette_6actes.ps1` rejouable). Feuille de route 0â†’4 **entiÃ¨rement bouclÃ©e**. Backend/scheduler arrÃªtÃ©s proprement, ports 8000/8501 libÃ©rÃ©s, working tree nettoyÃ© (base restaurÃ©e Ã  l'Ã©tat commitÃ©). |
@08/10/2026 | **Clôture** : scikit-learn 1.9.1 + scipy 1.16.3 installés (`HAS_SKLEARN=True`, Isolation Forest actif dans `security_service`), suite complète 39 passed sans régression, préflight `check_env.ps1` tout OK, ports 8000/8501 libérés, working tree propre, base restaurée.  | 
