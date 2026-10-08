# Progress_Sentinelle — Feuille de Route Sentinelle AIOps

> **Date de création :** 08/10/2026
> **Objet :** Rendre le backend fonctionnel nativement, moderniser le front-end Streamlit,
> et ranger le dépôt après les étapes 1→5. Document de suivi : mettre à jour l'avancement
> au fil de l'eau (colonnes Statut / Date).

---

## 1. État des lieux (au 08/10/2026)

### Ce qui fonctionne
| Composant | État | Preuve |
| :--- | :--- | :--- |
| Backend FastAPI (SQLite, scheduler, 6 services) | ✅ | Lancement uvicorn OK, scheduler démarré (télémétrie 10s / TTF 30s / santé 60s) |
| Suite de tests back-end | ✅ | `pytest -q` → **39 passed, 0 failed** (54.7s) |
| Étapes de remise en état 1 → 5 | ✅ validées | Intégrité des patches vérifiée (hash) ; `verif_etape1..4.py` OK ; `verif_etape5_supervision.py` → **TOUT EST OK** (13/13) |
| Front Streamlit (7 pages, auth MFA, panneau démo 1-clic, auto-refresh 5s) | ✅ | Raccordé à l'API via `api_client.py`, mode hors-ligne géré |

### Points faibles identifiés
1. **Aucun script de démarrage natif** : pas de `.bat`/`.ps1`, le README décrit des commandes
   qui n'ont jamais été validées de bout en bout (`py -m uvicorn backend.main:app`, `py scripts/init_db.py`).
2. **`streamlit-autorefresh` est abandonné** (dernière release : juin 2023) — alors que Streamlit
   intègre depuis le refresh natif via `st.fragment(run_every=...)`.
3. **Streamlit 1.61.1 installé / 1.65.0 disponible** — mise à jour possible.
4. **Docker Compose non fonctionnel / non validé** (hôte `database` erroné dans `DATABASE_URL`,
   jamais lancé) alors que le README le présente comme mode de déploiement.
5. **Dépôt encombré** : dossiers `_patch_etape1..5`, `_backup_etape3..5`, `*.bak_etape*`,
   `*.zip` d'étapes, doublons de PDF — et **aucun commit depuis l'étape 1**
   (26 fichiers modifiés non commités + une trentaine de fichiers non suivis).
6. **Dépréciations Python** : `datetime.utcnow()` utilisé dans plusieurs fichiers
   (`admin.py`, `reporting_service.py`, `3_Supervision.py`…) → futurs warnings/ruptures.

---

## 2. Décisions arrêtées (08/10/2026)

| # | Sujet | Décision retenue | Alternative écartée |
| :---: | :--- | :--- | :--- |
| D1 | Stratégie front-end | **A — Moderniser Streamlit** : passage en 1.65.0, remplacement de `streamlit-autorefresh` par les fragments natifs `st.fragment(run_every=...)`, correction des dépréciations. Tout le travail existant (7 pages, thème, MFA, panneau démo) est conservé. | B (Jinja2/HTMX), C (SPA React/Vue), D (double front) — réécutions trop lourdes pour le gain |
| D2 | Backend « nativement » | **A — Natif complet sans Docker** : venv unique, scripts de démarrage `.bat`/`.ps1` (backend + frontend), README à jour, SQLite conservé. Docker reste en documentation secondaire. | B (réparer Docker), C (service Windows) |
| D3 | Artefacts des étapes 1-5 | **A — Commit + suppression** : committer l'avancement validé, puis supprimer `_patch_etape*`, `_backup_etape*`, `*.bak_etape*`, `*.zip` d'étapes (la base validée reste dans git). | B (commit seul), C (laisser tel quel) |

