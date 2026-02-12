from src.models.carte import Carte

#Donner une main aleatoirement au joueur (s'assurrer que A = 11 puisse devenir A = 1 (regle bj))

from src.models.carte import Carte

class MainJoueur:
    #Représente les cartes tenues par un joueur (ou le dealer)

    def __init__(self):
        self.cartes = []

    def ajouter_carte(self, carte):
        #Ajoute une carte à la main
        self.cartes.append(carte)

    def valeur_totale(self):
        #Gerer As = 1 ou 11
        valeur = 0
        nb_as = 0

        # si As = 11
        for carte in self.cartes:
            v = carte.valeur_blackjack()
            valeur += v
            if carte.rang == "A":
                nb_as += 1

        # Si on dépasse 21 As = 1
        while valeur > 21 and nb_as > 0:
            valeur -= 10  # On passe l'As de 11 à 1
            nb_as -= 1

        return valeur

    def est_blackjack(self):
        # Retourne True si c'est un Blackjack
        return len(self.cartes) == 2 and self.valeur_totale() == 21

    def est_busted(self):
        # Retourne True si la main dépasse 21
        return self.valeur_totale() > 21

    def __str__(self):
     # Afficher main
        liste_cartes = " ".join(str(c) for c in self.cartes)
        return f"{liste_cartes} (Total: {self.valeur_totale()})"