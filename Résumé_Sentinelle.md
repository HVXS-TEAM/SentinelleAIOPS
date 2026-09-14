# 🛡️ Sentinelle AIOps — Résumé du Projet

> **Contexte :** Projet de soutenance BTS SIO (option SISR) / CIEL / CPR — Épreuve E6 (Projet Technique).
> Développé intégralement en Python, avec une interface Streamlit et une API REST FastAPI.

---

## 1. Ce que fait concrètement Sentinelle

**Sentinelle AIOps** est une plateforme web centralisée qui permet à un administrateur
système/réseau ou à un technicien de **surveiller, prédire et sécuriser** l'ensemble de son
parc informatique depuis une seule interface — sans avoir à jongler entre cinq outils distincts.

Elle repose sur **7 modules opérationnels** :

### 🔐 Module Sécurité — Détection d'anomalies
- Analyse en continu les fichiers journaux systèmes (`Syslog`, `Auth.log`).
- Détecte automatiquement les comportements suspects (tentatives brute-force SSH,
  scans de ports, connexions anormales) grâce à un modèle d'**apprentissage non supervisé
  Isolation Forest** (scikit-learn).
- Attribue un **score d'anomalie (0–100)** à chaque événement et génère des alertes
  horodatées par niveau de sévérité (Critique / Élevé / Moyen / Faible).
- **Sans règle à écrire à la main** : le modèle apprend lui-même ce qui est "normal"
  dans les logs, sans qu'on lui montre d'exemples d'attaques au préalable.

### 📈 Module Supervision — Prédiction de panne
- Collecte les métriques serveur (CPU, RAM, Disque, I/O réseau) en temps réel.
- Calcule un **Time-To-Failure (TTF)** : durée estimée avant saturation de chaque
  ressource, via **régression linéaire** sur la tendance de consommation.
- Affiche une zone de prédiction visuelle sur les graphiques (ligne pointillée projetée).
- Liste les équipements par urgence — le serveur qui va tomber dans 2 jours apparaît
  en premier, pas celui qui est à 40% de charge.

### 🌐 Module NetDevOps — Audit réseau automatisé
- Se connecte aux équipements Cisco (Switches, Routeurs) via **Netmiko (SSH)** et
  récupère leurs configurations courantes.
- Audite automatiquement ces configurations contre le **référentiel CIS Benchmark**
  (standard de sécurité réseau internationalement reconnu).
- Pour chaque non-conformité détectée (SNMP v1 actif, mot de passe en clair, Telnet
  ouvert...), un **LLM local Ollama** génère le script de correction Cisco IOS
  correspondant — présenté en diff lisible (avant/après).
- **Validation humaine obligatoire** avant toute application : l'admin approuve ou
  rejette chaque correctif. Aucune modification automatique sans accord.

### 🖥️ Module Parc Informatique — Inventaire & Topologie
- Découverte automatique des équipements du réseau par **SNMP**.
- Fiche complète par équipement : IP, MAC, OS/firmware, uptime, historique de métriques,
  alertes associées, audits réseau passés.
- Calcule un **Score de Santé (0–100)** synthétique par équipement, agrégeant
  disponibilité, charge CPU/RAM/disque et conformité.
- Vue **topologie réseau interactive** : carte graphique des équipements et de leurs
  interconnexions, colorée par état de santé.

### 📊 Module Dashboard — Centre de commandement
- Vue d'ensemble en temps réel : nombre d'équipements supervisés, alertes actives,
  score de santé moyen du parc, incidents prédits sur 7 jours, score de conformité réseau.
- Graphique de tendance CPU/RAM/Disque sur 7 jours avec projection.
- Grille d'état des équipements (puce verte/orange/rouge) avec mini-graphique par ligne.
- Flux d'alertes récentes en direct avec badges de sévérité et origine (Sécurité /
  Supervision / NetDevOps).

### 📋 Module Reporting & Administration
- Génération automatique de **rapports PDF** : audit de sécurité, supervision, conformité
  réseau — planifiables et téléchargeables depuis l'interface.
