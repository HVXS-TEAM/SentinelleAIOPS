"""Script to generate a high-fidelity PDF of Résumé_Sentinelle.md using Microsoft Edge headless.
Produces both 'Résumé_Sentinelle.pdf' and 'Resume_sentinelle.pdf' at workspace root.
"""
import os
import subprocess
import sys
import tempfile
from pathlib import Path

WORKSPACE = Path(__file__).resolve().parent.parent
MD_PATH = WORKSPACE / "Résumé_Sentinelle.md"
HTML_PATH = WORKSPACE / "scripts" / "temp_resume.html"
PDF_OUT_1 = WORKSPACE / "Résumé_Sentinelle.pdf"
PDF_OUT_2 = WORKSPACE / "Resume_sentinelle.pdf"
DOCS_PDF_1 = WORKSPACE / "docs" / "Résumé_Sentinelle.pdf"
DOCS_PDF_2 = WORKSPACE / "docs" / "Resume_sentinelle.pdf"

EDGE_PATH = r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"

HTML_TEMPLATE = """<!DOCTYPE html>
<html lang="fr">
<head>
    <meta charset="UTF-8">
    <title>Sentinelle AIOps — Résumé du projet</title>
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&family=JetBrains+Mono:wght@400;500&display=swap');

        @page {
            size: A4 portrait;
            margin: 18mm 18mm 18mm 18mm;
        }

        *, *::before, *::after {
            box-sizing: border-box;
        }

        body {
            font-family: 'Inter', -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
            color: #1a202c;
            background-color: #ffffff;
            font-size: 9.6pt;
            line-height: 1.55;
            margin: 0;
            padding: 0;
            -webkit-print-color-adjust: exact;
            print-color-adjust: exact;
        }

        .page-break {
            page-break-after: always;
            break-after: page;
        }

        .no-break {
            page-break-inside: avoid;
            break-inside: avoid;
        }

        /* Running Header and Footer simulation */
        .page-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            font-size: 8pt;
            color: #718096;
            border-bottom: 1px solid #e2e8f0;
            padding-bottom: 4px;
            margin-bottom: 18px;
        }

        .page-footer {
            display: flex;
            justify-content: space-between;
            align-items: center;
            font-size: 8pt;
            color: #718096;
            border-top: 1px solid #e2e8f0;
            padding-top: 4px;
            margin-top: 24px;
        }

        /* Cover page */
        .cover-container {
            display: flex;
            flex-direction: column;
            justify-content: center;
            min-height: 800px;
            text-align: center;
            padding: 40px 20px;
        }

        .cover-title {
            font-size: 28pt;
            font-weight: 800;
            letter-spacing: -0.5px;
            color: #0f172a;
            margin: 0 0 8px 0;
            text-transform: uppercase;
        }

        .cover-subtitle {
            font-size: 14pt;
            font-weight: 500;
            color: #475569;
            margin: 0 0 24px 0;
        }

        .cover-desc {
            font-size: 11pt;
            color: #334155;
            max-width: 580px;
            margin: 0 auto 40px auto;
            line-height: 1.6;
        }

        .meta-table {
            width: 100%;
            max-width: 650px;
            margin: 0 auto 50px auto;
            border-collapse: collapse;
            text-align: left;
            border: 1px solid #cbd5e1;
            border-radius: 6px;
            overflow: hidden;
            font-size: 9pt;
        }

        .meta-table td {
            padding: 12px 16px;
            border-bottom: 1px solid #e2e8f0;
            vertical-align: middle;
        }

        .meta-table tr:last-child td {
            border-bottom: none;
        }

        .meta-table .label {
            width: 25%;
            font-weight: 600;
            background-color: #f1f5f9;
            color: #1e293b;
        }

        .meta-table .value {
            color: #334155;
            background-color: #ffffff;
        }

        .cover-note {
            font-size: 8pt;
            color: #94a3b8;
            font-style: italic;
            margin-top: 60px;
        }

        /* Headings */
        h1, h2, h3, h4 {
            color: #0f172a;
            font-weight: 700;
            page-break-after: avoid;
            break-after: avoid;
        }

        h2 {
            font-size: 13.5pt;
            border-bottom: 1.5px solid #cbd5e1;
            padding-bottom: 5px;
            margin-top: 20px;
            margin-bottom: 12px;
        }

        h3 {
            font-size: 11pt;
            margin-top: 14px;
            margin-bottom: 6px;
            color: #1e293b;
            display: flex;
            align-items: center;
            gap: 6px;
        }

        h4 {
            font-size: 10pt;
            margin-top: 12px;
            margin-bottom: 4px;
            color: #334155;
        }

        p {
            margin: 0 0 8px 0;
            color: #334155;
        }

        ul, ol {
            margin: 4px 0 10px 0;
            padding-left: 20px;
            color: #334155;
        }

        li {
            margin-bottom: 4px;
        }

        li strong, p strong {
            color: #0f172a;
        }

        hr {
            border: none;
            border-top: 1px solid #e2e8f0;
            margin: 18px 0;
        }

        /* Tables */
        table.content-table {
            width: 100%;
            border-collapse: collapse;
            margin: 12px 0 16px 0;
            font-size: 8.8pt;
            border: 1px solid #cbd5e1;
            page-break-inside: avoid;
            break-inside: avoid;
        }

        table.content-table th, table.content-table td {
            padding: 8px 10px;
            border: 1px solid #e2e8f0;
            text-align: left;
            vertical-align: top;
        }

        table.content-table th {
            background-color: #f1f5f9;
            color: #0f172a;
            font-weight: 600;
            font-size: 8.8pt;
        }

        table.content-table tr:nth-child(even) td {
            background-color: #f8fafc;
        }

        /* Quotes & Callouts */
        blockquote {
            margin: 12px 0;
            padding: 10px 16px;
            background-color: #f8fafc;
            border-left: 3px solid #78d8ba;
            color: #334155;
            font-style: italic;
            font-size: 9.2pt;
        }

        /* Code block */
        pre {
            background-color: #0f172a;
            color: #f8fafc;
            padding: 10px 14px;
            border-radius: 4px;
            font-family: 'JetBrains Mono', monospace;
            font-size: 8.5pt;
            margin: 8px 0 12px 0;
            overflow-x: auto;
        }

        code {
            font-family: 'JetBrains Mono', monospace;
            background-color: #f1f5f9;
            color: #0f172a;
            padding: 1px 4px;
            border-radius: 3px;
            font-size: 8.8pt;
        }

        pre code {
            background-color: transparent;
            color: #78d8ba;
            padding: 0;
        }

        /* Highlight boxes */
        .limit-box {
            background-color: #f8fafc;
            border: 1px solid #e2e8f0;
            border-left: 3px solid #3b82f6;
            border-radius: 4px;
            padding: 10px 14px;
            margin-bottom: 12px;
        }

        .limit-box-title {
            font-weight: 700;
            color: #1e3a8a;
            margin-bottom: 4px;
            font-size: 9.5pt;
        }
    </style>
</head>
<body>

    <!-- PAGE 1 : COUVERTURE & MÉTA -->
    <div class="cover-container">
        <div class="page-header" style="border:none; margin-bottom: 40px;">
            <span>Sentinelle AIOps — Résumé du projet</span>
            <span>Page 1</span>
        </div>

        <div style="flex-grow: 1; display:flex; flex-direction:column; justify-content:center;">
            <h1 class="cover-title">SENTINELLE AIOps</h1>
            <div class="cover-subtitle">Résumé du projet</div>
            <div class="cover-desc">
                Plateforme intelligente de supervision, prédiction et sécurisation du parc informatique
            </div>

            <table class="meta-table">
                <tr>
                    <td class="label">Contexte</td>
                    <td class="value">Projet de soutenance BTS SIO — option SISR / CIEL / CPR — Épreuve E6</td>
                </tr>
                <tr>
                    <td class="label">Technologies clés</td>
                    <td class="value">Python • FastAPI • Streamlit • PostgreSQL • scikit-learn • Netmiko • Ollama • Docker Compose</td>
                </tr>
                <tr>
                    <td class="label">Positionnement</td>
                    <td class="value">Centre de commandement IT unifié, souverain et orienté prévention</td>
                </tr>
            </table>

            <div class="cover-note">
                Document de synthèse — version structurée à partir du document source fourni
            </div>
        </div>

        <div class="page-footer">
            <span>Sentinelle AIOps — Résumé du projet</span>
            <span>Page 1</span>
        </div>
    </div>

    <div class="page-break"></div>

    <!-- PAGE 2 : CE QUE FAIT CONCRÈTEMENT SENTINELLE (PART 1) -->
    <div class="page-header">
        <span>Sentinelle AIOps — Résumé du projet</span>
        <span>Page 2</span>
    </div>

    <blockquote>
        <strong>Contexte :</strong> Projet de soutenance BTS SIO (option SISR) / CIEL / CPR — Épreuve E6 (Projet Technique).<br>
        Développé intégralement en Python, avec une interface Streamlit et une API REST FastAPI.
    </blockquote>

    <h2>1. Ce que fait concrètement Sentinelle</h2>
    <p>
        <strong>Sentinelle AIOps</strong> est une plateforme web centralisée qui permet à un administrateur
        système/réseau ou à un technicien de <strong>surveiller, prédire et sécuriser</strong> l'ensemble de son
        parc informatique depuis une seule interface — sans avoir à jongler entre cinq outils distincts.
    </p>
    <p>Elle repose sur <strong>7 modules opérationnels</strong> :</p>

    <div class="no-break">
        <h3>🔐 Module Sécurité — Détection d'anomalies</h3>
        <ul>
            <li>Analyse en continu les fichiers journaux systèmes (<code>Syslog</code>, <code>Auth.log</code>).</li>
            <li>Détecte automatiquement les comportements suspects (tentatives brute-force SSH, scans de ports, connexions anormales) grâce à un modèle d'<strong>apprentissage non supervisé Isolation Forest</strong> (scikit-learn).</li>
            <li>Attribue un <strong>score d'anomalie (0–100)</strong> à chaque événement et génère des alertes horodatées par niveau de sévérité (Critique / Élevé / Moyen / Faible).</li>
            <li><strong>Sans règle à écrire à la main</strong> : le modèle apprend lui-même ce qui est "normal" dans les logs, sans qu'on lui montre d'exemples d'attaques au préalable.</li>
        </ul>
    </div>

    <div class="no-break">
        <h3>📈 Module Supervision — Prédiction de panne</h3>
        <ul>
            <li>Collecte les métriques serveur (CPU, RAM, Disque, I/O réseau) en temps réel.</li>
            <li>Calcule un <strong>Time-To-Failure (TTF)</strong> : durée estimée avant saturation de chaque ressource, via <strong>régression linéaire</strong> sur la tendance de consommation.</li>
            <li>Affiche une zone de prédiction visuelle sur les graphiques (ligne pointillée projetée).</li>
            <li>Liste les équipements par urgence — le serveur qui va tomber dans 2 jours apparaît en premier, pas celui qui est à 40% de charge.</li>
        </ul>
    </div>

    <div class="no-break">
        <h3>🌐 Module NetDevOps — Audit réseau automatisé</h3>
        <ul>
            <li>Se connecte aux équipements Cisco (Switches, Routeurs) via <strong>Netmiko (SSH)</strong> et récupère leurs configurations courantes.</li>
            <li>Audite automatiquement ces configurations contre le <strong>référentiel CIS Benchmark</strong> (standard de sécurité réseau internationalement reconnu).</li>
            <li>Pour chaque non-conformité détectée (SNMP v1 actif, mot de passe en clair, Telnet ouvert...), un <strong>LLM local Ollama</strong> génère le script de correction Cisco IOS correspondant — présenté en diff lisible (avant/après).</li>
            <li><strong>Validation humaine obligatoire</strong> avant toute application : l'admin approuve ou rejette chaque correctif. Aucune modification automatique sans accord.</li>
        </ul>
    </div>

    <div class="page-footer">
        <span>Sentinelle AIOps — Résumé du projet</span>
        <span>Page 2</span>
    </div>

    <div class="page-break"></div>

    <!-- PAGE 3 : MODULES SUITE & PROBLEME QU'IL RESOUT -->
    <div class="page-header">
        <span>Sentinelle AIOps — Résumé du projet</span>
        <span>Page 3</span>
    </div>

    <div class="no-break">
        <h3>🖥️ Module Parc Informatique — Inventaire & Topologie</h3>
        <ul>
            <li>Découverte automatique des équipements du réseau par <strong>SNMP</strong>.</li>
            <li>Fiche complète par équipement : IP, MAC, OS/firmware, uptime, historique de métriques, alertes associées, audits réseau passés.</li>
            <li>Calcule un <strong>Score de Santé (0–100)</strong> synthétique par équipement, agrégeant disponibilité, charge CPU/RAM/disque et conformité.</li>
            <li>Vue <strong>topologie réseau interactive</strong> : carte graphique des équipements et de leurs interconnexions, colorée par état de santé.</li>
        </ul>
    </div>

    <div class="no-break">
        <h3>📊 Module Dashboard — Centre de commandement</h3>
        <ul>
            <li>Vue d'ensemble en temps réel : nombre d'équipements supervisés, alertes actives, score de santé moyen du parc, incidents prédits sur 7 jours, score de conformité réseau.</li>
            <li>Graphique de tendance CPU/RAM/Disque sur 7 jours avec projection.</li>
            <li>Grille d'état des équipements (puce verte/orange/rouge) avec mini-graphique par ligne.</li>
            <li>Flux d'alertes récentes en direct avec badges de sévérité et origine (Sécurité / Supervision / NetDevOps).</li>
        </ul>
    </div>

    <div class="no-break">
        <h3>📋 Module Reporting & Administration</h3>
        <ul>
            <li>Génération automatique de <strong>rapports PDF</strong> : audit de sécurité, supervision, conformité réseau — planifiables et téléchargeables depuis l'interface.</li>
            <li><strong>Gestion des utilisateurs</strong> avec 3 niveaux de rôle (Administrateur / Technicien / Visiteur) et authentification <strong>MFA TOTP</strong>.</li>
            <li><strong>Audit Trail complet</strong> : chaque action (connexion, modification, approbation d'un correctif réseau) est tracée avec horodatage et auteur.</li>
            <li>Notifications multicanales configurables : <strong>Email, Telegram, Discord</strong> — avec règles de routage par niveau de sévérité.</li>
        </ul>
    </div>

    <div class="no-break">
        <h3>🤖 Module Assistant IA Conversationnel</h3>
        <ul>
            <li>Chatbot en langage naturel, alimenté par <strong>Ollama (LLM local, sans cloud)</strong>.</li>
            <li>Permet de poser des questions en français sur les données du système : <em>"Quels serveurs risquent une saturation disque cette semaine ?"</em>, <em>"Montre-moi les alertes critiques de la dernière heure."</em></li>
            <li>Contraint en <strong>lecture seule stricte</strong> : l'assistant interroge uniquement la base de données via des requêtes SQL paramétrées — il ne peut pas modifier, supprimer ou exécuter des commandes sur les équipements.</li>
            <li>Réponses enrichies : tableaux de données et mini-graphiques directement inline dans le chat.</li>
        </ul>
    </div>

    <div class="page-footer">
        <span>Sentinelle AIOps — Résumé du projet</span>
        <span>Page 3</span>
    </div>

    <div class="page-break"></div>

    <!-- PAGE 4 : LE PROBLÈME QU'IL RÉSOUT & CE QUE SENTINELLE APPORTE -->
    <div class="page-header">
        <span>Sentinelle AIOps — Résumé du projet</span>
        <span>Page 4</span>
    </div>

    <h2>2. Pourquoi ce projet existe — le problème qu'il résout</h2>
    <p><strong>Le contexte réel des PME et établissements</strong></p>
    <p>Dans la majorité des structures de taille intermédiaire (PME, établissements scolaires, collectivités), l'administration système et réseau est aujourd'hui <strong>réactive et fragmentée</strong> :</p>
    <ul>
        <li>Le technicien découvre la panne <strong>après</strong> qu'elle s'est produite (alerte utilisateur, site inaccessible, serveur hors ligne).</li>
        <li>Les logs de sécurité s'accumulent sans jamais être analysés faute de temps.</li>
        <li>L'audit de conformité réseau se fait manuellement tous les 6 mois — quand il se fait.</li>
        <li>L'inventaire du parc est tenu sur un fichier Excel qui n'est plus à jour.</li>
        <li>Cinq outils différents sont ouverts simultanément : Zabbix pour la supervision, Kibana pour les logs, un client SSH pour les switchs, un PDF pour le CIS Benchmark, et un tableur pour l'inventaire.</li>
    </ul>

    <p>
        <strong>Le résultat :</strong> des incidents évitables, une conformité dégradée, et un technicien qui passe plus de temps à chercher l'information qu'à agir.
    </p>

    <h3>Ce que Sentinelle apporte</h3>
    <p>Sentinelle résout ces problèmes en basculant d'une posture <strong>réactive</strong> à une posture <strong>proactive et centralisée</strong> :</p>

    <table class="content-table">
        <thead>
            <tr>
                <th style="width: 50%;">Avant Sentinelle</th>
                <th style="width: 50%;">Avec Sentinelle</th>
            </tr>
        </thead>
        <tbody>
            <tr>
                <td>Panne détectée par l'utilisateur</td>
                <td><strong>Saturation prédite J-4 à J-7 à l'avance</strong></td>
            </tr>
            <tr>
                <td>Logs jamais analysés</td>
                <td><strong>Anomalies détectées automatiquement 24h/24</strong></td>
            </tr>
            <tr>
                <td>Audit CIS tous les 6 mois, manuel</td>
                <td><strong>Audit continu, correctifs générés instantanément</strong></td>
            </tr>
            <tr>
                <td>Inventaire Excel périmé</td>
                <td><strong>Découverte SNMP automatique, score de santé en temps réel</strong></td>
            </tr>
            <tr>
                <td>5 outils différents</td>
                <td><strong>1 interface unifiée, 1 seule connexion</strong></td>
            </tr>
            <tr>
                <td>Rapports rédigés à la main</td>
                <td><strong>Rapports PDF générés en un clic</strong></td>
            </tr>
        </tbody>
    </table>

    <div class="page-footer">
        <span>Sentinelle AIOps — Résumé du projet</span>
        <span>Page 4</span>
    </div>

    <div class="page-break"></div>

    <!-- PAGE 5 : SOLUTIONS CONCURRENTES -->
    <div class="page-header">
        <span>Sentinelle AIOps — Résumé du projet</span>
        <span>Page 5</span>
    </div>

    <h2>3. Avantages différenciants par rapport aux solutions existantes</h2>
    <h3>Solutions concurrentes de référence</h3>

    <table class="content-table">
        <thead>
            <tr>
                <th style="width: 24%;">Solution</th>
                <th style="width: 33%;">Positionnement</th>
                <th style="width: 43%;">Limites pour ce cas d'usage</th>
            </tr>
        </thead>
        <tbody>
            <tr>
                <td><strong>Datadog</strong></td>
                <td>AIOps enterprise complet</td>
                <td>Coût prohibitif (SaaS, ~$15–$50/hôte/mois), cloud obligatoire, données envoyées hors du SI</td>
            </tr>
            <tr>
                <td><strong>Grafana + Prometheus</strong></td>
                <td>Supervision & dashboarding</td>
                <td>Aucune IA ni prédiction native, configuration très complexe, aucun audit réseau</td>
            </tr>
            <tr>
                <td><strong>Zabbix</strong></td>
                <td>Supervision réseau/serveur</td>
                <td>Réactif (seuils fixes), aucun ML, aucun audit CIS, aucun assistant IA</td>
            </tr>
            <tr>
                <td><strong>Elastic SIEM / Kibana</strong></td>
                <td>Analyse de logs sécurité</td>
                <td>Spécialisé logs uniquement, très lourd à opérer, aucun module supervision ni réseau</td>
            </tr>
            <tr>
                <td><strong>Cisco DNA Center</strong></td>
                <td>NetDevOps Cisco</td>
                <td>Licences très coûteuses, limité à l'écosystème Cisco, aucun module sécurité logs ni supervision</td>
            </tr>
            <tr>
                <td><strong>Splunk</strong></td>
                <td>SIEM + analytics</td>
                <td>Tarification à la volumétrie (très cher dès 1 Go/jour), cloud ou infrastructure dédiée</td>
            </tr>
            <tr>
                <td><strong>ManageEngine OpManager</strong></td>
                <td>Supervision unifiée</td>
                <td>Interface vieillissante, IA limitée, coûteux en licences, pas d'assistant conversationnel</td>
            </tr>
        </tbody>
    </table>

    <div class="page-footer">
        <span>Sentinelle AIOps — Résumé du projet</span>
        <span>Page 5</span>
    </div>

    <div class="page-break"></div>

    <!-- PAGE 6 : CE QUI REND SENTINELLE UNIQUE & DÉPLOIEMENT -->
    <div class="page-header">
        <span>Sentinelle AIOps — Résumé du projet</span>
        <span>Page 6</span>
    </div>

    <h3>Ce qui rend Sentinelle unique</h3>

    <h4>✅ Unification dans un seul outil</h4>
    <p>Sentinelle couvre en un seul déploiement ce que Zabbix + Elastic + un client SSH + un référentiel CIS papier font séparément. Un seul login, une seule interface, une seule source de données consolidée.</p>

    <h4>✅ IA embarquée locale — zéro dépendance cloud</h4>
    <ul>
        <li>Le modèle Isolation Forest tourne localement, sans envoi de logs à un tiers.</li>
        <li>L'assistant IA (Ollama) s'exécute entièrement sur le serveur de l'établissement.</li>
        <li><strong>Conformité RGPD et confidentialité</strong> : aucune donnée d'exploitation ne quitte le SI.</li>
    </ul>

    <h4>✅ Prédiction, pas seulement seuils</h4>
    <p>Les solutions traditionnelles (Zabbix, Nagios) déclenchent une alerte quand une valeur dépasse un seuil fixe. Sentinelle <strong>calcule une tendance</strong> et prédit <em>quand</em> la ressource atteindra le seuil — plusieurs jours à l'avance.</p>

    <h4>✅ Correctifs réseau explicables et validés</h4>
    <p>Contrairement à des solutions d'automatisation réseau qui appliquent des changements sans traçabilité, Sentinelle <strong>montre le diff avant/après</strong>, soumet chaque correctif à validation humaine, et journalise chaque décision (Audit Trail).</p>

    <h4>✅ Coût zéro de licence</h4>
    <p>Entièrement construit sur des briques open-source (Python, FastAPI, Streamlit, scikit-learn, Netmiko, Ollama, PostgreSQL). Le seul coût est celui du serveur qui héberge la solution — déployable même sur un matériel modeste via Docker Compose.</p>

    <h4>✅ Accessible à un technicien BTS, opérable sans expertise IA</h4>
    <p>L'interface est pensée pour un technicien N1/N2, pas pour un data scientist. Les modèles IA sont pré-entraînés et se réentraînent automatiquement. L'assistant en langage naturel permet d'interroger les données sans écrire une seule ligne de SQL.</p>

    <h4>✅ Déployable on-premise en 10 minutes</h4>
    <pre><code>docker-compose up -d   # Lance PostgreSQL + FastAPI + Streamlit</code></pre>
    <p>Pas de cloud, pas d'agent à installer sur chaque serveur supervisé pour la plupart des modules — la collecte SNMP et SSH se fait depuis la plateforme centrale.</p>

    <div class="page-footer">
        <span>Sentinelle AIOps — Résumé du projet</span>
        <span>Page 6</span>
    </div>

    <div class="page-break"></div>

    <!-- PAGE 7 : STACK TECHNIQUE & EN RÉSUMÉ -->
    <div class="page-header">
        <span>Sentinelle AIOps — Résumé du projet</span>
        <span>Page 7</span>
    </div>

    <h2>4. Stack technique résumée</h2>

    <table class="content-table">
        <thead>
            <tr>
                <th style="width: 25%;">Couche</th>
                <th style="width: 35%;">Technologie</th>
                <th style="width: 40%;">Rôle</th>
            </tr>
        </thead>
        <tbody>
            <tr>
                <td><strong>Langage principal</strong></td>
                <td>Python 3.11+</td>
                <td>Backend, ML, automatisation réseau, frontend</td>
            </tr>
            <tr>
                <td><strong>API REST</strong></td>
                <td>FastAPI</td>
                <td>Exposition des données aux modules frontend</td>
            </tr>
            <tr>
                <td><strong>Interface</strong></td>
                <td>Streamlit</td>
                <td>Dashboard web interactif sans JavaScript</td>
            </tr>
            <tr>
                <td><strong>Base de données</strong></td>
                <td>PostgreSQL (prod) / SQLite (démo)</td>
                <td>Stockage centralisé</td>
            </tr>
            <tr>
                <td><strong>ML / Prédiction</strong></td>
                <td>scikit-learn (Isolation Forest, Régression Linéaire)</td>
                <td>Détection d'anomalies, TTF</td>
            </tr>
            <tr>
                <td><strong>Automatisation réseau</strong></td>
                <td>Netmiko + pysnmp</td>
                <td>SSH Cisco, découverte SNMP</td>
            </tr>
            <tr>
                <td><strong>LLM local</strong></td>
                <td>Ollama (Mistral / LLaMA 3)</td>
                <td>Assistant IA, génération de correctifs IOS</td>
            </tr>
            <tr>
                <td><strong>Rapports</strong></td>
                <td>ReportLab / WeasyPrint</td>
                <td>Génération PDF automatique</td>
            </tr>
            <tr>
                <td><strong>Conteneurisation</strong></td>
                <td>Docker Compose</td>
                <td>Déploiement local reproductible</td>
            </tr>
            <tr>
                <td><strong>Auth / Sécurité</strong></td>
                <td>JWT + MFA TOTP (PyOTP)</td>
                <td>Authentification sécurisée</td>
            </tr>
        </tbody>
    </table>

    <hr>

    <h2>5. En résumé</h2>
    <p>
        <strong>Sentinelle AIOps</strong> répond à un besoin réel et documenté des structures informatiques
        de taille intermédiaire : disposer d'une plateforme de supervision intelligente, abordable
        et souveraine, sans les contraintes de coût, de complexité ou de dépendance cloud des
        solutions enterprise.
    </p>

    <blockquote>
        Il ne s'agit pas d'un simple tableau de bord de plus — c'est un <strong>centre de commandement
        IT</strong> qui prédit les pannes avant qu'elles arrivent, détecte les intrusions sans règles
        à écrire, audite les réseaux en continu, et répond aux questions en français.<br>
        Le tout, gratuitement, en 10 minutes de déploiement, sur votre propre infrastructure.
    </blockquote>

    <div class="page-footer">
        <span>Sentinelle AIOps — Résumé du projet</span>
        <span>Page 7</span>
    </div>

    <div class="page-break"></div>

    <!-- PAGE 8 : LIMITES DU PROJET (6.1 & 6.2) -->
    <div class="page-header">
        <span>Sentinelle AIOps — Résumé du projet</span>
        <span>Page 8</span>
    </div>

    <h2>6. Limites du projet</h2>
    <p>
        Afin de garantir une transparence technique et de valoriser la démarche d'ingénierie lors de la soutenance, il convient de distinguer les <strong>limites temporaires actuelles</strong> (liées au périmètre du prototype et de la démonstration BTS) des <strong>limites structurelles en phase finale</strong> (choix d'architecture et de positionnement assumés).
    </p>

    <h3>6.1. Limites actuelles (Phase prototype / Démonstration BTS)</h3>

    <div class="limit-box" style="margin-bottom: 8px; padding: 8px 12px;">
        <div class="limit-box-title">1. Données et environnement de démonstration</div>
        <p style="margin:0; font-size: 8.8pt;">
            Une partie des flux de télémétrie, des journaux d'authentification et des équipements Cisco s'appuie sur des générateurs et simulateurs de lab afin de garantir une démonstration fluide, reproductible et autonome en soutenance, sans dépendance vis-à-vis d'un parc physique complet. Base locale dimensionnée pour la démo.
        </p>
    </div>

    <div class="limit-box" style="margin-bottom: 8px; padding: 8px 12px;">
        <div class="limit-box-title">2. Périmètre constructeur NetDevOps</div>
        <p style="margin:0; font-size: 8.8pt;">
            L'audit CIS et la génération de correctifs sont actuellement ciblés sur les équipements <strong>Cisco IOS</strong> via SSH/Netmiko. Les autres constructeurs (Junos, FortiOS, HP/Aruba) ne sont pas encore interfaçés.
        </p>
    </div>

    <div class="limit-box" style="margin-bottom: 8px; padding: 8px 12px;">
        <div class="limit-box-title">3. Modélisation prédictive initiale</div>
        <p style="margin:0; font-size: 8.8pt;">
            L'estimation du <em>Time-To-Failure (TTF)</em> repose sur une régression linéaire sur tendance glissante (saturations continues). Elle ne modélise pas encore les saisonnalités complexes (pics de sauvegardes nocturnes). L'Isolation Forest traite les logs Syslog/Auth.log sans corrélation d'attaques multi-étapes complexes.
        </p>
    </div>

    <div class="limit-box" style="margin-bottom: 12px; padding: 8px 12px;">
        <div class="limit-box-title">4. Architecture d'interface (Streamlit)</div>
        <p style="margin:0; font-size: 8.8pt;">
            Streamlit offre une vélocité de développement et un rendu tableau de bord idéal pour les techniciens, mais son mécanisme d'exécution par interaction limite la charge à quelques utilisateurs simultanés (non conçu pour des centaines d'utilisateurs web concurrents sans refonte front-end découplée).
        </p>
    </div>

    <div class="page-footer">
        <span>Sentinelle AIOps — Résumé du projet</span>
        <span>Page 8</span>
    </div>

    <div class="page-break"></div>

    <!-- PAGE 9 : LIMITES EN PHASE FINALE -->
    <div class="page-header">
        <span>Sentinelle AIOps — Résumé du projet</span>
        <span>Page 9</span>
    </div>

    <h3>6.2. Limites en phase finale (Cible production & Choix de conception)</h3>

    <div class="limit-box" style="margin-bottom: 8px; padding: 8px 12px;">
        <div class="limit-box-title">1. Volumétrie et non-remplacement d'un SIEM d'entreprise (vs Splunk / Elastic SIEM)</div>
        <p style="margin:0; font-size: 8.8pt;">
            Sentinelle est conçue pour les PME et établissements intermédiaires. Elle n'a pas vocation à archiver à froid des téraoctets de logs d'audit légal sur plusieurs années ni à remplacer une équipe SOC de 50 analystes. Son objectif reste l'alerte proactive et l'exploitabilité immédiate pour l'équipe IT en place.
        </p>
    </div>

    <div class="limit-box" style="margin-bottom: 8px; padding: 8px 12px;">
        <div class="limit-box-title">2. Contraintes de l'IA 100% souveraine et locale (vs API Cloud)</div>
        <p style="margin:0; font-size: 8.8pt;">
            Le refus catégorique d'envoyer des données dans le cloud impose l'exécution de modèles locaux quantifiés (7B/8B). Très performants pour l'assistance SQL et la syntaxe Cisco IOS, ils nécessitent toutefois un serveur adapté (16-32 Go RAM, accélération GPU recommandée).
        </p>
    </div>

    <div class="limit-box" style="margin-bottom: 8px; padding: 8px 12px;">
        <div class="limit-box-title">3. Garde-fous opérationnels et absence d'« auto-remédiation » aveugle</div>
        <p style="margin:0; font-size: 8.8pt;">
            Par choix délibéré de sécurité opérationnelle, Sentinelle <strong>n'appliquera jamais de correctif réseau de façon 100% autonome</strong>. Le principe de <em>Human-in-the-Loop</em> (validation humaine obligatoire) est une limite fonctionnelle permanente et voulue pour éliminer tout risque d'isolement réseau.
        </p>
    </div>

    <div class="limit-box" style="margin-bottom: 12px; padding: 8px 12px;">
        <div class="limit-box-title">4. Protocoles réseau historiques</div>
        <p style="margin:0; font-size: 8.8pt;">
            La solution privilégie SNMP et SSH/CLI pour s'adapter à la réalité hétérogène des parcs PME existants. L'intégration de la télémétrie moderne en streaming (gNMI / RESTCONF / NETCONF) reste tributaire du renouvellement du matériel chez le client.
        </p>
    </div>

    <div style="margin-top: 18px; text-align: center; color: #64748b; font-size: 8pt;">
        <em>Fin du document de synthèse — Sentinelle AIOps — BTS SIO / CIEL / CPR</em>
    </div>

    <div class="page-footer">
        <span>Sentinelle AIOps — Résumé du projet</span>
        <span>Page 9</span>
    </div>

</body>
</html>
"""

