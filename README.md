# 🛡️ Sentinelle AIOps — Plateforme Centralisée d'Administration Système & Réseau

**Diplôme préparé :** BTS SIO (option SISR) / CIEL / CPR — Épreuve E6 (Projet Technique)  
**Technologies :** Python 3.11+ (testé 3.14), FastAPI, Streamlit 1.65, SQLite, scikit-learn (Isolation Forest), Netmiko, Ollama (LLM local).

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

## 🛠️ Installation & Démarrage Rapide (mode natif)

> **Prérequis :** Python 3.11+ (testé avec 3.14), aucun Docker nécessaire.
> Le venv `venv_env/` et les dépendances sont créés automatiquement au premier lancement.

### Démarrage en une commande

| Action | Double-clic (Explorateur) | Ligne de commande |
| :--- | :--- | :--- |
| **Backend + Frontend** | `demarrer_tout.bat` | `powershell -ExecutionPolicy Bypass -File scripts\start_all.ps1` |
| Backend seul (port 8000) | `demarrer_backend.bat` | `powershell -ExecutionPolicy Bypass -File scripts\start_backend.ps1` |
| Frontend seul (port 8501) | `demarrer_frontend.bat` | `powershell -ExecutionPolicy Bypass -File scripts\start_frontend.ps1` |
| Préflight environnement | — | `powershell -ExecutionPolicy Bypass -File scripts\check_env.ps1` |

- Documentation API interactive : **http://localhost:8000/docs**
- Interface web : **http://localhost:8501**
- Le scheduler démarre avec le backend (télémétrie 10 s, TTF 30 s, santé du parc 60 s).

### Commandes manuelles (équivalent)

```bash
# dépendances (si le venv n'existe pas encore)
py -m pip install --pre -r requirements.txt

# backend (depuis le dossier backend/)
cd backend
../venv_env/Scripts/python.exe -m uvicorn main:app --port 8000

# frontend
venv_env/Scripts/python.exe -m streamlit run frontend/app.py
```

### ⚠️ Base de données

- **Base réelle :** `backend/sentinelle_aiops.db` (SQLite, créée/autocomplétée au démarrage du backend).
- `py scripts/init_db.py` **écrase et recrée toute la base** (données de démo incluses) :
  à n'utiliser que pour une réinitialisation complète.
- Les `.env` : `backend/.env` porte la `SECRET_KEY` (générée, à conserver).

---


## 🧪 Lancer la Suite de Tests Unitaires

```bash
cd backend
../venv_env/Scripts/python.exe -m pytest tests
```

> 39 tests sont attendus (`39 passed`).

---

## 🐳 Option secondaire : Déploiement Conteneurisé (non maintenu)

Une configuration Docker Compose (PostgreSQL + Backend + Frontend) existe dans
`docker-compose.yml` mais **n'est plus validée** : le mode natif (§ Installation) est
le mode officiel. En cas de besoin :

```bash
docker-compose up -d
```

> ⚠️ Le `DATABASE_URL` de `docker-compose.yml` pointe vers un hôte PostgreSQL à vérifier
> avant usage, et la base de données réelle du projet est SQLite (`backend/sentinelle_aiops.db`).

---

## 📄 Scripts de vérification (recette)

Le backend doit tourner (port 8000) et, pour les tests front, le compte de démo est utilisé automatiquement.

```bash
# ── Backend (depuis backend/, backend en marche) ──
../venv_env/Scripts/python.exe verif_etape1.py   # TTF, alertes, score de santé
../venv_env/Scripts/python.exe verif_etape2.py   # maintenance / rétention des données
../venv_env/Scripts/python.exe verif_etape3.py   # module sécurité (Isolation Forest)
../venv_env/Scripts/python.exe verif_etape4.py   # génération du rapport PDF

# ── Frontend (depuis frontend/, backend en marche) ──
../venv_env/Scripts/python.exe verif_etape3_front.py      # MFA, rôles, session, hors-ligne
../venv_env/Scripts/python.exe verif_etape5_supervision.py # carte prédiction + TTF
../venv_env/Scripts/python.exe verif_hors_ligne_pages.py   # robustesse des 7 pages, API coupée
```

Recette de bout en bout rejouable (6 actes de démo + validation du PDF) :

```powershell
powershell -ExecutionPolicy Bypass -File recette_6actes.ps1
```

> Dernier passage de recette : tous les scripts au vert (voir §7 de `Progress_Sentinelle.md`).

---

## 🔐 Identifiants de Démonstration

* **Administrateur :** `admin` / `AdminPass2026!` (MFA TOTP activé)
* **Technicien :** `tech` / `TechPass2026!`
* **Visiteur :** `visiteur` / `VisitorPass2026!`
