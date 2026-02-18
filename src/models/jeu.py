from src.models.sabot import Sabot
from src.models.main_joueur import MainJoueur


class Jeu:

    def __init__(self, banque=None, nb_paquets=6):
        self.sabot = Sabot(nb_paquets=nb_paquets)
        self.banque = banque
        self.dealer = MainJoueur()
        self.mains_joueur = [MainJoueur()]
        self.index_main_active = 0
        self.mise_principale = 0
        self.resultats = []
        self.manche_en_cours = False

    @property
    def joueur(self):
        return self.mains_joueur[self.index_main_active]

    def placer_mises(self, principale):
        total = principale
        if self.banque and not self.banque.placer_mise(total):
            return False
        self.mise_principale = principale
        return True

    def demarrer_manche(self):
        self.dealer = MainJoueur()
        main_initiale = MainJoueur()
        main_initiale.mise = self.mise_principale
        self.mains_joueur = [main_initiale]
        self.index_main_active = 0
        self.resultats = []


        if self.sabot.cartes_restantes() < 20:
            self.sabot.initialiser_sabot()

        self.mains_joueur[0].ajouter_carte(self.sabot.tirer())
        self.dealer.ajouter_carte(self.sabot.tirer())
        self.mains_joueur[0].ajouter_carte(self.sabot.tirer())
        self.dealer.ajouter_carte(self.sabot.tirer())

        self.manche_en_cours = True


    def joueur_tire(self):
        carte = self.sabot.tirer()
        self.joueur.ajouter_carte(carte)
        return carte

    def joueur_double(self):
        if not self.joueur.peut_double():
            return None
        cout = self.joueur.mise
        if self.banque and not self.banque.placer_mise(cout):
            return None
        self.joueur.mise *= 2
        self.joueur.est_double = True
        carte = self.sabot.tirer()
        self.joueur.ajouter_carte(carte)
        return carte

    def joueur_split(self):
        main = self.joueur
        if not main.peut_split():
            return False
        cout = main.mise
        if self.banque and not self.banque.placer_mise(cout):
            return False

        carte_retiree = main.retirer_carte()
        nouvelle_main = MainJoueur()
        nouvelle_main.mise = main.mise
        nouvelle_main.ajouter_carte(carte_retiree)

        main.ajouter_carte(self.sabot.tirer())
        nouvelle_main.ajouter_carte(self.sabot.tirer())

        self.mains_joueur.insert(self.index_main_active + 1, nouvelle_main)
        return True

    def passer_main_suivante(self):
        if self.index_main_active < len(self.mains_joueur) - 1:
            self.index_main_active += 1
            return True
        return False

    def toutes_mains_jouees(self):
        return self.index_main_active >= len(self.mains_joueur) - 1

    def tour_du_dealer(self):
        while self.dealer.valeur_totale() < 17:
            self.dealer.ajouter_carte(self.sabot.tirer())

    def calculer_resultats(self):
        self.tour_du_dealer()
        self.resultats = []
        score_d = self.dealer.valeur_totale()
        dealer_bj = self.dealer.est_blackjack()
        total_gains = 0

        for main in self.mains_joueur:
            score_j = main.valeur_totale()
            joueur_bj = main.est_blackjack() and len(self.mains_joueur) == 1

            if main.est_busted():
                res = "Perdu (Bust)"
                gain = 0
            elif joueur_bj and dealer_bj:
                res = "Égalité (Push)"
                gain = main.mise
            elif joueur_bj:
                res = "Blackjack!"
                gain = main.mise + int(main.mise * 1.5)
            elif dealer_bj:
                res = "Perdu (Dealer Blackjack)"
                gain = 0
            elif score_d > 21:
                res = "Gagné (Dealer Bust)"
                gain = main.mise * 2
            elif score_j > score_d:
                res = "Gagné"
                gain = main.mise * 2
            elif score_j < score_d:
                res = "Perdu"
                gain = 0
            else:
                res = "Égalité (Push)"
                gain = main.mise

            total_gains += gain
            self.resultats.append(res)

        if self.banque and total_gains > 0:
            self.banque.payer(total_gains)

        self.manche_en_cours = False
        return self.resultats

    def resultat(self):
        if self.resultats:
            return self.resultats[0]
        return "?"
