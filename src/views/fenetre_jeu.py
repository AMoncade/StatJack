from PySide6.QtWidgets import QMainWindow, QPushButton, QVBoxLayout, QHBoxLayout, QWidget, QLabel, QFrame
from PySide6.QtCore import Qt
from PySide6.QtGui import QPixmap


class FenetreJeu(QMainWindow):
    def __init__(self, jeu_logique):
        super().__init__()
        self.jeu = jeu_logique

        self.setWindowTitle("StatJack - Le Laboratoire de Blackjack")
        self.resize(1100, 700)  # Un peu plus large pour faire de la place au sabot

        #widget central
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.layout_global = QHBoxLayout(self.central_widget)

        # zone jeu
        self.zone_jeu = QWidget()
        self.layout_principal = QVBoxLayout(self.zone_jeu)
        self.layout_global.addWidget(self.zone_jeu, stretch=3)  # Prend 3/4 de la largeur

        style_texte = "font-size: 18px; font-weight: bold; padding: 10px;"

        self.label_info_dealer = QLabel("Dealer")
        self.label_info_dealer.setStyleSheet(style_texte)
        self.label_info_dealer.setAlignment(Qt.AlignCenter)
        self.layout_principal.addWidget(self.label_info_dealer)

        self.layout_cartes_dealer = QHBoxLayout()
        self.layout_cartes_dealer.setAlignment(Qt.AlignCenter)
        self.layout_principal.addLayout(self.layout_cartes_dealer)

        self.label_resultat = QLabel("")
        self.label_resultat.setStyleSheet("font-size: 24px; color: blue; font-weight: bold;")
        self.label_resultat.setAlignment(Qt.AlignCenter)
        self.layout_principal.addWidget(self.label_resultat)

        self.label_info_joueur = QLabel("Vous")
        self.label_info_joueur.setStyleSheet(style_texte)
        self.label_info_joueur.setAlignment(Qt.AlignCenter)
        self.layout_principal.addWidget(self.label_info_joueur)

        self.layout_cartes_joueur = QHBoxLayout()
        self.layout_cartes_joueur.setAlignment(Qt.AlignCenter)
        self.layout_principal.addLayout(self.layout_cartes_joueur)

        self.layout_boutons = QHBoxLayout()
        self.btn_tirer = QPushButton("Tirer (Hit)")
        self.btn_rester = QPushButton("Rester (Stand)")
        self.btn_rejouer = QPushButton("Nouvelle Manche")
        self.btn_rejouer.hide()

        for btn in [self.btn_tirer, self.btn_rester, self.btn_rejouer]:
            btn.setMinimumHeight(50)
            btn.setStyleSheet("font-size: 14px;")

        self.layout_boutons.addWidget(self.btn_tirer)
        self.layout_boutons.addWidget(self.btn_rester)
        self.layout_boutons.addWidget(self.btn_rejouer)
        self.layout_principal.addLayout(self.layout_boutons)

        # separation
        ligne = QFrame()
        ligne.setFrameShape(QFrame.VLine)
        ligne.setFrameShadow(QFrame.Sunken)
        self.layout_global.addWidget(ligne)

        # zone sabot
        self.zone_sabot = QWidget()
        self.layout_sabot = QVBoxLayout(self.zone_sabot)
        self.layout_sabot.setAlignment(Qt.AlignTop | Qt.AlignCenter)
        self.layout_global.addWidget(self.zone_sabot, stretch=1)  # Prend 1/4 de la largeur

        self.lbl_titre_sabot = QLabel("SABOT\n(6 Paquets)")
        self.lbl_titre_sabot.setStyleSheet("font-size: 20px; font-weight: bold;")
        self.lbl_titre_sabot.setAlignment(Qt.AlignCenter)
        self.layout_sabot.addWidget(self.lbl_titre_sabot)

        # dos de carte
        self.lbl_image_sabot = QLabel()
        self.lbl_image_sabot.setFixedSize(160, 240)
        self.lbl_image_sabot.setStyleSheet(
            "background-color: darkred; border-radius: 5px; border: 2px solid white; margin-top: 20px; margin-bottom: 20px;")
        self.layout_sabot.addWidget(self.lbl_image_sabot)

        # Compteur
        self.lbl_compteur = QLabel("Cartes : 312 / 312")
        self.lbl_compteur.setStyleSheet("font-size: 18px; font-weight: bold; color: darkgreen;")
        self.lbl_compteur.setAlignment(Qt.AlignCenter)
        self.layout_sabot.addWidget(self.lbl_compteur)

        # Bouton pour remelanger
        self.btn_reset_sabot = QPushButton("Mélanger le Sabot")
        self.btn_reset_sabot.setMinimumHeight(40)
        self.btn_reset_sabot.setStyleSheet("font-size: 14px; background-color: #f0ad4e; font-weight: bold;")
        self.layout_sabot.addWidget(self.btn_reset_sabot)

        # connexion
        self.btn_tirer.clicked.connect(self.action_tirer)
        self.btn_rester.clicked.connect(self.action_rester)
        self.btn_rejouer.clicked.connect(self.demarrer_nouvelle_manche)
        self.btn_reset_sabot.clicked.connect(self.action_reset_sabot)

        # Démarrage
        self.demarrer_nouvelle_manche()

    # interface logique
    def demarrer_nouvelle_manche(self):
        self.jeu.demarrer_manche()
        self.btn_tirer.setEnabled(True)
        self.btn_rester.setEnabled(True)
        self.btn_rejouer.hide()
        self.label_resultat.setText("")
        self.rafraichir_interface(tour_fini=False)

    def action_tirer(self):
        self.jeu.joueur_tire()
        self.rafraichir_interface(tour_fini=False)
        if self.jeu.joueur.est_busted():
            self.finir_manche()

    def action_rester(self):
        self.jeu.tour_du_dealer()
        self.finir_manche()

    def action_reset_sabot(self):
        # fonction avec les 312 cartes
        if hasattr(self.jeu, 'creer_sabot'):
            self.jeu.creer_sabot()

        self.demarrer_nouvelle_manche()

    def finir_manche(self):
        resultat = self.jeu.resultat()
        self.label_resultat.setText(resultat)
        self.btn_tirer.setEnabled(False)
        self.btn_rester.setEnabled(False)
        self.btn_rejouer.show()
        self.rafraichir_interface(tour_fini=True)

    def rafraichir_interface(self, tour_fini):
        self.label_info_joueur.setText(f"Vous : {self.jeu.joueur}")

        if tour_fini:
            self.label_info_dealer.setText(f"Dealer : {self.jeu.dealer}")
        else:
            self.label_info_dealer.setText("Dealer : ?")

        self.vider_layout(self.layout_cartes_joueur)
        self.vider_layout(self.layout_cartes_dealer)

        for carte in self.jeu.joueur.cartes:
            self.ajouter_carte(self.layout_cartes_joueur, carte)

        if tour_fini:
            for carte in self.jeu.dealer.cartes:
                self.ajouter_carte(self.layout_cartes_dealer, carte)
        else:
            if len(self.jeu.dealer.cartes) > 0:
                premiere_carte = self.jeu.dealer.cartes[0]
                self.ajouter_carte(self.layout_cartes_dealer, premiere_carte)

                lbl_cache = QLabel()
                lbl_cache.setFixedSize(160, 240)
                lbl_cache.setStyleSheet("background-color: darkred; border-radius: 5px; border: 2px solid white;")
                self.layout_cartes_dealer.addWidget(lbl_cache)

        # mise a jour compteur carte
        try:
            if hasattr(self.jeu, 'sabot') and hasattr(self.jeu.sabot, 'cartes'):
                cartes_restantes = len(self.jeu.sabot.cartes)
            else:
                cartes_restantes = len(self.jeu.sabot)

            self.lbl_compteur.setText(f"Cartes : {cartes_restantes} / 312")

            # Change la couleur en rouge si pas bcp de carte
            if cartes_restantes < 52:
                self.lbl_compteur.setStyleSheet("font-size: 18px; font-weight: bold; color: red;")
            else:
                self.lbl_compteur.setStyleSheet("font-size: 18px; font-weight: bold; color: darkgreen;")

        except Exception as e:
            # ÇA C'EST POUR NOUS AIDER À DÉBOGUER
            print(f"BUG COMPTEUR : {e}")
            self.lbl_compteur.setText("Cartes : ? / 312")

    def ajouter_carte(self, layout, carte):
        chemin = carte.get_image_path()
        lbl = QLabel()
        pixmap = QPixmap(chemin)
        if not pixmap.isNull():
            pixmap = pixmap.scaled(160, 240, Qt.KeepAspectRatio, Qt.SmoothTransformation)  # MÊME TAILLE QU'EN HAUT !
            lbl.setPixmap(pixmap)
        else:
            lbl.setText(str(carte))
        layout.addWidget(lbl)

    def vider_layout(self, layout):
        while layout.count():
            item = layout.takeAt(0)
            widget = item.widget()
            if widget is not None:
                widget.deleteLater()