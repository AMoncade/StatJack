import random
from src.models.carte import Carte


class Sabot:
    #Gère un sabot de plusieurs paquets de cartes (Standard des casinos = 6)

    def __init__(self, nb_paquets = 6):
        self.nb_paquets = nb_paquets
        self.cartes = []
        self.initialiser_sabot()

    def initialiser_sabot(self):
        #Crée les cartes
        self.cartes = []
        for _ in range(self.nb_paquets):
            for couleur in Carte.couleurs:
                for rang in Carte.rang:
                    self.cartes.append(Carte(rang, couleur))

        self.melanger()

    def melanger(self):
        #Mélange aléatoire
        random.shuffle(self.cartes)

    def tirer(self):
        #Retire la carte du dessus et la retourne (None si c'est vide)
        if len(self.cartes) > 0:
            return self.cartes.pop()
        else:
            return None

    def cartes_restantes(self):
        return len(self.cartes)