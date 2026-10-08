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

### Étape 0 — Rangements & gel de l'avancement
> Objectif : partir d'un dépôt propre et traçable.

- [ ] Commit complet de l'état validé (étapes 1→5), ex. :
      `feat: etapes 1-5 — maintenance, auth MFA, rapports PDF, supervision dynamisee` *(Statut : ⏳ / Date : )*
- [ ] Backup de `backend/sentinelle_aiops.db` **avant** toute suppression (copie hors git).
- [ ] Ajouter au `.gitignore` : `_patch_etape*/`, `_backup_etape*/`, `*.bak_*`, `*.zip` d'étapes,
      `verif*_out.txt` (vérifier l'existant avant).
- [ ] Supprimer du disque : `_patch_etape1..5/`, `_backup_etape3..5/`, `*.bak_etape1..3`,
      `*.db.bak_*`, `etape*_patch.zip`, `files.zip`, doublons PDF (`test_output.pdf`, doublons `docs/`).
- [ ] Vérifier `git status` propre après nettoyage.

**Validation :** `git status` sans artefact ; `pytest -q` toujours à 39 passed.

### Étape 1 — Backend fonctionnel nativement (D2)
> Objectif : « un clone + un script = le backend tourne ».

- [ ] Créer `scripts/start_backend.bat` et `scripts/start_backend.ps1` :
      création/vérification du venv, `pip install -r backend/requirements.txt`,
      lancement `uvicorn main:app` (port 8000) depuis `backend/`.
- [ ] Créer `scripts/start_frontend.bat` / `.ps1` : `streamlit run frontend/app.py` (port 8501).
- [ ] Créer `scripts/start_all.ps1` : backend + frontend, URLs affichées.
- [ ] Créer `scripts/check_env.ps1` : vérifie version Python (>=3.11), venv présent,
      ports 8000/8501 libres.
- [ ] Corriger/valider les commandes du README (§ Installation) contre la réalité :
      `uvicorn backend.main:app` depuis la racine — **à tester** ; sinon documenter le lancement
      depuis `backend/`.
- [ ] Statuer sur `scripts/init_db.py` : il fait `drop_all` (détruit la base !) — le documenter
      comme « réinitialisation complète » et éventuellement proposer une variante non destructive.
- [ ] Tenir à jour `backend/.env` : conserver `SECRET_KEY` générée, documenter les variables
      (`CORS_ORIGINS`, `OLLAMA_BASE_URL`, `OLLAMA_MODEL`).
- [ ] Docker : reléguer en section secondaire du README (« Optionnel / Non maintenu »),
      le laisser tel quel ou supprimer `docker-compose.yml` *(décision mineure à trancher au moment T)*.

**Validation :** depuis un clone vierge, `start_all.ps1` suffit à servir `http://localhost:8000/docs`
et `http://localhost:8501` ; `pytest -q` OK.

---

### Étape 2 — Modernisation du front Streamlit (D1)
> Objectif : base technique à jour, zéro dépendance abandonnée.

- [ ] Passer `streamlit` 1.61.1 → **1.65.0** (`frontend/requirements.txt` + venv) ;
      tester le démarrage de l'app et la page de connexion.
- [ ] **Supprimer `streamlit-autorefresh`** et remplacer tous les `st_autorefresh(interval=5000, ...)`
      par des fragments natifs : `@st.fragment(run_every=5)` autour des zones de données à
      rafraîchir ; conserver le bouton pause (figer l'écran pendant la soutenance) en basculant
      `run_every` à `None`.
      → Cartographie à faire dans : `1_Dashboard.py`, `2_Sécurité.py`, `3_Supervision.py`,
      `4_NetDevOps.py`, `5_Parc_Informatique.py`, `6_Reporting_&_Admin.py`, `7_Assistant_IA.py`,
      `page_template.py`, `components.py`.
- [ ] Remplacer les `datetime.utcnow()` dépréciés par `datetime.now(timezone.utc)`
      côté front **et** back (`admin.py`, `reporting_service.py`, `3_Supervision.py`, etc.).
- [ ] Corriger les warnings d'exécution apparus lors des vérifs (ignorer les
      `ScriptRunContext` bénins, traiter les autres).
- [ ] Mettre à jour les dépendances front mineures (`plotly`, `pandas`…) si compatible ;
      ne pas toucher à `python-telegram-bot` sans besoin.

**Validation :** `python frontend/verif_etape5_supervision.py` → **TOUT EST OK** (backend lancé) ;
rejeu de `verif_etape3_front.py` ; démarrage manuel des 7 pages sans exception ni warning
bloquant ; `pip show streamlit` → 1.65.0 ; plus aucune import `streamlit_autorefresh`.

---


### Étape 3 — Recette globale & soutenance
> Objectif : preuve de bout en bout.

- [ ] `pytest -q` → 39 passed minimum (régression nulle).
- [ ] Parcours manuel des 6 actes de démo via le panneau 1-clic :
      bruteforce → score santé chute ; stress disque → courbe 88% + TTF ; faille CIS →
      3 non-conformités ; reset → nominal. (`verif_etape4.py` pour le PDF.)
- [ ] Vérifier le mode hors-ligne (API coupée) sur toutes les pages : bandeau, pas d'écran rouge.
- [ ] Vérifier MFA TOTP (login admin) + rôles (visiteur/technicien/administrateur).
- [ ] Mettre à jour `ETAT_SITUATION_BACKEND.md` : statuts finaux.

**Validation :** checklist complète cochée ; rien d'échoue.

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