**Piste « autre frontend » (idée ouverte, non retenue pour l'instant) :** consignée en §6 comme
évolution future — une console HTML/Jinja légère servie par FastAPI (un seul port, un seul
processus) resterait le candidat naturel si un second front est un jour nécessaire (ex. démo sans
installer Streamlit). À réévaluer après la modernisation de D1.

---


## 3. Feuille de route

### Étape 0 — Rangements & gel de l'avancement ✅ TERMINÉE (08/10/2026)
> Objectif : partir d'un dépôt propre et traçable.

- [x] Commit complet de l'état validé (étapes 1→5) : `3369df9`
      `feat: etapes 1-5 — maintenance, auth MFA, rapports PDF, supervision dynamisee` (45 fichiers)
- [x] Backup de `backend/sentinelle_aiops.db` → `backup/sentinelle_aiops_20261008_1715.db`
      (dossier `backup/` ajouté au `.gitignore`).
- [x] `.gitignore` enrichi : `_patch_etape*/`, `_backup_etape*/`, `*.bak_*`, `backup/`,
      `verif*_out.txt`, `verif*_err.txt`, `pytest_out.txt`, `pytest_err.txt`, `backend_uvicorn_*.txt`.
- [x] Supprimé du disque : `_patch_etape1..5/`, `_backup_etape3..5/`, `*.bak_etape1..3`,
      `*.db.bak_*`, `etape*_patch.zip`, `files.zip`, `test_output.pdf`.
- [x] `git rm` des doublons suivis : `Resume_sentinelle.pdf`, `Résumé_Sentinelle.pdf`
      (copies identiques de `docs/`), `frontend/files.zip` — commit `7269b8f`.
- [x] `git status` propre ; **`pytest -q` → 39 passed** après nettoyage.

**Validation :** ✅ `git status` sans artefact ; ✅ `pytest -q` = 39 passed.

### Étape 1 — Backend fonctionnel nativement (D2) ✅ TERMINÉE (08/10/2026)
> Objectif : « un clone + un script = le backend tourne ».

- [x] `scripts/start_backend.ps1` + `scripts/start_frontend.ps1` : création auto du venv
      si absent, installation des dépendances au 1er lancement, vérification du port,
      lancement uvicorn/streamlit. **Testés** : backend UP (200), frontend UP (200).
- [x] `scripts/start_all.ps1` : préflight → backend (fenêtre dédiée) → attente /docs →
      frontend (fenêtre dédiée) → bandeau URLs. **Testé de bout en bout** : 8000 UP + 8501 UP.
- [x] `scripts/check_env.ps1` : Python ≥ 3.11, venv, dépendances critiques, base SQLite,
      ports libres. **Testé en positif** (ENVIRONNEMENT PRÊT, exit 0) **et en négatif**
      (blocage de start_all quand une dépendance critique manque, exit 1).
      `scikit-learn` traité en **avertissement non bloquant** (repli statistique dans
      `security_service` : `HAS_SKLEARN` + scoring de repli).
- [x] Wrappers double-clic : `demarrer_backend.bat`, `demarrer_frontend.bat`, `demarrer_tout.bat`
      (commentaires ASCII, `%~dp0` quoté pour supporter les chemins à espaces).
- [x] README : section « mode natif » réécrite (tableau de démarrage, commandes manuelles,
      avertissement `init_db.py` destructif, `SECRET_KEY`), Docker relégué en option
      secondaire non maintenu, section scripts de vérification ajoutée.
- [x] Corrections de robustesse : BOM UTF-8 sur les `.ps1` (lecture PowerShell 5.1),
      quotation des chemins à espaces dans `Start-Process -ArgumentList`,
      `$ErrorActionPreference="Continue"` dans `check_env.ps1` (tracebacks non bloquants).

**Point ouvert :** `scikit-learn` n'est **pas encore installé** dans le venv (Python 3.14
nécessite le wheel `cp314`, téléchargement échoué à cause du réseau PyPI instable pendant
les tests). L'app fonctionne en mode repli (scores de démo identiques : `-0.85`), mais
`pip install scikit-learn` est **à refaire avant une soutenance** pour activer l'Isolation
Forest réel. `check_env.ps1` le signale à chaque préflight.

**Validation :** ✅ `check_env` exit 0 ; ✅ `start_all` → 8000 UP + 8501 UP ; ✅ arrêt propre.

---

### Étape 2 — Modernisation du front Streamlit (D1)
> Objectif : base technique à jour, zéro dépendance abandonnée.

- [x] Passer `streamlit` 1.61.1 → **1.65.0** (`frontend/requirements.txt` + venv via
      wheel offline `streamlit-1.65.0-py3-none-any.whl`, wheel supprimé après install) ;
      démarrage de l'app + page de connexion OK (8000 UP + 8501 UP via `start_all`).
- [x] **Supprimer `streamlit-autorefresh`** (abandonné, juin 2023, `requirements.txt` nettoyé)
      et le remplacer par un **fragment natif** `@st.fragment(run_every=5)` dans
      `page_template.py` (`_auto_refresh_tick()`) : équivalent fidèle du full rerun 5 s
      (pattern officiel `st.rerun()` depuis un fragment), **garde anti-boucle**
      `time.monotonic()` (le corps d'un fragment s'exécute aussi à chaque run complet),
      bouton pause soutenance conservé (fragment non rendu → timer annulé), fragment
      désarmé sous AppTest (`streamlit.testing` détecté + `demo_autorefresh_paused=True`
      dans les scripts `verif_*`) pour laisser les vérifs se terminer.
      → Cartographie : `st_autorefresh` n'était utilisé **que** dans `page_template.py`
      (socle commun des 7 pages) — aucune des 7 pages n'avait de modernisation à subir.