- **Gestion des utilisateurs** avec 3 niveaux de rôle (Administrateur / Technicien /
  Visiteur) et authentification **MFA TOTP**.
- **Audit Trail complet** : chaque action (connexion, modification, approbation d'un
  correctif réseau) est tracée avec horodatage et auteur.
- Notifications multicanales configurables : **Email, Telegram, Discord** — avec règles
  de routage par niveau de sévérité.

### 🤖 Module Assistant IA Conversationnel
- Chatbot en langage naturel, alimenté par **Ollama (LLM local, sans cloud)**.
- Permet de poser des questions en français sur les données du système :
  *"Quels serveurs risquent une saturation disque cette semaine ?"*,
  *"Montre-moi les alertes critiques de la dernière heure."*
- Contraint en **lecture seule stricte** : l'assistant interroge uniquement la base de
  données via des requêtes SQL paramétrées — il ne peut pas modifier, supprimer ou
  exécuter des commandes sur les équipements.
- Réponses enrichies : tableaux de données et mini-graphiques directement inline dans
  le chat.

---

## 2. Pourquoi ce projet existe — le problème qu'il résout

### Le contexte réel des PME et établissements
Dans la majorité des structures de taille intermédiaire (PME, établissements scolaires,
collectivités), l'administration système et réseau est aujourd'hui **réactive et fragmentée** :

- Le technicien découvre la panne **après** qu'elle s'est produite (alerte utilisateur,
  site inaccessible, serveur hors ligne).
- Les logs de sécurité s'accumulent sans jamais être analysés faute de temps.
- L'audit de conformité réseau se fait manuellement tous les 6 mois — quand il se fait.
- L'inventaire du parc est tenu sur un fichier Excel qui n'est plus à jour.
- Cinq outils différents sont ouverts simultanément : Zabbix pour la supervision,
  Kibana pour les logs, un client SSH pour les switchs, un PDF pour le CIS Benchmark,
  et un tableur pour l'inventaire.

**Le résultat :** des incidents évitables, une conformité dégradée, et un technicien
qui passe plus de temps à chercher l'information qu'à agir.

### Ce que Sentinelle apporte
Sentinelle résout ces problèmes en basculant d'une posture **réactive** à une posture
**proactive et centralisée** :

| Avant Sentinelle | Avec Sentinelle |
|---|---|
| Panne détectée par l'utilisateur | Saturation prédite J-4 à J-7 à l'avance |
| Logs jamais analysés | Anomalies détectées automatiquement 24h/24 |
| Audit CIS tous les 6 mois, manuel | Audit continu, correctifs générés instantanément |
| Inventaire Excel périmé | Découverte SNMP automatique, score de santé en temps réel |
| 5 outils différents | 1 interface unifiée, 1 seule connexion |
| Rapports rédigés à la main | Rapports PDF générés en un clic |

---

## 3. Avantages différenciants par rapport aux solutions existantes

### Solutions concurrentes de référence

| Solution | Positionnement | Limites pour ce cas d'usage |
|---|---|---|
| **Datadog** | AIOps enterprise complet | Coût prohibitif (SaaS, ~$15–$50/hôte/mois), cloud obligatoire, données envoyées hors du SI |
| **Grafana + Prometheus** | Supervision & dashboarding | Aucune IA ni prédiction native, configuration très complexe, aucun audit réseau |
| **Zabbix** | Supervision réseau/serveur | Réactif (seuils fixes), aucun ML, aucun audit CIS, aucun assistant IA |
| **Elastic SIEM / Kibana** | Analyse de logs sécurité | Spécialisé logs uniquement, très lourd à opérer, aucun module supervision ni réseau |
| **Cisco DNA Center** | NetDevOps Cisco | Licences très coûteuses, limité à l'écosystème Cisco, aucun module sécurité logs ni supervision |
| **Splunk** | SIEM + analytics | Tarification à la volumétrie (très cher dès 1 Go/jour), cloud ou infrastructure dédiée |
| **ManageEngine OpManager** | Supervision unifiée | Interface vieillissante, IA limitée, coûteux en licences, pas d'assistant conversationnel |

