# État de Situation & Feuille de Route – Sentinelle AIOps (BTS SIO / Épreuve E6)

---

## 1. Contexte & Problématique Initiale
Initialement, le back-end de **Sentinelle AIOps** (FastAPI + SQLAlchemy + SQLite) disposait de toute la logique algorithmique nécessaire (*Isolation Forest*, régression linéaire *Time-To-Failure*, audit *CIS Benchmark*), mais demeurait **passif** :
- Les métriques devaient être injectées manuellement via l'API pour que les calculs s'exécutent.
- Sans action humaine ou script externe, la base de données n'évoluait pas et les alertes ne se déclenchaient pas en continu.
- Le front-end Streamlit reposait sur des données statiques / mockées sans lien dynamique avec l'état réel de l'infrastructure.

---

## 2. Réalisations & Évolution de l'Architecture

### Phase 1 : Moteur d'Arrière-Plan Autonome (APScheduler) — ✅ TERMINÉ & VALIDÉ
Un scheduler asynchrone autonome a été conçu et intégré dans le cycle de vie de FastAPI sans toucher à la moindre ligne de code des services métiers existants :

1. **Création du module autonome :** [`backend/app/core/scheduler.py`](file:///d:/Projets%20Edwin/BTS%20Projects/Sentinelle%20AIOPS/backend/app/core/scheduler.py)
   - **Job Télémétrie (toutes les 10s) :** Simule la collecte de métriques système (CPU, RAM, Disque, Bande passante) pour les 4 équipements du parc (`SW-CORE-01`, `RTR-EDGE-01`, `SRV-APP-01`, `SRV-DB-01`) avec variation réaliste et écriture en base.
   - **Job Prédiction TTF (toutes les 30s) :** Exécute automatiquement `supervision_service.calculate_ttf()` pour anticiper les pannes de disque.
   - **Job Santé du Parc (toutes les 60s) :** Réévalue le score de santé global des équipements via `inventory_service.calculate_health_score()`.
   
2. **Branchage sur le cycle de vie applicatif :** [`backend/main.py`](file:///d:/Projets%20Edwin/BTS%20Projects/Sentinelle%20AIOPS/backend/main.py)
   - Utilisation d'un `lifespan` asynchrone (`@asynccontextmanager`) pour démarrer (`start_scheduler()`) et arrêter proprement (`stop_scheduler()`) les tâches de fond lors du boot/shutdown du serveur.
   - Validation opérationnelle : génération continue des métriques constatée et confirmée.

---

### Phase 2 : Routeur de Simulation Déterministe pour Démo BTS — ✅ TERMINÉ & VALIDÉ
Pour sécuriser la soutenance orale sans dépendre d'outils d'attaque externes (ex. machine Kali Linux, saturation manuelle `dd`), un routeur interactif dédié a été développé et intégré :

1. **Création du module :** [`backend/app/api/v1/endpoints/simulation.py`](file:///d:/Projets%20Edwin/BTS%20Projects/Sentinelle%20AIOPS/backend/app/api/v1/endpoints/simulation.py)
   - **`POST /api/v1/simulation/inject-bruteforce` (Acte 3 - Sécurité) :** Injection d'un lot de 10 logs SSH brute-force synthétiques (`198.51.100.45`) traité par `security_service.analyze_log_batch()` (*Isolation Forest*).
   - **`POST /api/v1/simulation/stress-disk` (Acte 2 - Supervision) :** Simulation d'une montée rapide du disque sur `SRV-APP-01` (60% à 88%) et calcul immédiat de la régression linéaire via `supervision_service.calculate_ttf()`.
   - **`POST /api/v1/simulation/cis-flaw` (Acte 4 - NetDevOps) :** Injection d'une configuration Cisco non conforme (SNMP public/private, absence motd) auditée par `netdevops_service.run_full_audit()` (*CIS Benchmark*).
   - **`POST /api/v1/simulation/reset` :** Purge des données synthétiques et restauration immédiate des scores de santé nominaux.

2. **Raccordement et Validation :** [`backend/app/api/v1/router.py`](file:///d:/Projets%20Edwin/BTS%20Projects/Sentinelle%20AIOPS/backend/app/api/v1/router.py)
   - Routeur inclus avec succès sous le préfixe `/simulation` (tag `Simulation Démo`).
   - Tests automatisés exécutés sur les 4 routes avec réponses HTTP 200 OK et conformité fonctionnelle validée.

---

## 3. Phase 3 : Spécification Détaillée de la Dynamisation Front-End Streamlit

```
┌───────────────────────────────────────────────────────────────────────────────────┐
│                           ARCHITECTURE FRONT-END STREAMLIT                        │
├───────────────────────────────────────────────────────────────────────────────────┤
│                                                                                   │
│   ┌───────────────────────────────────────────────────────────────────────────┐   │
│   │                 PANNEAU LATÉRAL DE CONTRÔLE DÉMO (1-CLIC)                 │   │
│   │  [🔴 Acte 3 : Brute-Force]   [🟡 Acte 2 : Stress Disque]                 │   │
│   │  [🔵 Acte 4 : Faille CIS]    [🟢 Reset Nominal]                          │   │
│   └─────────────────────────────────────┬─────────────────────────────────────┘   │
│                                         │ Déclenchements POST                     │
│                                         ▼                                         │
│   ┌───────────────────────────────────────────────────────────────────────────┐   │
│   │                  API REST FASTAPI (http://localhost:8000)                 │   │
│   │         /simulation/*  |  /supervision/*  |  /securite/*  |  /inventory/* │   │
│   └─────────────────────────────────────┬─────────────────────────────────────┘   │
│                                         │ Données en temps réel                   │
│                                         ▼                                         │
│   ┌───────────────────────────────────────────────────────────────────────────┐   │
│   │                  PAGES STREAMLIT DYNAMIQUES (AUTO-REFRESH)                │   │
│   │  1_Dashboard  │ 2_Sécurité  │ 3_Supervision │ 4_NetDevOps │ 5_Parc │ 7_IA │   │
│   └───────────────────────────────────────────────────────────────────────────┘   │
└───────────────────────────────────────────────────────────────────────────────────┘
```

### 3.1. Objectifs & Valeur Ajoutée pour l'Épreuve BTS
- **Zéro donnée statique :** Chaque carte KPI, graphique temporel, badge de sévérité ou table d'incidents doit refléter l'état vivant de l'API.
- **Réactivité visuelle en direct :** Dès qu'un scénario de simulation est déclenché par le candidat, les écrans de supervision et de sécurité doivent s'actualiser sous les yeux du jury en moins de 2 secondes.
- **Pilotage de soutenance sans friction :** Intégration d'un composant de contrôle permanent (Sidebar ou onglet dédié) pour dérouler les 6 actes avec une fluidité maximale.

---

### 3.2. Détail Page par Page du Raccordement API

| Page Streamlit | Endpoints API consommés | Éléments visuels dynamisés | Comportement attendu |
| :--- | :--- | :--- | :--- |
| **`1_Dashboard.py`** | `GET /api/v1/inventory/equipements`<br>`GET /api/v1/admin/alertes`<br>`GET /api/v1/supervision/metrics` | • Cartes KPI (Santé globale, Alertes actives, Équipements surveillés)<br>• Graphique multi-courbes de télémétrie<br>• Flux des dernières alertes critiques | Mise à jour automatique des jauges et passage des alertes au rouge lors d'une simulation. |
| **`2_Sécurité.py`** | `GET /api/v1/securite/events`<br>`GET /api/v1/admin/alertes` | • Tableau des intrusions et attaques détectées<br>• Graphique de distribution des scores d'anomalie (*Isolation Forest*)<br>• Badge d'état de l'hôte ciblé (`SRV-AUTH-01`) | Dès le déclenchement de l'Acte 3, apparition instantanée de l'IP `198.51.100.45` avec score `-0.85` et sévérité `critique`. |
| **`3_Supervision.py`** | `GET /api/v1/supervision/metrics`<br>`GET /api/v1/supervision/predictions` | • Courbes d'évolution CPU / RAM / Disque par équipement<br>• Jauge prédictive *Time-To-Failure* (TTF)<br>• Alertes de dépassement de seuil critique | Lors du stress disque (Acte 2), la courbe de `SRV-APP-01` grimpe à 88% et la jauge TTF bascule à `< 3h`. |
| **`4_NetDevOps.py`** | `GET /api/v1/netdevops/audits`<br>`GET /api/v1/netdevops/backups/{id}` | • Liste des non-conformités *CIS Benchmark*<br>• Visualiseur de diff de configuration Cisco IOS<br>• Propositions de remédiation assistées | Visualisation immédiate des 3 failles de `SW-CORE-01` (`CIS-1.1`, `CIS-2.2`, `CIS-3.1`) avec correctifs proposés. |
| **`5_Parc_Informatique.py`** | `GET /api/v1/inventory/equipements`<br>`GET /api/v1/inventory/equipements/{id}` | • Grille des 5 équipements du parc<br>• Barres de progression des `health_score`<br>• Fiches détaillées (IP, MAC, OS, Uptime) | Observation en direct de la chute et de la restauration des scores de santé de chaque équipement. |
| **`6_Reporting_&_Admin.py`** | `GET /api/v1/admin/journal-audit`<br>`POST /api/v1/admin/generate-pdf-report` | • Journal d'audit traçable des actions<br>• Bouton de téléchargement du rapport PDF officiel | Téléchargement du rapport de soutenance consolidé avec les événements récents. |
| **`7_Assistant_IA.py`** | `POST /api/v1/assistant/query` | • Interface de chat interactive alimentée par LLM / RAG | Réponse en langage naturel sur l'état du réseau et les causes racines des incidents. |

---

### 3.3. Composant Démo « 1-Clic » dans la Barre Latérale (`components.py`)
Pour une ergonomie optimale lors de la présentation orale :
1. **Intégration dans `st.sidebar` :** Un bloc permanent intitulé `🎯 Démonstration BTS (1-Clic)` accessible depuis n'importe quelle page.
2. **4 Actions immédiates :**
   - 🔴 **`[Injecter Brute-force SSH]`** $\rightarrow$ Appelle `POST /api/v1/simulation/inject-bruteforce` et affiche un toast `🚨 Attaque simulée sur 198.51.100.45 !`.
   - 🟡 **`[Simuler Saturation Disque]`** $\rightarrow$ Appelle `POST /api/v1/simulation/stress-disk` et affiche un toast `⚠️ Stress disque déclenché sur SRV-APP-01 !`.
   - 🔵 **`[Injecter Faille CIS Cisco]`** $\rightarrow$ Appelle `POST /api/v1/simulation/cis-flaw` et affiche un toast `🛡️ 3 failles CIS détectées sur SW-CORE-01 !`.
   - 🟢 **`[Réinitialiser Démo (Reset)]`** $\rightarrow$ Appelle `POST /api/v1/simulation/reset` et affiche un toast `✅ Démo réinitialisée à l'état nominal !`.

---

### 3.4. Mécanisme de Rafraîchissement & Gestion du Cache
- **Auto-Refresh discret :** Fragment natif `@st.fragment(run_every=5)` appelant `st.rerun()` (toutes les 5 secondes), avec bouton pause pour figer l'écran pendant les explications au jury. (Ancien `st_autorefresh` retiré : dépendance abandonnée — voir `Progress_Sentinelle.md` § décision D1.)
- **Gestion des erreurs & Mode Hors-ligne :** En cas d'indisponibilité momentanée de l'API, le front-end capture l'exception proprement et affiche un avertissement clair au lieu de lever un écran de crash rouge.

---

## 4. Tableau Récapitulatif d'Avancement Global

| Composant / Phase | Contenu & Rôle | Statut |
| :--- | :--- | :---: |
| **Socle Back-end** | FastAPI, BDD SQLAlchemy, JWT + MFA TOTP, 6 Services métiers | ✅ **TERMINÉ** |
| **Phase 1 : Moteur Autonome** | `scheduler.py` (télémétrie 10s, TTF 30s, santé 60s) + `lifespan` | ✅ **TERMINÉ** |
| **Phase 2 : Simulation Démo** | `simulation.py` (4 endpoints) + `router.py` + tests unitaires (PASS) | ✅ **TERMINÉ** |
| **Phase 3 : Dynamisation Front-end** | Raccordement Streamlit (7 pages) + Panneau Démo 1-Clic + Auto-refresh natif | ✅ **TERMINÉ** |
| **Phase 4 : Hardening & Tests** | Couverture de tests accrue + répétition générale soutenance | 📅 **À VENIR** |

---

## 5. Note de statut final — remise en état & recette (08/10/2026)

Le projet a fait l'objet d'une remise en état complète (cf. `Progress_Sentinelle.md`) :
lancement **natif** (scripts `scripts/*.ps1` + `demarrer_*.bat`, sans Docker), **Streamlit
modernisé en 1.65.0** (dépendance abandonnée `streamlit-autorefresh` retirée, remplacée par
un fragment natif ; `use_container_width` et `datetime.utcnow()` dépréciés remplacés).

Recette globale validée le 08/10/2026 (aucun échec) :

| Contrôle | Script | Résultat |
| :--- | :--- | :---: |
| Tests unitaires back-end | `pytest -q` | ✅ 39 passed |
| Auth / MFA / rôles / hors-ligne | `frontend/verif_etape3_front.py` | ✅ 16/16 |
| Supervision prédictive (TTF) | `frontend/verif_etape5_supervision.py` | ✅ 13/13 |
| Hors-ligne sur les 7 pages | `frontend/verif_hors_ligne_pages.py` | ✅ 14/14 |
| 6 actes de démo (dont PDF) | `recette_6actes.ps1` | ✅ 6/6 |

Base de données sauvegardée dans `backup/`. Préflight `scripts/check_env.ps1` → exit 0.
