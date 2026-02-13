from PySide6.QtWidgets import QMainWindow, QPushButton, QVBoxLayout, QHBoxLayout, QWidget, QLabel
from PySide6.QtCore import Qt
from PySide6.QtGui import QPixmap


class FenetreJeu(QMainWindow):
    def __init__(self, jeu_logique):
        super().__init__()
        self.jeu = jeu_logique  # Lien vers le Modèle

        self.setWindowTitle("StatJack - Le Laboratoire de Blackjack")
        self.resize(1000, 700)  # augmenter la taille pour les images

        # mise en place visuel
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.layout_principal = QVBoxLayout(self.central_widget)

        # Zone d'affichage augmenter la taille
        style_texte = "font-size: 18px; font-weight: bold; padding: 10px;"

        self.label_info_dealer = QLabel("Dealer")
        self.label_info_dealer.setStyleSheet(style_texte)
        self.label_info_dealer.setAlignment(Qt.AlignCenter)
        self.layout_principal.addWidget(self.label_info_dealer)

        # boite pour cartes dealer
        self.layout_cartes_dealer = QHBoxLayout()
        self.layout_cartes_dealer.setAlignment(Qt.AlignCenter)
        self.layout_principal.addLayout(self.layout_cartes_dealer)

        self.label_resultat = QLabel("")
        self.label_resultat.setStyleSheet("font-size: 24px; color: blue; font-weight: bold;")
        self.label_resultat.setAlignment(Qt.AlignCenter)
        self.layout_principal.addWidget(self.label_resultat)  # On le met au milieu

        self.label_info_joueur = QLabel("Vous")
        self.label_info_joueur.setStyleSheet(style_texte)
        self.label_info_joueur.setAlignment(Qt.AlignCenter)
        self.layout_principal.addWidget(self.label_info_joueur)

        # boite pour cartes joueur
        self.layout_cartes_joueur = QHBoxLayout()
        self.layout_cartes_joueur.setAlignment(Qt.AlignCenter)
        self.layout_principal.addLayout(self.layout_cartes_joueur)

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
        # Réinitialise l'interface et le modele pour un nouveau tour
        self.jeu.demarrer_manche()

        # On réactive les boutons de jeu
        self.btn_tirer.setEnabled(True)
        self.btn_rester.setEnabled(True)
        self.btn_rejouer.hide()
        self.label_resultat.setText("")

        self.rafraichir_interface(tour_fini=False)

    def action_tirer(self):
        # Le joueur demande une carte
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
        # Affiche le résultat final
        resultat = self.jeu.resultat()
        self.label_resultat.setText(resultat)

        self.btn_tirer.setEnabled(False)
        self.btn_rester.setEnabled(False)
        self.btn_rejouer.show()

        self.rafraichir_interface(tour_fini=True)

    def rafraichir_interface(self, tour_fini):
        # Met à jour les textes selon l'état (lien)

        # Affichage du Joueur
        self.label_info_joueur.setText(f"Vous : {self.jeu.joueur}")

        # Affichage dealer
        if tour_fini:
            self.label_info_dealer.setText(f"Dealer : {self.jeu.dealer}")
        else:
            self.label_info_dealer.setText("Dealer : ?")

        # clean la table avant d'afficher
        self.vider_layout(self.layout_cartes_joueur)
        self.vider_layout(self.layout_cartes_dealer)

        # mettre images joueur
        for carte in self.jeu.joueur.cartes:  # check si c'est cartes ou main dans ton code
            self.ajouter_carte(self.layout_cartes_joueur, carte)

        # montrer tout
        if tour_fini:
            for carte in self.jeu.dealer.cartes:
                self.ajouter_carte(self.layout_cartes_dealer, carte)
        else:
            # juste la premiere visible
            premiere_carte = self.jeu.dealer.cartes[0]
            self.ajouter_carte(self.layout_cartes_dealer, premiere_carte)

            # carte cachée 🂠
            lbl_cache = QLabel()
            lbl_cache.setFixedSize(125, 250)
            lbl_cache.setStyleSheet("background-color: darkred; border-radius: 5px; border: 2px solid white;")
            self.layout_cartes_dealer.addWidget(lbl_cache)

    def ajouter_carte(self, layout, carte):
        # associer image = carte
        chemin = carte.get_image_path()

        lbl = QLabel()
        pixmap = QPixmap(chemin)

        if not pixmap.isNull():
            pixmap = pixmap.scaled(200, 400, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            lbl.setPixmap(pixmap)
        else:
            lbl.setText(str(carte))  # si l'image plante

        layout.addWidget(lbl)

    def vider_layout(self, layout):
        # enleve les vielles cartes
        while layout.count():
            item = layout.takeAt(0)
            widget = item.widget()
            if widget is not None:
                widget.deleteLater()