### Ce qui rend Sentinelle unique

#### ✅ Unification dans un seul outil
Sentinelle couvre en un seul déploiement ce que Zabbix + Elastic + un client SSH + un
référentiel CIS papier font séparément. Un seul login, une seule interface, une seule
source de données consolidée.

#### ✅ IA embarquée locale — zéro dépendance cloud
- Le modèle Isolation Forest tourne localement, sans envoi de logs à un tiers.
- L'assistant IA (Ollama) s'exécute entièrement sur le serveur de l'établissement.
- **Conformité RGPD et confidentialité** : aucune donnée d'exploitation ne quitte le SI.

#### ✅ Prédiction, pas seulement seuils
Les solutions traditionnelles (Zabbix, Nagios) déclenchent une alerte quand une valeur
dépasse un seuil fixe. Sentinelle **calcule une tendance** et prédit *quand* la ressource
atteindra le seuil — plusieurs jours à l'avance.

#### ✅ Correctifs réseau explicables et validés
Contrairement à des solutions d'automatisation réseau qui appliquent des changements
sans traçabilité, Sentinelle **montre le diff avant/après**, soumet chaque correctif
à validation humaine, et journalise chaque décision (Audit Trail).

#### ✅ Coût zéro de licence
Entièrement construit sur des briques open-source (Python, FastAPI, Streamlit,
scikit-learn, Netmiko, Ollama, PostgreSQL). Le seul coût est celui du serveur qui
héberge la solution — déployable même sur un matériel modeste via Docker Compose.

#### ✅ Accessible à un technicien BTS, opérable sans expertise IA
L'interface est pensée pour un technicien N1/N2, pas pour un data scientist. Les
modèles IA sont pré-entraînés et se réentraînent automatiquement. L'assistant en
langage naturel permet d'interroger les données sans écrire une seule ligne de SQL.

#### ✅ Déployable on-premise en 10 minutes
```bash
docker-compose up -d   # Lance PostgreSQL + FastAPI + Streamlit
```
Pas de cloud, pas d'agent à installer sur chaque serveur supervisé pour la plupart
des modules — la collecte SNMP et SSH se fait depuis la plateforme centrale.

---

## 4. Stack technique résumée

| Couche | Technologie | Rôle |
|---|---|---|
| **Langage principal** | Python 3.11+ | Backend, ML, automatisation réseau, frontend |
| **API REST** | FastAPI | Exposition des données aux modules frontend |
| **Interface** | Streamlit | Dashboard web interactif sans JavaScript |
| **Base de données** | PostgreSQL (prod) / SQLite (démo) | Stockage centralisé |
| **ML / Prédiction** | scikit-learn (Isolation Forest, Régression Linéaire) | Détection d'anomalies, TTF |
| **Automatisation réseau** | Netmiko + pysnmp | SSH Cisco, découverte SNMP |
| **LLM local** | Ollama (Mistral / LLaMA 3) | Assistant IA, génération de correctifs IOS |
| **Rapports** | ReportLab / WeasyPrint | Génération PDF automatique |
| **Conteneurisation** | Docker Compose | Déploiement local reproductible |
| **Auth / Sécurité** | JWT + MFA TOTP (PyOTP) | Authentification sécurisée |

---

## 5. En résumé

**Sentinelle AIOps** répond à un besoin réel et documenté des structures informatiques
de taille intermédiaire : disposer d'une plateforme de supervision intelligente, abordable
et souveraine, sans les contraintes de coût, de complexité ou de dépendance cloud des
solutions enterprise.

> Il ne s'agit pas d'un simple tableau de bord de plus — c'est un **centre de commandement
> IT** qui prédit les pannes avant qu'elles arrivent, détecte les intrusions sans règles
> à écrire, audite les réseaux en continu, et répond aux questions en français.
> Le tout, gratuitement, en 10 minutes de déploiement, sur votre propre infrastructure.

