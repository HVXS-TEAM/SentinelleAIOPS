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
- **Auto-Refresh discret :** Utilisation de l'intervalle `st_autorefresh(interval=5000, key="datarefresh")` (toutes les 5 secondes) avec bouton pause pour figer l'écran pendant les explications au jury.
- **Gestion des erreurs & Mode Hors-ligne :** En cas d'indisponibilité momentanée de l'API, le front-end capture l'exception proprement et affiche un avertissement clair au lieu de lever un écran de crash rouge.

---

## 4. Tableau Récapitulatif d'Avancement Global

| Composant / Phase | Contenu & Rôle | Statut |
| :--- | :--- | :---: |
| **Socle Back-end** | FastAPI, BDD SQLAlchemy, JWT + MFA TOTP, 6 Services métiers | ✅ **TERMINÉ** |
| **Phase 1 : Moteur Autonome** | `scheduler.py` (télémétrie 10s, TTF 30s, santé 60s) + `lifespan` | ✅ **TERMINÉ** |
| **Phase 2 : Simulation Démo** | `simulation.py` (4 endpoints) + `router.py` + tests unitaires (PASS) | ✅ **TERMINÉ** |
| **Phase 3 : Dynamisation Front-end** | Raccordement Streamlit (7 pages) + Panneau Démo 1-Clic + Auto-refresh | ⏳ **EN COURS D'ENGAGEMENT** |
| **Phase 4 : Hardening & Tests** | Couverture de tests accrue + répétition générale soutenance | 📅 **À VENIR** |
