import random
from src.models.carte import Carte


class Sabot:
    # Gère un sabot de plusieurs paquets de cartes (Standard des casinos = 6)

    def __init__(self, nb_paquets=6):
        self.nb_paquets = nb_paquets
        self.cartes = []
        self.running_count = 0
        self.initialiser_sabot()

    def initialiser_sabot(self):
        # Crée les cartes
        self.cartes = []
        self.running_count = 0
        for _ in range(self.nb_paquets):
            for couleur in Carte.couleurs:
                for rang in Carte.rang:
                    self.cartes.append(Carte(rang, couleur))

        self.melanger()

    def melanger(self):
        # Mélange aléatoire
        self.running_count = 0
        random.shuffle(self.cartes)

    def tirer(self):
        # Retire la carte du dessus et la retourne (None si c'est vide)
        if len(self.cartes) > 0:
            carte = self.cartes.pop()
            self.running_count += carte.valeur_hilo()
            return carte
        return None

    def cartes_restantes(self):
        return len(self.cartes)

    def true_count(self):
        paquets_restants = max(self.cartes_restantes() / 52, 0.5)
        return self.running_count / paquets_restants

    def clone(self):
        # Copie l'état du sabot
        s = Sabot(nb_paquets=self.nb_paquets)
        # Écrase l'état généré par __init__ avec l'état réel
        s.cartes = list(self.cartes)
        s.running_count = self.running_count
        return s

    def melanger_sans_reset(self):
        random.shuffle(self.cartes)

    def retirer_carte(self, carte):
        # Retire une carte du sabot
        try:
            idx = self.cartes.index(carte)
        except ValueError:
            return False

        c = self.cartes.pop(idx)
        self.running_count += c.valeur_hilo()
        return True

    def retirer_cartes(self, cartes):
        # Retire plusieurs carte
        for c in cartes:
            self.retirer_carte(c)