---

## 6. Limites du projet

Afin de garantir une transparence technique et de valoriser la démarche d'ingénierie lors de la soutenance, il convient de distinguer les **limites temporaires actuelles** (liées au périmètre du prototype et de la démonstration BTS) des **limites structurelles en phase finale** (choix d'architecture et de positionnement assumés).

### 6.1. Limites actuelles (Phase prototype / Démonstration BTS)

1. **Données et environnement de démonstration :**
   - Une partie des flux de télémétrie, des journaux d'authentification et des équipements Cisco s'appuie sur des générateurs et simulateurs de lab afin de garantir une démonstration fluide, reproductible et autonome en soutenance, sans dépendance vis-à-vis d'un parc physique complet.
   - Base de données locale dimensionnée pour le scénario de démonstration plutôt que pour l'ingestion massive multi-années.

2. **Périmètre constructeur NetDevOps :**
   - L'audit CIS et la génération de correctifs sont actuellement ciblés sur les équipements Cisco IOS via SSH/Netmiko. Les autres constructeurs (Junos, FortiOS, HP/Aruba) ne sont pas encore interfaçés.

3. **Modélisation prédictive initiale :**
   - L'estimation du *Time-To-Failure (TTF)* repose sur une régression linéaire sur tendance glissante. Elle anticipe très bien les saturations régulières (disque qui se remplit, fuite mémoire progressive), mais ne modélise pas encore les saisonnalités complexes (pics d'activité hebdomadaires ou sauvegardes nocturnes).
   - L'apprentissage non supervisé (*Isolation Forest*) est entraîné sur des caractéristiques de logs ciblées (Syslog/Auth.log) sans corrélation d'attaques multi-étapes avancées (graphe MITRE ATT&CK complet).

4. **Architecture d'interface (Streamlit) :**
   - Streamlit offre une vélocité de développement et un rendu tableau de bord idéal pour les techniciens, mais son mécanisme d'exécution par interaction limite la charge à quelques utilisateurs simultanés (non conçu pour des centaines d'utilisateurs web concurrents sans refonte front-end découplée).

---

### 6.2. Limites en phase finale (Cible production & Choix de conception)

1. **Volumétrie et non-remplacement d'un SIEM d'entreprise (vs Splunk / Elastic SIEM) :**
   - Sentinelle est conçue pour les PME et établissements intermédiaires. Elle n'a pas vocation à archiver à froid des téraoctets de logs d'audit légal sur plusieurs années ni à remplacer une équipe SOC de 50 analystes. Son objectif reste l'alerte proactive et l'exploitabilité immédiate pour l'équipe IT en place.

2. **Contraintes de l'IA 100% souveraine et locale (vs API Cloud) :**
   - Le refus catégorique d'envoyer des données dans le cloud impose l'exécution de modèles de taille intermédiaire (Mistral 7B / Llama 3 8B quantifiés). Ces modèles sont très performants pour l'assistance SQL et la génération de commandes Cisco IOS, mais restent tributaires des ressources de calcul de l'hôte (16 à 32 Go de RAM requis, accélération GPU recommandée).

3. **Garde-fous opérationnels et absence d'« auto-remédiation » aveugle :**
   - Par choix délibéré de sécurité opérationnelle, Sentinelle **n'appliquera jamais de correctif réseau de façon 100% autonome**. Le principe de *Human-in-the-Loop* (validation humaine obligatoire avant application) est une limite fonctionnelle permanente et voulue pour éliminer tout risque de coupure de service réseau suite à une hallucination IA.

4. **Protocoles réseau historiques :**
   - La solution privilégie SNMP et SSH/CLI pour s'adapter à la réalité hétérogène des parcs PME existants. L'intégration d'architectures modernes basées sur la télémétrie en streaming (gNMI / RESTCONF / NETCONF) constitue une évolution future mais dépendante du renouvellement du matériel chez le client.