def generate_pdf():
    print("Writing temporary HTML...")
    HTML_PATH.write_text(HTML_TEMPLATE, encoding="utf-8")

    tmp_dir = Path(tempfile.gettempdir()) / "edge_pdf_gen"
    tmp_dir.mkdir(parents=True, exist_ok=True)

    cmd = [
        EDGE_PATH,
        "--headless=new",
        f"--user-data-dir={tmp_dir}",
        "--disable-gpu",
        "--no-pdf-header-footer",
        f"--print-to-pdf={PDF_OUT_1}",
        str(HTML_PATH)
    ]

    print(f"Executing: {' '.join(cmd)}")
    result = subprocess.run(cmd, capture_output=True, text=True)

    if PDF_OUT_1.exists() and PDF_OUT_1.stat().st_size > 0:
        print(f"Success! Generated {PDF_OUT_1} ({PDF_OUT_1.stat().st_size} bytes)")
        
        # Copy to alternative filenames/locations for convenience
        import shutil
        shutil.copy2(PDF_OUT_1, PDF_OUT_2)
        print(f"Copied to {PDF_OUT_2}")
        
        DOCS_PDF_1.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(PDF_OUT_1, DOCS_PDF_1)
        shutil.copy2(PDF_OUT_1, DOCS_PDF_2)
        print(f"Copied to docs directory ({DOCS_PDF_1}, {DOCS_PDF_2})")
    else:
        print(f"Error: PDF was not generated. Returncode: {result.returncode}")
        print("Stderr:", result.stderr)

    if HTML_PATH.exists():
        HTML_PATH.unlink()

if __name__ == "__main__":
    generate_pdf()