- [x] Remplacer les `datetime.utcnow()` dépréciés par le helper **`utcnow_naive()`**
      (`backend/app/core/time_utils.py`) : **17 sites back** (services, endpoints,
      maintenance, scheduler, security, tous les `default=` des modèles, tests,
      `verif_etape2.py`, `init_db.py`) + **3 sites front** (`1_Dashboard.py`,
      `2_Sécurité.py`, `3_Supervision.py`). Naïf conservé volontairement (colonnes
      SQLite sans fuseau, comparaisons naïf/naïf partout — passer en aware casserait
      les soustractions) ; imports `datetime` morts nettoyés.
- [x] Traiter les warnings : migration **`use_container_width` → `width`**
      (`True`→`"stretch"`, `False`→`"content"`, 5 sites : `app.py`, `components.py` ×2,
      `page_template.py` ×2, `1_Dashboard.py` ×2) car Streamlit 1.65 émet un
      DeprecationWarning (suppression annoncée après le 31/12/2025) ; `ScriptRunContext`
      bénins ignorés comme prévu.
- [ ] Mettre à jour les dépendances front mineures (`plotly`, `pandas`…) si compatible ;
      ne pas toucher à `python-telegram-bot` sans besoin. (**Reporté** : réseau PyPI
      instable — `scikit-learn` reste à installer, `check_env` le signale en `[ATTN]`.)

**Validation :** ✅ `verif_etape5_supervision.py` → **TOUT EST OK** (13/13, backend lancé,
Streamlit 1.65.0) ; ✅ `pytest -q` → 39 passed ; ✅ `check_env` exit 0 avec contrôle
`streamlit >= 1.65` ; ✅ `pip show streamlit` → 1.65.0 ;
✅ zéro référence `streamlit_autorefresh` / `st_autorefresh` / `use_container_width` /
`utcnow()` dans le code projet. Commit `5277f3d` (26 fichiers).

---


### Étape 3 — Recette globale & soutenance
> Objectif : preuve de bout en bout.

- [x] `pytest -q` → 39 passed minimum (régression nulle).
- [x] Parcours manuel des 6 actes de démo via le panneau 1-clic :
      bruteforce → score santé chute ; stress disque → courbe 88% + TTF ; faille CIS →
      3 non-conformités ; reset → nominal. (`verif_etape4.py` pour le PDF.)
      → Script rejouable `recette_6actes.ps1` : **6/6 OK** (PDF validé 68 Ko, magic `%PDF`).
