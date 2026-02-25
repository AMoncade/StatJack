import sys
import os

# Garantir que le dossier StatJack est dans sys.path (fix PyCharm / CWD différent)
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from PySide6.QtWidgets import QApplication

from src.models.settings import Settings
from src.models.banque import Banque
from src.models.audio import AudioManager
from src.models.jeu import Jeu

from src.views.app_window import AppWindow, PAGE_MENU, PAGE_JEU, PAGE_PARAMETRES, PAGE_TUTORIEL
from src.views.menu_principal import MenuPrincipal
from src.views.vue_jeu import VueJeu
from src.views.vue_parametres import VueParametres
from src.views.vue_tutoriel import VueTutoriel

from src.controllers.controleur_jeu import ControleurJeu
from src.controllers.controleur_tutoriel import ControleurTutoriel


STYLE_GLOBAL = """
    QMainWindow {
        background-color: #0d0d1a;
    }
    QWidget {
        font-family: 'Helvetica Neue', Arial ;
    }
    QMessageBox {
        background-color: #1a1a2e;
        color: white;
    }
    QMessageBox QLabel {
        color: white;
    }
    QMessageBox QPushButton {
        background-color: #2d2d44;
        color: white;
        border: 1px solid #555;
        border-radius: 5px;
        padding: 5px 15px;
        min-width: 60px;
    }
"""


def main():
    app = QApplication(sys.argv)
    app.setStyleSheet(STYLE_GLOBAL)

    # Modeles
    settings = Settings()
    banque = Banque(settings)
    audio = AudioManager(settings)
    jeu = Jeu(banque=banque, nb_paquets=settings.get("nb_paquets"))

    # Fenetre principale
    fenetre = AppWindow()

    # Vues
    menu = MenuPrincipal(banque)
    vue_jeu = VueJeu()
    vue_params = VueParametres(settings, banque, audio)
    vue_tuto = VueTutoriel()

    # Ordre: PAGE_MENU=0, PAGE_JEU=1, PAGE_PARAMETRES=2, PAGE_TUTORIEL=3
    fenetre.ajouter_page(menu)
    fenetre.ajouter_page(vue_jeu)
    fenetre.ajouter_page(vue_params)
    fenetre.ajouter_page(vue_tuto)

    # Controleurs
    ctrl_jeu = ControleurJeu(vue_jeu, jeu, audio)
    ctrl_tuto = ControleurTutoriel(vue_tuto)

    # Navigation depuis le menu
    def aller_jouer():
        from src.models.sabot import Sabot
        jeu.sabot = Sabot(nb_paquets=settings.get("nb_paquets"))
        vue_jeu.afficher_argent(banque.solde)
        fenetre.aller_a(PAGE_JEU)

    def aller_menu():
        menu.rafraichir_argent()
        fenetre.aller_a(PAGE_MENU)

    def aller_tuto():
        ctrl_tuto.demarrer()
        fenetre.aller_a(PAGE_TUTORIEL)

    menu.jouer_clique.connect(aller_jouer)
    menu.tutoriel_clique.connect(aller_tuto)
    menu.parametres_clique.connect(lambda: fenetre.aller_a(PAGE_PARAMETRES))
    menu.quitter_clique.connect(app.quit)

    # Navigation retour
    vue_jeu.retour_menu_clique.connect(aller_menu)
    vue_jeu.parametres_clique.connect(lambda: fenetre.aller_a(PAGE_PARAMETRES))
    vue_params.retour_clique.connect(aller_menu)
    vue_tuto.quitter_clique.connect(aller_menu)

    # Demarrage
    fenetre.aller_a(PAGE_MENU)
    fenetre.show()

    audio.jouer_musique()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
