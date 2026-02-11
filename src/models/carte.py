class Carte:
    #Représente une carte standard (ex: Valet de Coeur)

    #Constantes
    couleurs = ["❤️", "♦️", "♠️", "♣️"]
    rang = ["2", "3", "4", "5", "6", "7", "8", "9", "10", "J", "Q", "K", "A"]

    def __init__(self, rang, couleur):
        self.rang = rang
        self.couleur = couleur

    def valeur_blackjack(self):
        #Retourne la valeur numérique. 10 pour les faces, 11 pour l'As (par défaut, pas oublier de mettre = 1 + tard)
        if self.rang in ["J", "Q", "K"]:
            return 10
        elif self.rang == "A":
            return 11
        else:
            return int(self.rang)

    def __str__(self):
        #Affiche la carte "bien"
        return f"[{self.rang} {self.couleur}]"