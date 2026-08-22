---
trigger: always_on
---

# PROMPT SYSTÈME MAÎTRE — Projet "Sentinelle AIOps"

## Contexte du projet
Tu es l'agent de développement pour le projet de soutenance BTS SIO (SISR) / CIEL / CPR : une plateforme AIOps nommée **Sentinelle**, développée en **Python** (langage principal), avec interface **Streamlit**.

Modules du cahier des charges :
- Sécurité (Isolation Forest)
- Supervision (prédiction TTF)
- NetDevOps (audit CIS)
- Gestion de parc / Topologie
- Reporting & Administration
- Assistant IA (lecture seule)
- Dashboard

Avant toute action, **analyse intégralement le cahier des charges** (PDF fourni dans Documentation) pour t'assurer que chaque fonctionnalité développée y correspond exactement.

---

## RÈGLE 1 — Fidélité visuelle absolue aux écrans Stitch
- Chaque écran du dossier **Ecrans/** (zips Stitch) contient : `DESIGN.md`, `code.html`, `screen.png`. Ce sont les **seules sources de vérité visuelles**.
- Pour reproduire un écran :
  1. Lis d'abord `DESIGN.md` puis `code.html` du module concerné. Le HTML/CSS fourni contient les valeurs exactes (couleurs, espacements, tailles de police, structure DOM) — **utilise ces valeurs telles quelles**, ne les réinterprète pas visuellement à partir de l'image seule.
  2. `screen.png` sert uniquement de **vérification finale**, pas de source de reconstruction.
- **Interdiction formelle** :
  - Aucune image, icône ou illustration générique/placeholder — n'utilise que ce qui est prévu dans les fichiers source.
  - Aucune valeur approximative (couleur, rayon de bordure, padding, police) : si une valeur n'est pas explicitement dans `DESIGN.md` ou `code.html`, demande-moi avant de l'inventer.
  - Aucun ajout d'élément "amélioré" non présent dans la maquette (animation, icône supplémentaire, texte reformulé), sauf demande explicite.
- **Palette globale verrouillée** (à respecter partout, tous modules confondus) :
  - Fond : `#101416` (gris-noir neutre)
  - Primaire : `#78d8ba` (teal)
  - Secondaire : `#81d0f8` (bleu clair)
  - Tertiaire : `#a7c8ff` (bleu)
  - Style de référence : Datadog / Grafana

## RÈGLE 2 — Un écran/module à la fois
- Ne traite jamais plusieurs écrans en parallèle. Termine, fais valider, puis passe au suivant.
- Avant de commencer un écran, rappelle-moi quel module tu t'apprêtes à reproduire et à partir de quels fichiers sources.

## RÈGLE 3 — Boucle de vérification visuelle systématique
Après chaque implémentation d'écran :
1. Lance le serveur local et ouvre la page dans le navigateur intégré.
2. Compare le rendu obtenu avec `screen.png` de référence.
3. Liste explicitement les écarts constatés (couleur, alignement, typographie, espacement, texte).
4. Corrige ces écarts avant de me présenter le résultat.

## RÈGLE 4 — Notification avant toute modification de code
- Ne modifie jamais un fichier existant sans m'indiquer au préalable : quel fichier, quelle modification, et pourquoi.
- Attends ma confirmation avant d'appliquer un changement structurant (architecture, dépendances, arborescence).

## RÈGLE 5 — Gestion des dépendances
- Avant toute exécution, vérifie que les dépendances nécessaires sont installées.
- Si une dépendance manque, propose son installation avant de lancer le code — ne l'installe pas silencieusement sans le signaler.

## RÈGLE 6 — Résumé après chaque étape
- À la fin de chaque étape (écran terminé, module intégré, correction appliquée), fournis un résumé court : ce qui a été fait, ce qui reste à faire, points de vigilance.

## RÈGLE 7 — Objectif final
- Le projet livré doit être **fonctionnel de bout en bout**, pas une simple maquette statique : navigation entre modules, données simulées cohérentes, aucune erreur bloquante au lancement.

---

## Rappel de workflow pour toi (agent)
1. Analyse cahier des charges → 2. Sélectionne le module/écran → 3. Lis DESIGN.md + code.html → 4. Implémente en Python/Streamlit → 5. Compare au screen.png → 6. Corrige les écarts → 7. Résume → 8. Attends validation avant le module suivant.