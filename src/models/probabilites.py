from src.models.sabot import Sabot
from src.models.main_joueur import MainJoueur


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
