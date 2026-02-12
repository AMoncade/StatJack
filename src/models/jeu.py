from src.models.sabot import Sabot
from src.models.main_joueur import MainJoueur

#Doit gerer le déroulement d'une manche
#Penser que joueur peut split, double, hit, stand apres avoir recu ses deux cartes
#Penser dealer doit tirer jusqu'a ce qu'il atteigne au minimum 17

from src.models.sabot import Sabot
from src.models.main_joueur import MainJoueur


class Jeu:

    def __init__(self):
        self.sabot = Sabot(nb_paquets=6)
        self.joueur = MainJoueur()
        self.dealer = MainJoueur()

    def demarrer_manche(self):
        #Réinitialise les mains et distribue 2 cartes à chacun
        self.joueur = MainJoueur()
        self.dealer = MainJoueur()

        # Si le sabot est presque vide (20 cartes), on remélange
        if self.sabot.cartes_restantes() < 20:
            self.sabot.initialiser_sabot()

        # Distribution alternée : Joueur -> Dealer -> Joueur -> Dealer
        self.joueur.ajouter_carte(self.sabot.tirer())
        self.dealer.ajouter_carte(self.sabot.tirer())
        self.joueur.ajouter_carte(self.sabot.tirer())
        self.dealer.ajouter_carte(self.sabot.tirer())

    def joueur_tire(self):
        #Action 'HIT' du joueur
        carte = self.sabot.tirer()
        self.joueur.ajouter_carte(carte)
        return carte

    def tour_du_dealer(self):
        # Dealer doit tirer tant qu'il a moins de 17

        while self.dealer.valeur_totale() < 17:
            self.dealer.ajouter_carte(self.sabot.tirer())

    def resultat(self):
        #Détermine le gagnant
        score_j = self.joueur.valeur_totale()
        score_d = self.dealer.valeur_totale()

        if score_j > 21:
            return "Perdu (Bust)"
        elif score_d > 21:
            return "Gagné (Dealer Bust)"
        elif score_j > score_d:
            return "Gagné"
        elif score_j < score_d:
            return "Perdu"
        else:
            return "Égalité (Push)"