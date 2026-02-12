import sys
from PySide6.QtWidgets import QApplication
from src.models.jeu import Jeu
from src.views.fenetre_jeu import FenetreJeu


def main():
    # Créer l'application PySide
    app = QApplication(sys.argv)

    # Initialiser le Moteur (Modèle)
    moteur_jeu = Jeu()

    # Initialiser la vue et lui donner le moteur
    fenetre = FenetreJeu(moteur_jeu)

    # Afficher la fenêtre
    fenetre.show()

    # Boucle infini de l'application
    sys.exit(app.exec())


if __name__ == "__main__":
    main()