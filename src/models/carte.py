import os

class Carte:

    couleurs = ["❤️", "♦️", "♠️", "♣️"]
    rang = ["2", "3", "4", "5", "6", "7", "8", "9", "10", "J", "Q", "K", "A"]

    def __init__(self, rang, couleur):
        self.rang = rang
        self.couleur = couleur

    def valeur_blackjack(self):
        if self.rang in ["J", "Q", "K"]:
            return 10
        elif self.rang == "A":
            return 11
        else:
            return int(self.rang)

    def valeur_hilo(self):
        v = self.valeur_blackjack()
        if v <= 6:
            return 1
        elif v <= 9:
            return 0
        else:
            return -1

    def __eq__(self, other):
        if not isinstance(other, Carte):
            return False
        return self.rang == other.rang and self.couleur == other.couleur

    def __hash__(self):
        return hash((self.rang, self.couleur))

    def get_image_path(self):
        traduction_couleur = {
            "❤️": "hearts",
            "♦️": "diamonds",
            "♠️": "spades",
            "♣️": "clubs"
        }

        nom_couleur = traduction_couleur[self.couleur]
        return os.path.join("cartes", f"{self.rang}_{nom_couleur}.png")

    def __str__(self):
        return f"[{self.rang} {self.couleur}]"