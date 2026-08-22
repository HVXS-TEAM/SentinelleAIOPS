# 🛡️ Sentinelle AIOps — Plateforme Centralisée d'Administration Système & Réseau

**Diplôme préparé :** BTS SIO (option SISR) / CIEL / CPR — Épreuve E6 (Projet Technique)  
**Technologies :** Python 3.11+, FastAPI, Streamlit, PostgreSQL, scikit-learn, Netmiko, Ollama (LLM local), Docker Compose.

---

## 📌 Présentation du Projet

**Sentinelle AIOps** transforme l'administration système et réseau conventionnelle (réactive et manuelle) vers un pilotage unifié, prédictif, sécurisé et partiellement automatisé. 

### Les 6 Modules Métiers de la Plateforme :
1. **Module Sécurité :** Détection non supervisée d'anomalies (brute-force SSH, port scan) dans les journaux `Syslog`/`Auth.log` via le modèle **Isolation Forest**.
2. **Module Supervision :** Prédiction de la saturation des ressources serveur (CPU, RAM, Disque) et calcul du **Time-To-Failure (TTF)** par **Régression Linéaire**.
3. **Module NetDevOps :** Audit automatisé des configurations réseau Cisco selon le référentiel **CIS Benchmark** assisté par un **LLM local (Ollama)** avec scripts de correction IOS.
4. **Module Parc Informatique :** Découverte SNMP automatique des équipements et calcul d'un **Score de Santé** synthétique (0 à 100).
5. **Module Reporting & Administration :** Tableau de bord Streamlit (Design System Teal `#78D8BA`), génération automatique de rapports PDF, traçabilité *Audit Trail* et notifications multicanales.
6. **Module Assistant IA Conversationnel :** Chatbot adossé à Ollama local, contraint en **lecture seule stricte** (SQL paramétré / function calling).

---

## 🛠️ Installation & Démarrage Rapide

### 1. Cloner / Ouvrir le Répertoire du Projet
```bash
cd "e:/Projets Edwin/BTS Projects/Sentinelle AIOPS"
```

### 2. Installer les Dépendances Python
```bash
py -m pip install --pre -r requirements.txt
```

### 3. Initialiser la Base de Données (SQLite / PostgreSQL)
```bash
py scripts/init_db.py
```

### 4. Lancer le Backend API REST (FastAPI)
```bash
py -m uvicorn backend.main:app --host 0.0.0.0 --port 8000 --reload
```
> La documentation interactive OpenAPI est disponible sur `http://localhost:8000/docs`

### 5. Lancer l'Interface Frontend (Streamlit)
```bash
py -m streamlit run frontend/app.py
```
> L'interface web s'ouvre sur `http://localhost:8501`

---

## 🐳 Déploiement Conteneurisé avec Docker Compose

Pour déployer l'intégralité du lab (Base PostgreSQL, Backend FastAPI et Frontend Streamlit) :

```bash
docker-compose up -d
```

---

## 🧪 Lancer la Suite de Tests Unitaires

```bash
cd backend
py -m pytest tests
```

---

## 🔐 Identifiants de Démonstration

* **Administrateur :** `admin` / `AdminPass2026!` (MFA TOTP activé)
* **Technicien :** `tech` / `TechPass2026!`
* **Visiteur :** `visiteur` / `VisitorPass2026!`
