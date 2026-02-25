from src.models.sabot import Sabot
from src.models.main_joueur import MainJoueur
import random
import copy


def _total_avec_carte(main_joueur, carte):
    total = 0
    nb_as = 0
    for c in main_joueur.cartes:
        total += c.valeur_blackjack()
        if c.rang == "A":
            nb_as += 1
    total += carte.valeur_blackjack()
    if carte.rang == "A":
        nb_as += 1
    while total > 21 and nb_as > 0:
        total -= 10
        nb_as -= 1
    return total


class CalculateurProbabilites:

    @staticmethod
    def probabilite_bust(main_joueur, sabot):
        cartes_restantes = sabot.cartes_restantes()
        if cartes_restantes == 0:
            return 0.0

        cartes_qui_bust = 0
        for carte in sabot.cartes:
            if _total_avec_carte(main_joueur, carte) > 21:
                cartes_qui_bust += 1

        return cartes_qui_bust / cartes_restantes

    @staticmethod
    def probabilite_ameliorer(main_joueur, sabot):
        cartes_restantes = sabot.cartes_restantes()
        if cartes_restantes == 0:
            return 0.0

        cartes_ameliorent = 0
        for carte in sabot.cartes:
            nouveau_total = _total_avec_carte(main_joueur, carte)
            if 17 <= nouveau_total <= 21:
                cartes_ameliorent += 1

        return cartes_ameliorent / cartes_restantes

    @staticmethod
    def distribution_prochaine_carte(sabot):
        cartes_restantes = sabot.cartes_restantes()
        if cartes_restantes == 0:
            return {}

        compteur = {}
        for carte in sabot.cartes:
            v = carte.valeur_blackjack()
            compteur[v] = compteur.get(v, 0) + 1

        return {v: count / cartes_restantes for v, count in sorted(compteur.items())}

    @staticmethod
    def simuler_mains(sabot, nb_simulations=1000):
        resultats = []
        gains_cumules = []
        total = 0

        for i in range(nb_simulations):
            sabot_temp = Sabot(nb_paquets=sabot.nb_paquets)

            main_j = MainJoueur()
            main_d = MainJoueur()
            for _ in range(2):
                main_j.ajouter_carte(sabot_temp.tirer())
                main_d.ajouter_carte(sabot_temp.tirer())

            # Strategie de base simplifiee
            while main_j.valeur_totale() < 17:
                main_j.ajouter_carte(sabot_temp.tirer())

            while main_d.valeur_totale() < 17:
                main_d.ajouter_carte(sabot_temp.tirer())

            score_j = main_j.valeur_totale()
            score_d = main_d.valeur_totale()

            if score_j > 21:
                gain = -1
            elif main_j.est_blackjack():
                gain = 1.5
            elif score_d > 21:
                gain = 1
            elif score_j > score_d:
                gain = 1
            elif score_j < score_d:
                gain = -1
            else:
                gain = 0

            total += gain
            resultats.append(gain)
            gains_cumules.append(total / (i + 1))

        return gains_cumules

    @staticmethod
    def simuler_monte_carlo(main_joueur, dealer, sabot, nb_simulations=500):
        if not dealer.cartes or not main_joueur.cartes:
            return {}

        carte_visible_dealer = dealer.cartes[0].valeur_blackjack()
        valeur_initiale_joueur = main_joueur.valeur_totale()

        # Liste des valeurs de cartes restantes pour tirer rapidement au hasard
        valeurs_dispo = [c.valeur_blackjack() for c in sabot.cartes]
        if not valeurs_dispo:
            return {}

        stats = {}
        actions_possibles = ["Stand", "Hit"]
        if main_joueur.peut_double():
            actions_possibles.append("Double")

        for action in actions_possibles:
            victoires = 0

            for _ in range(nb_simulations):
                total_joueur = valeur_initiale_joueur
                as_joueur = sum(1 for c in main_joueur.cartes if c.rang == "A")

                # Le joueur joue son action virtuelle
                if action == "Hit" or action == "Double":
                    carte_tiree = random.choice(valeurs_dispo)
                    if carte_tiree == 11: as_joueur += 1
                    total_joueur += carte_tiree

                    # Ajustement des As si on dépasse 21
                    while total_joueur > 21 and as_joueur > 0:
                        total_joueur -= 10
                        as_joueur -= 1

                if total_joueur > 21:
                    continue  # Défaite automatique (Bust)

                # Le dealer joue (règle: s'arrête à 17)
                total_dealer = carte_visible_dealer
                as_dealer = 1 if carte_visible_dealer == 11 else 0
                # On assume que la carte cachée est tirée aléatoirement

                while total_dealer < 17:
                    carte_dealer = random.choice(valeurs_dispo)
                    if carte_dealer == 11: as_dealer += 1
                    total_dealer += carte_dealer

                    while total_dealer > 21 and as_dealer > 0:
                        total_dealer -= 10
                        as_dealer -= 1

                # Qui gagne ?
                if total_dealer > 21 or total_joueur > total_dealer:
                    victoires += 1
                elif total_joueur == total_dealer and action == "Double":
                    # Au double, une égalité rembourse, ce n'est pas une vraie "victoire" complète,
                    # mais on peut compter 0.5 victoire pour la statistique.
                    victoires += 0.5

                    # Calcul du pourcentage
            stats[action] = (victoires / nb_simulations) * 100

        return stats
