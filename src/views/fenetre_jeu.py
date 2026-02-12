from PySide6.QtWidgets import QMainWindow, QPushButton, QVBoxLayout, QHBoxLayout, QWidget, QLabel, QMessageBox
from PySide6.QtCore import Qt


class FenetreJeu(QMainWindow):
    def __init__(self, jeu_logique):
        super().__init__()
        self.jeu = jeu_logique  # Lien vers le Modèle

        self.setWindowTitle("StatJack - Le Laboratoire de Blackjack")
        self.resize(800, 600)

        # mise en place visuel
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.layout_principal = QVBoxLayout(self.central_widget)

        # Zone d'affichage augmenter la taille
        style_texte = "font-size: 18px; font-weight: bold; padding: 10px;"

        self.label_dealer = QLabel("Dealer : [ ? ]")
        self.label_dealer.setStyleSheet(style_texte)
        self.label_dealer.setAlignment(Qt.AlignCenter)

        self.label_joueur = QLabel("Vous : [ ? ]")
        self.label_joueur.setStyleSheet(style_texte)
        self.label_joueur.setAlignment(Qt.AlignCenter)

        self.label_resultat = QLabel("")
        self.label_resultat.setStyleSheet("font-size: 24px; color: blue; font-weight: bold;")
        self.label_resultat.setAlignment(Qt.AlignCenter)

        self.layout_principal.addWidget(self.label_dealer)
        self.layout_principal.addWidget(self.label_resultat)  # On le met au milieu
        self.layout_principal.addWidget(self.label_joueur)

        # Zone des boutons
        self.layout_boutons = QHBoxLayout()
        self.btn_tirer = QPushButton("Tirer (Hit)")
        self.btn_rester = QPushButton("Rester (Stand)")
        self.btn_rejouer = QPushButton("Nouvelle Manche")  # Bouton pour recommencer
        self.btn_rejouer.hide()  # Caché au début

        # Style des boutons
        for btn in [self.btn_tirer, self.btn_rester, self.btn_rejouer]:
            btn.setMinimumHeight(50)
            btn.setStyleSheet("font-size: 14px;")

        self.layout_boutons.addWidget(self.btn_tirer)
        self.layout_boutons.addWidget(self.btn_rester)
        self.layout_boutons.addWidget(self.btn_rejouer)
        self.layout_principal.addLayout(self.layout_boutons)

        # lier les boutons aux actions
        self.btn_tirer.clicked.connect(self.action_tirer)
        self.btn_rester.clicked.connect(self.action_rester)
        self.btn_rejouer.clicked.connect(self.demarrer_nouvelle_manche)

        # demarrage
        self.demarrer_nouvelle_manche()

    def demarrer_nouvelle_manche(self):
        #Réinitialise l'interface et le modele pour un nouveau tour
        self.jeu.demarrer_manche()

        # On réactive les boutons de jeu
        self.btn_tirer.setEnabled(True)
        self.btn_rester.setEnabled(True)
        self.btn_rejouer.hide()
        self.label_resultat.setText("")

        self.rafraichir_interface(tour_fini=False)

    def action_tirer(self):
        #Le joueur demande une carte
        self.jeu.joueur_tire()
        self.rafraichir_interface(tour_fini=False)

        # verif si a bust
        if self.jeu.joueur.est_busted():
            self.finir_manche()

    def action_rester(self):
        # tour du dealer
        self.jeu.tour_du_dealer()
        self.finir_manche()

    def finir_manche(self):
        #Affiche le résultat final
        resultat = self.jeu.resultat()
        self.label_resultat.setText(resultat)

        self.btn_tirer.setEnabled(False)
        self.btn_rester.setEnabled(False)
        self.btn_rejouer.show()

        self.rafraichir_interface(tour_fini=True)

    def rafraichir_interface(self, tour_fini):
        #Met à jour les textes selon l'état (lien)
        # Affichage du Joueur
        self.label_joueur.setText(f"Vous : {self.jeu.joueur}")

        # Affichage dealer
        if not tour_fini:

            carte_visible = self.jeu.dealer.cartes[0]
            self.label_dealer.setText(f"Dealer : [{carte_visible}] [ 🂠 ]")
        else:
            # montrer tout
            self.label_dealer.setText(f"Dealer : {self.jeu.dealer}")