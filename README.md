# StatJack — Simulateur Probabiliste de Blackjack

> **Projet d'Intégration (Épreuve Synthèse de Programme)**
> *420-SF4-HY — Projet d'intégration SIM — Hiver 2026 — Cégep de St-Hyacinthe*
> Présenté à Hugo Lapointe Di Giacomo

---

## Contexte

StatJack transforme le Blackjack en un **laboratoire d'apprentissage interactif** pour les probabilités. Le projet démontre qu'avec une application rigoureuse de la stratégie de base et du comptage de cartes, l'avantage mathématique peut basculer en faveur du joueur — tout en illustrant l'impact de la **variance** à court terme.

L'objectif n'est pas de créer un jeu de hasard, mais un **outil pédagogique** permettant d'analyser l'efficacité des stratégies de jeu face aux lois statistiques.

## Fonctionnalités principales

- **Moteur de jeu complet** — Hit, Stand, Double, Split, gestion du croupier (stand on 17), Blackjack naturel
- **Calculateur de probabilités dynamique** — Pourcentage de bust et d'amélioration en temps réel selon la composition du sabot
- **Stratégie de base et EV** — Recommandations basées sur l'Espérance Mathématique et simulations Monte Carlo
- **Comptage de cartes Hi-Lo** — Running Count et True Count mis à jour à chaque carte tirée
- **Mode Entraînement** — Intercepte les mauvaises décisions et explique l'erreur mathématique
- **Mode Tutoriel** — Guide pas-à-pas pour les joueurs sans expérience
- **Graphe de simulation** — Visualisation de la convergence des gains et de l'impact de la variance
- **Infobulles scientifiques** — Formules mathématiques expliquées directement dans l'interface
- **Ambiance sonore** — Effets audio et musique de fond pour l'immersion

## Technologies

| Technologie | Usage |
|---|---|
| Python 3.10+ | Langage principal |
| PySide6 | Interface graphique (signaux/slots) |
| Matplotlib | Graphiques de variance et progression |
| NumPy | Calculs vectoriels et simulations |
> [!NOTE]
> *Les recommandations HIT/STAND sont basées sur un calcul récursif d’espérance mathématique, tandis que les statistiques Monte Carlo servent principalement d’outil visuel et pédagogique.*

## Architecture

Le projet suit le patron **MVC** (Modèle-Vue-Contrôleur) :

```
src/
├── models/          # Logique métier (Jeu, Sabot, Main, Probabilités, Hi-Lo)
├── views/           # Interface PySide6 (VueJeu, Sidebar, Paramètres)
├── controllers/     # Contrôleurs et workers asynchrones
└── assets/          # Images des cartes, sons, musique
```

## Équipe et responsabilités

| Membre | Rôles principaux |
|---|---|
| **Adrien Moncade** | Interface utilisateur (UI/UX), coordination générale du projet |
| **Edouard Gagné** | Optimisation de performance, architecture système, précision arithmétique |
| **Félix Desharnais** | Moteur de calcul mathématique, documentation, intégration continue (Git) |
| **Luka Therrien** | Tests et validation, gestion des risques, debugging |

## Tâches principales par version

| Version | Date | Responsable(s) | Description |
|---|---|---|---|
| 1.1 | 2026-02-11 | Adrien | Structure initiale et définition de la vision |
| 1.2 | 2026-02-18 | Équipe complète | Vision de l'application et analyse préliminaire |
| 2.0 | 2026-02-25 | Edouard, Adrien, Luka | Backend OOP (Sabot, Cartes, Mains) |
| 2.1 | 2026-03-10 | Luka, Félix | Moteur mathématique (probabilités, Monte Carlo) |
| 2.2 | 2026-03-24 | Adrien, Edouard | Interface graphique PySide6 et connexion MVC |
| 2.3 | 2026-04-05 | Luka, Adrien | Panneau de statistiques dynamique (EV, True Count) |
| 2.4 | 2026-04-15 | Edouard, Félix | Mode Entraînement (interception et indices) |
| 3.0 | 2026-05-06 | Équipe complète | Correction de bugs critiques, infobulles, analyse révisée |

## Concepts scientifiques

- **Probabilités conditionnelles** — Recalcul dynamique après chaque carte tirée (processus sans remise)
- **Système Hi-Lo** — Comptage de cartes (+1, 0, -1) pour estimer l'avantage du joueur
- **Loi des grands nombres** — Convergence des gains réels vers l'espérance mathématique
- **Simulations Monte Carlo** — Estimation empirique des probabilités par milliers de mains simulées
> 
> *Les recommandations HIT/STAND sont basées sur un calcul récursif d’espérance mathématique, tandis que les statistiques Monte Carlo servent principalement d’outil visuel et pédagogique.*


## Lien scientifique

Le calcul de la stratégie de base repose sur l'Espérance Mathématique (EV) pour chaque action possible. L'objectif est de maximiser l'EV en choisissant l'action optimale selon la main du joueur et la carte visible du croupier.

## Documents

- [Analyse préliminaire](https://1drv.ms/w/c/cbccbcda01405813/IQD0b8YEEk-0QJC7kS6ey4HVATgH1v-i00KOF11j9KeUFrU?e=Rt8VQe)
- [Analyse révisée](https://1drv.ms/w/c/cbccbcda01405813/IQBhCfqGLlQGRYnnEZk-Ila5AV9sm9vCxHsxAm_NjsMMAJM?e=7bByPd)

---
*Développé dans le cadre du cours « Projet d'intégration SIM » au Cégep de St-Hyacinthe — Hiver 2026*