- [x] Vérifier le mode hors-ligne (API coupée) sur toutes les pages : bandeau, pas d'écran rouge.
      → Nouveau `frontend/verif_hors_ligne_pages.py` : **14/14 OK** (7 pages, aucune exception,
      bandeau d'avertissement partout). Seuls les `ScriptRunContext` bénins ignorés.
- [x] Vérifier MFA TOTP (login admin) + rôles (visiteur/technicien/administrateur).
      → `frontend/verif_etape3_front.py` : **TOUT EST OK (16/16)** (MFA, rôles, hors-ligne, session expirée).
- [x] Mettre à jour `ETAT_SITUATION_BACKEND.md` : statuts finaux.

**Validation :** ✅ checklist complète cochée ; rien n'a échoué.
pytest 39 passed · verif_etape3 16/16 · verif_etape5 13/13 · hors-ligne 7 pages 14/14 ·
6 actes démo 6/6. Base sauvegardée dans `backup/`.

### Étape 4 — Documentation
- [ ] README : instructions natives (scripts), section Docker secondaire, versions réelles
      (Python, Streamlit 1.65, FastAPI), identifiants démo à jour.
- [ ] Ce fichier `Progress_Sentinelle.md` : statuts/dates renseignés au fil de l'eau.

---

## 4. Ordre d'exécution & estimation

| Ordre | Étape | Effort estimé | Dépend de |
| :---: | :--- | :--- | :--- |
| 1 | Étape 0 — Commit + rangements | ⏱️ court (30 min) | — |
| 2 | Étape 1 — Scripts natifs + README | ⏱️ moyen (1-2 h) | Étape 0 |
| 3 | Étape 2 — Modernisation Streamlit | ⏱️ moyen-plus (2-4 h) | Étape 1 (pour valider en réel) |
| 4 | Étape 3 — Recette globale | ⏱️ court (1 h) | Étapes 1+2 |
| 5 | Étape 4 — Documentation | ⏱️ court (30 min) | Étape 3 |

**Règle de sécurité :** sauvegarder `backend/sentinelle_aiops.db` **avant** l'étape 0
(une fois les `.bak` supprimés, le seul repli est git — et la base n'y est pas versionnable
en l'état).

---

## 5. Risques identifiés

| Risque | Impact | Parade |
| :--- | :---: | :--- |
| Migration Streamlit 1.61 → 1.65 casse un composant (thème, `AppTest`, proto `st.html`) | Moyen | Rejouer `verif_etape5_supervision.py` + `verif_etape3_front.py` après mise à jour ; rollback venv possible |
| `st.fragment` change le comportement de rafraîchissement (session state, callbacks) | Moyen | Refactor page par page, validation intermédiaire à chaque page |
| Suppression des artefacts = perte d'une source de vérité | Fort | **Commit d'abord** (D3) ; backup base de données avant |
| `init_db.py` exécuté par erreur → perte des données démo | Fort | Le documenter clairement dans le README comme destructif |
| `pytest` échoue après mise à jour des dépendances | Moyen | Fixer les versions dans requirements, comparer avant/après |

---

## 6. Évolution future (hors périmètre actuel)

- **Second front léger** (idée ouverte, écartée en D1 pour l'instant) : console HTML/Jinja2/HTMX
  servie par FastAPI sur le port 8000 — un seul processus à démontrer, utile si Streamlit devient
  un frein (démo sans installation lourde). À réévaluer après l'étape 2.
- Phase 4 du plan d'origine (`ETAT_SITUATION_BACKEND.md`) : hardening & couverture de tests accrue.
- Réparation du `docker-compose.yml` si le déploiement conteneurisé redevient un objectif
  (hôte `database` erroné dans `DATABASE_URL`, jamais validé).

---

## 7. Journal des mises à jour

| Date | Événement |
| :--- | :--- |
| 08/10/2026 | Création du document. Décisions D1 (Streamlit modernisé), D2 (natif sans Docker), D3 (commit + nettoyage) arrêtées. Validation des étapes 1→5 confirmée (39 tests OK, verif_etape5 TOUT EST OK). |
| 08/10/2026 | **Étape 0 terminée** : commits `3369df9` (état validé, 45 fichiers) + `7269b8f` (suppression artefacts), backup base `backup/sentinelle_aiops_20261008_1715.db`, `.gitignore` enrichi, pytest 39 passed après nettoyage. |
| 08/10/2026 | **Étape 1 terminée** : scripts natifs `check_env/start_backend/start_frontend/start_all` (.ps1) + 3 wrappers `.bat`, README réécrit (mode natif, Docker secondaire), tests positif/négatif OK, `start_all` validé de bout en bout (8000+8501 UP). Point ouvert : installation `scikit-learn` à refaire (réseau PyPI instable). |
| 08/10/2026 | **Étape 2 terminée** : Streamlit 1.65.0 (wheel offline), `streamlit-autorefresh` supprimé → fragment natif `@st.fragment(run_every=5)` avec garde anti-boucle + pause soutenance + désarmement AppTest, `utcnow()` → helper `utcnow_naive()` (17 sites back + 3 front), `use_container_width` → `width`. Validations : verif_etape5 TOUT EST OK (13/13), pytest 39 passed, check_env exit 0. Commit `5277f3d` (26 fichiers). Reste reporté : dépendances mineures + `scikit-learn` (réseau PyPI instable). |
| 08/10/2026 | **Étape 3 terminée** : recette globale validée sans échec — pytest 39 passed, verif_etape3 (MFA/rôles/hors-ligne/session) 16/16, verif_etape5 (TTF) 13/13, **nouveau** `verif_hors_ligne_pages.py` 14/14 (7 pages), 6 actes démo 6/6 (PDF validé `%PDF`, 68 Ko). Base sauvegardée `backup/sentinelle_aiops_20261008_2225.db`. Suivi `Progress_Sentinelle.md` + `ETAT_SITUATION_BACKEND.md` mis à jour (Phase 3 → TERMINÉ, §5 note de recette). Reste : étape 4 (doc finale). |

