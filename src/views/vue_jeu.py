from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel,
                               QPushButton, QFrame, QGraphicsOpacityEffect)
from PySide6.QtCore import Signal, Qt, QPropertyAnimation, QEasingCurve, QTimer
from PySide6.QtGui import QColor

from src.views.widgets.carte_widget import CarteWidget
from src.views.widgets.jeton_widget import JetonWidget
from src.views.widgets.cercle_mise import CercleMise
from src.views.widgets.table_fond import TableFond


PHASE_MISE = "MISE"
PHASE_JEU = "JEU"
PHASE_RESULTAT = "RESULTAT"


class VueJeu(QWidget):
    hit_clique = Signal()
    stand_clique = Signal()
    double_clique = Signal()
    split_clique = Signal()
    miser_clique = Signal(int, int, int)
    prochaine_manche_clique = Signal()
    voir_graphe_clique = Signal()
    retour_menu_clique = Signal()
    parametres_clique = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.phase = PHASE_MISE
        self.cercle_actif = "Mise"
        self._animations_en_cours = []
        self._setup_ui()

    def _setup_ui(self):
        layout_racine = QHBoxLayout(self)
        layout_racine.setContentsMargins(0, 0, 0, 0)

        # Zone principale (table verte)
        self.table = TableFond()
        layout_table = QVBoxLayout(self.table)
        layout_table.setContentsMargins(15, 10, 15, 10)
        layout_racine.addWidget(self.table, stretch=4)

        # Barre du haut
        barre_haut = QHBoxLayout()
        self.label_argent = QLabel("$10000")
        self.label_argent.setStyleSheet(
            "font-size: 20px; color: #51cf66; font-weight: bold;"
        )
        barre_haut.addWidget(self.label_argent)
        barre_haut.addStretch()

        btn_params = QPushButton("⚙")
        btn_params.setFixedSize(40, 40)
        btn_params.setStyleSheet(
            "font-size: 20px; background: rgba(0,0,0,80); color: white; "
            "border-radius: 20px; border: 1px solid #555;"
        )
        btn_params.clicked.connect(self.parametres_clique.emit)
        barre_haut.addWidget(btn_params)

        btn_menu = QPushButton("Menu")
        btn_menu.setStyleSheet(
            "font-size: 14px; background: rgba(0,0,0,80); color: white; "
            "border-radius: 8px; border: 1px solid #555; padding: 6px 12px;"
        )
        btn_menu.clicked.connect(self.retour_menu_clique.emit)
        barre_haut.addWidget(btn_menu)
        layout_table.addLayout(barre_haut)

        # Zone cartes dealer
        self.label_dealer = QLabel("Dealer")
        self.label_dealer.setAlignment(Qt.AlignCenter)
        self.label_dealer.setStyleSheet(
            "font-size: 18px; color: white; font-weight: bold;"
        )
        layout_table.addWidget(self.label_dealer)

        self.layout_cartes_dealer = QHBoxLayout()
        self.layout_cartes_dealer.setAlignment(Qt.AlignCenter)
        layout_table.addLayout(self.layout_cartes_dealer)

        # Résultat (avec animation)
        self.label_resultat = QLabel("")
        self.label_resultat.setAlignment(Qt.AlignCenter)
        self.label_resultat.setStyleSheet(
            "font-size: 26px; color: #FFD700; font-weight: bold; margin: 5px;"
        )
        layout_table.addWidget(self.label_resultat)

        # Zone cartes joueur
        self.label_joueur = QLabel("Vous")
        self.label_joueur.setAlignment(Qt.AlignCenter)
        self.label_joueur.setStyleSheet(
            "font-size: 18px; color: white; font-weight: bold;"
        )
        layout_table.addWidget(self.label_joueur)

        self.layout_cartes_joueur = QHBoxLayout()
        self.layout_cartes_joueur.setAlignment(Qt.AlignCenter)
        layout_table.addLayout(self.layout_cartes_joueur)

        # Indicateur main active
        self.label_main_active = QLabel("")
        self.label_main_active.setAlignment(Qt.AlignCenter)
        self.label_main_active.setStyleSheet("font-size: 14px; color: #FFD700;")
        layout_table.addWidget(self.label_main_active)

        # Boutons actions (JEU)
        self.widget_actions = QWidget()
        layout_actions = QHBoxLayout(self.widget_actions)
        layout_actions.setAlignment(Qt.AlignCenter)

        style_btn_action = """
            QPushButton {{
                background-color: {bg};
                color: white; border: 2px solid #555;
                border-radius: 10px; font-size: 16px; font-weight: bold;
                padding: 10px 20px; min-width: 100px;
            }}
            QPushButton:hover {{ border-color: #FFD700; }}
            QPushButton:disabled {{ background-color: #333; color: #666; }}
        """

        self.btn_split = QPushButton("Split")
        self.btn_split.setStyleSheet(style_btn_action.format(bg="#7B2D8E"))
        self.btn_split.clicked.connect(self.split_clique.emit)
        layout_actions.addWidget(self.btn_split)

        self.btn_double = QPushButton("Double")
        self.btn_double.setStyleSheet(style_btn_action.format(bg="#D4A017"))
        self.btn_double.clicked.connect(self.double_clique.emit)
        layout_actions.addWidget(self.btn_double)

        self.btn_hit = QPushButton("Hit")
        self.btn_hit.setStyleSheet(style_btn_action.format(bg="#2E7D32"))
        self.btn_hit.clicked.connect(self.hit_clique.emit)
        layout_actions.addWidget(self.btn_hit)

        self.btn_stand = QPushButton("Stand")
        self.btn_stand.setStyleSheet(style_btn_action.format(bg="#C62828"))
        self.btn_stand.clicked.connect(self.stand_clique.emit)
        layout_actions.addWidget(self.btn_stand)

        layout_table.addWidget(self.widget_actions)

        # Boutons post-manche (RESULTAT)
        self.widget_post = QWidget()
        layout_post = QHBoxLayout(self.widget_post)
        layout_post.setAlignment(Qt.AlignCenter)

        style_btn_post = """
            QPushButton {
                background-color: #2d2d44; color: white;
                border: 2px solid #555; border-radius: 10px;
                font-size: 16px; font-weight: bold;
                padding: 10px 20px; min-width: 160px;
            }
            QPushButton:hover { border-color: #FFD700; background-color: #3d3d5c; }
        """

        self.btn_prochaine = QPushButton("Prochaine Manche")
        self.btn_prochaine.setStyleSheet(style_btn_post)
        self.btn_prochaine.clicked.connect(self.prochaine_manche_clique.emit)
        layout_post.addWidget(self.btn_prochaine)

        self.btn_graphe = QPushButton("Voir Graphe")
        self.btn_graphe.setStyleSheet(style_btn_post)
        self.btn_graphe.clicked.connect(self.voir_graphe_clique.emit)
        layout_post.addWidget(self.btn_graphe)

        layout_table.addWidget(self.widget_post)

        # Zone mises (MISE)
        self.widget_mises = QWidget()
        layout_mises = QVBoxLayout(self.widget_mises)
        layout_mises.setAlignment(Qt.AlignCenter)

        lbl_mises = QLabel("Placez vos mises")
        lbl_mises.setAlignment(Qt.AlignCenter)
        lbl_mises.setStyleSheet("font-size: 18px; color: white; font-weight: bold;")
        layout_mises.addWidget(lbl_mises)

        # 3 cercles
        layout_cercles = QHBoxLayout()
        layout_cercles.setAlignment(Qt.AlignCenter)
        layout_cercles.setSpacing(20)

        self.cercle_pp = CercleMise("PP")
        self.cercle_principale = CercleMise("Mise")
        self.cercle_21_3 = CercleMise("21+3")


        for cercle in [self.cercle_pp, self.cercle_principale, self.cercle_21_3]:
            cercle.cercle_clique.connect(self._on_cercle_clique)
            layout_cercles.addWidget(cercle)

        layout_mises.addLayout(layout_cercles)

        # 4 jetons
        layout_jetons = QHBoxLayout()
        layout_jetons.setAlignment(Qt.AlignCenter)
        layout_jetons.setSpacing(10)

        for val in [100, 200, 500, 1000]:
            jeton = JetonWidget(val)
            jeton.jeton_clique.connect(self._on_jeton_clique)
            layout_jetons.addWidget(jeton)

        layout_mises.addLayout(layout_jetons)

        # Boutons dealer/reset
        layout_mise_btns = QHBoxLayout()
        layout_mise_btns.setAlignment(Qt.AlignCenter)

        style_mise_btn = """
            QPushButton {
                background-color: #2d2d44; color: white;
                border: 2px solid #555; border-radius: 8px;
                font-size: 14px; font-weight: bold;
                padding: 8px 20px;
            }
            QPushButton:hover { border-color: #FFD700; }
        """

        self.btn_reset_mises = QPushButton("Réinitialiser")
        self.btn_reset_mises.setStyleSheet(style_mise_btn)
        self.btn_reset_mises.clicked.connect(self._reset_mises)
        layout_mise_btns.addWidget(self.btn_reset_mises)

        self.btn_dealer = QPushButton("Distribuer")
        self.btn_dealer.setStyleSheet(style_mise_btn.replace("#2d2d44", "#2E7D32"))
        self.btn_dealer.clicked.connect(self._on_distribuer)
        layout_mise_btns.addWidget(self.btn_dealer)

        layout_mises.addLayout(layout_mise_btns)

        layout_table.addWidget(self.widget_mises)

        # Sidebar probabilités
        self.sidebar = QFrame()
        self.sidebar.setFixedWidth(220)
        self.sidebar.setStyleSheet(
            "background-color: #1a1a2e; border-left: 2px solid #333;"
        )
        layout_sidebar = QVBoxLayout(self.sidebar)
        layout_sidebar.setAlignment(Qt.AlignTop)

        self.lbl_true_count = QLabel("True Count : --")
        self.lbl_true_count.setStyleSheet(
            "font-size: 14px; color: #FFD700; padding: 4px;"
        )
        layout_sidebar.addWidget(self.lbl_true_count)

        # Label pour l'avantage
        self.lbl_avantage = QLabel("Avantage : --")
        self.lbl_avantage.setStyleSheet(
            "font-size: 14px; color: #AAA; padding: 4px; font-weight: bold;"
        )
        layout_sidebar.addWidget(self.lbl_avantage)

        lbl_probas = QLabel("Probabilités")
        lbl_probas.setAlignment(Qt.AlignCenter)
        lbl_probas.setStyleSheet(
            "font-size: 16px; font-weight: bold; color: white; padding: 8px;"
        )
        layout_sidebar.addWidget(lbl_probas)

        self.lbl_bust = QLabel("Bust : --")
        self.lbl_bust.setStyleSheet("font-size: 14px; color: #ff6b6b; padding: 4px;")
        layout_sidebar.addWidget(self.lbl_bust)

        self.lbl_ameliorer = QLabel("Améliorer (17-21) : --")
        self.lbl_ameliorer.setStyleSheet("font-size: 14px; color: #51cf66; padding: 4px;")
        layout_sidebar.addWidget(self.lbl_ameliorer)

        # % de victoire
        sep_stats = QFrame()
        sep_stats.setFrameShape(QFrame.HLine)
        sep_stats.setStyleSheet("color: #444;")
        layout_sidebar.addWidget(sep_stats)

        self.lbl_win_stand = QLabel("Stand (Gagner) : --")
        self.lbl_win_stand.setStyleSheet("font-size: 14px; color: #FFF; padding: 4px;")
        layout_sidebar.addWidget(self.lbl_win_stand)

        self.lbl_win_hit = QLabel("Hit (Gagner) : --")
        self.lbl_win_hit.setStyleSheet("font-size: 14px; color: #FFF; padding: 4px;")
        layout_sidebar.addWidget(self.lbl_win_hit)

        self.lbl_win_double = QLabel("Double (Gagner) : --")
        self.lbl_win_double.setStyleSheet("font-size: 14px; color: #FFF; padding: 4px;")
        layout_sidebar.addWidget(self.lbl_win_double)

        self.lbl_true_count = QLabel("True Count : --")
        self.lbl_true_count.setStyleSheet(
            "font-size: 14px; color: #FFD700; padding: 4px;"
        )
        layout_sidebar.addWidget(self.lbl_true_count)

        self.lbl_running_count = QLabel("Running Count : --")
        self.lbl_running_count.setStyleSheet(
            "font-size: 14px; color: #AAA; padding: 4px;"
        )
        layout_sidebar.addWidget(self.lbl_running_count)

        sep2 = QFrame()
        sep2.setFrameShape(QFrame.HLine)
        sep2.setStyleSheet("color: #444;")
        layout_sidebar.addWidget(sep2)

        self.lbl_cartes_restantes = QLabel("Cartes : --")
        self.lbl_cartes_restantes.setStyleSheet(
            "font-size: 14px; color: #AAA; padding: 4px;"
        )
        layout_sidebar.addWidget(self.lbl_cartes_restantes)

        layout_sidebar.addStretch()
        layout_racine.addWidget(self.sidebar)

        # Etat initial
        self.set_phase(PHASE_MISE)

    # Phase management
    def set_phase(self, phase):
        self.phase = phase
        self.widget_actions.setVisible(phase == PHASE_JEU)
        self.widget_post.setVisible(phase == PHASE_RESULTAT)
        self.widget_mises.setVisible(phase == PHASE_MISE)
        self.label_main_active.setVisible(phase in (PHASE_JEU, PHASE_RESULTAT))

    # Mises
    def _on_cercle_clique(self, nom):
        self.cercle_actif = nom

    def _on_jeton_clique(self, valeur):
        if self.cercle_actif == "PP":
            self.cercle_pp.ajouter_mise(valeur)
        elif self.cercle_actif == "21+3":
            self.cercle_21_3.ajouter_mise(valeur)
        else:
            self.cercle_principale.ajouter_mise(valeur)

    def _reset_mises(self):
        self.cercle_pp.reset()
        self.cercle_principale.reset()
        self.cercle_21_3.reset()
        self.cercle_actif = "Mise"

    def _on_distribuer(self):
        principale = self.cercle_principale.mise
        if principale <= 0:
            return
        pp = self.cercle_pp.mise
        vingt_et_un = self.cercle_21_3.mise
        self.miser_clique.emit(principale, pp, vingt_et_un)

    # Affichage
    def afficher_argent(self, montant):
        self.label_argent.setText(f"${montant}")

    def afficher_cartes_dealer(self, cartes, reveler=False):
        self._vider_layout(self.layout_cartes_dealer)
        if not cartes:
            return
        if reveler:
            for c in cartes:
                self.layout_cartes_dealer.addWidget(CarteWidget(c))
        else:
            self.layout_cartes_dealer.addWidget(CarteWidget(cartes[0]))
            if len(cartes) > 1:
                self.layout_cartes_dealer.addWidget(CarteWidget(face_cachee=True))

    def afficher_cartes_joueur(self, mains, index_actif=0):
        self._vider_layout(self.layout_cartes_joueur)
        for i, main in enumerate(mains):
            # Label total par main
            total = main.valeur_totale()
            lbl_total = QLabel(f"({total})")
            lbl_total.setStyleSheet(
                "font-size: 14px; font-weight: bold; color: #FFD700; margin-right: 4px;"
            )
            self.layout_cartes_joueur.addWidget(lbl_total)

            for carte in main.cartes:
                w = CarteWidget(carte)
                if len(mains) > 1 and i == index_actif:
                    w.setStyleSheet(w.styleSheet() + "border: 2px solid #FFD700;")
                self.layout_cartes_joueur.addWidget(w)
            if i < len(mains) - 1:
                sep_lbl = QLabel("|")
                sep_lbl.setStyleSheet("font-size: 40px; color: #FFD700;")
                self.layout_cartes_joueur.addWidget(sep_lbl)

        if len(mains) > 1:
            self.label_main_active.setText(
                f"Main {index_actif + 1} / {len(mains)}"
            )
        else:
            self.label_main_active.setText("")

    def afficher_infos_joueur(self, main_joueur, label_extra=""):
        total = main_joueur.valeur_totale()
        txt = f"Vous : {total}"
        if label_extra:
            txt += f" — {label_extra}"
        self.label_joueur.setText(txt)

    def afficher_infos_dealer(self, dealer, reveler=False):
        if reveler:
            self.label_dealer.setText(f"Dealer : {dealer.valeur_totale()}")
        else:
            if dealer.cartes:
                self.label_dealer.setText(
                    f"Dealer : {dealer.cartes[0].valeur_blackjack()}"
                )
            else:
                self.label_dealer.setText("Dealer")

    # Animations
    def animer_victoire(self):
        self._flash_label(self.label_resultat, "#00FF00", "#51cf66")

    def animer_defaite(self):
        self._flash_label(self.label_resultat, "#FF0000", "#ff6b6b")

    def animer_egalite(self):
        self._flash_label(self.label_resultat, "#FFD700", "#FFD700")

    def _flash_label(self, label, couleur_flash, couleur_finale):
        style_base = label.styleSheet()

        # Phase 1 : gros texte couleur flash
        label.setStyleSheet(
            f"font-size: 34px; color: {couleur_flash}; font-weight: bold; margin: 5px;"
        )

        # Phase 2 : revenir à la taille normale
        def phase2():
            label.setStyleSheet(
                f"font-size: 30px; color: {couleur_finale}; font-weight: bold; margin: 5px;"
            )

        # Phase 3 : petite pulse
        def phase3():
            label.setStyleSheet(
                f"font-size: 26px; color: {couleur_finale}; font-weight: bold; margin: 5px;"
            )

        QTimer.singleShot(200, phase2)
        QTimer.singleShot(500, phase3)

    def maj_probabilites(self, pct_bust, pct_ameliorer, stats_actions=None):
        self.lbl_bust.setText(f"Bust : {pct_bust:.1f}%")
        self.lbl_ameliorer.setText(f"Améliorer (17-21) : {pct_ameliorer:.1f}%")

        if pct_bust > 50:
            self.lbl_bust.setStyleSheet("font-size: 14px; color: #ff0000; padding: 4px;")
        elif pct_bust > 25:
            self.lbl_bust.setStyleSheet("font-size: 14px; color: #ff6b6b; padding: 4px;")
        else:
            self.lbl_bust.setStyleSheet("font-size: 14px; color: #ffd93d; padding: 4px;")

        # Affichage des stats Monte Carlo
        if stats_actions:
            self.lbl_win_stand.setText(f"Stand (Gagner) : {stats_actions.get('Stand', 0):.1f}%")
            self.lbl_win_hit.setText(f"Hit (Gagner) : {stats_actions.get('Hit', 0):.1f}%")

            # Griser le Double s'il n'est pas possible
            if 'Double' in stats_actions:
                self.lbl_win_double.setText(f"Double (Gagner) : {stats_actions['Double']:.1f}%")
                self.lbl_win_double.setStyleSheet("font-size: 14px; color: #FFF; padding: 4px;")
            else:
                self.lbl_win_double.setText("Double (Gagner) : --")
                self.lbl_win_double.setStyleSheet("font-size: 14px; color: #555; padding: 4px;")
        else:
            self.lbl_win_stand.setText("Stand (Gagner) : --")
            self.lbl_win_hit.setText("Hit (Gagner) : --")
            self.lbl_win_double.setText("Double (Gagner) : --")

    def maj_comptage(self, running, true_count, cartes_restantes, total_cartes, avantage):
        self.lbl_running_count.setText(f"Running Count : {running:+d}")
        self.lbl_true_count.setText(f"True Count : {true_count:+.1f}")
        self.lbl_cartes_restantes.setText(
            f"Cartes : {cartes_restantes} / {total_cartes}"
        )

        self.lbl_avantage.setText(f"Avantage : {avantage:+.2f}%")

        # Change la couleur selon si l'avantage
        if avantage > 0:
            self.lbl_avantage.setStyleSheet("font-size: 14px; color: #51cf66; padding: 4px; font-weight: bold;")  # Vert
        else:
            self.lbl_avantage.setStyleSheet(
                "font-size: 14px; color: #ff6b6b; padding: 4px; font-weight: bold;")  # Rouge

    def activer_split(self, actif):
        self.btn_split.setEnabled(actif)

    def activer_double(self, actif):
        self.btn_double.setEnabled(actif)

    def _vider_layout(self, layout):
        while layout.count():
            item = layout.takeAt(0)
            w = item.widget()
            if w:
                w.deleteLater()
