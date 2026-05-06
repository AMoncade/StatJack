import io

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QFrame,
    QToolButton, QDialog, QTextEdit, QSizePolicy
)
from PySide6.QtCore import Signal, Qt, QTimer
from PySide6.QtGui import QPixmap, QImage

from matplotlib.figure import Figure
from matplotlib.backends.backend_agg import FigureCanvasAgg

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
    miser_clique = Signal(int)
    prochaine_manche_clique = Signal()
    voir_graphe_clique = Signal()
    retour_menu_clique = Signal()
    parametres_clique = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.phase = PHASE_MISE
        self.cercle_actif = "Mise"
        self.aides_stats = {
            "bust": {
                "titre": "Bust",
                "texte": (
                    "Probabilité de dépasser 21 si une carte est tirée maintenant.\n\n"
                    "Plus ce pourcentage est élevé, plus tirer est risqué."
                ),
                "latex": r"P(\mathrm{bust})=\sum_{v:\,f(T,S,v)>21} p(v)",
                "legende": (
                    "T : total actuel du joueur\n\n"
                    "S : nombre d’as encore comptés comme 11\n\n"
                    "v : valeur d’une carte possible\n\n"
                    "p(v) : probabilité de tirer une carte de valeur v\n\n"
                    "f(T,S,v) : total obtenu après avoir tiré v, avec ajustement des as"
                )
            },

            "ameliorer": {
                "titre": "Améliorer la main",
                "texte": (
                    "Probabilité d’obtenir un total plus élevé que le total actuel "
                    "sans dépasser 21.\n\n"
                    "Cette statistique mesure le potentiel d’amélioration si une carte est tirée."
                ),
                "latex": r"P(\mathrm{ameliorer})=\sum_{v:\,T<f(T,S,v)\leq 21} p(v)",
                "legende": (
                    "T : total actuel du joueur\n\n"
                    "S : nombre d’as encore comptés comme 11\n\n"
                    "v : valeur d’une carte possible\n\n"
                    "p(v) : probabilité de tirer une carte de valeur v\n\n"
                    "f(T,S,v) : total obtenu après avoir tiré v, avec ajustement des as"
                )
            },

            "reco_ev": {
                "titre": "Reco HIT/STAND / EV",
                "texte": (
                    "Reco HIT/STAND : action recommandée entre rester et tirer.\n\n"
                    "EV stand : valeur attendue si la main reste telle quelle.\n"
                    "EV opt : meilleure valeur attendue possible entre rester "
                    "ou continuer à tirer de façon optimale.\n"
                    "Edge décision : écart entre la meilleure décision et le fait de rester."
                ),
                "latex": r"EV^*(T,S)=\max\left(EV_{\mathrm{stand}}(T),\sum_v p(v)\,EV^*(T_v,S_v)\right)",
                "legende": (
                    "EV* : meilleure valeur attendue possible depuis cet état\n\n"
                    "EV_stand(T) : valeur attendue si le joueur reste immédiatement\n\n"
                    "T : total actuel du joueur\n\n"
                    "S : nombre d’as encore comptés comme 11\n\n"
                    "v : valeur d’une carte possible\n\n"
                    "p(v) : probabilité de tirer une carte de valeur v\n\n"
                    "T_v : nouveau total après tirage de v\n\n"
                    "S_v : nouveau nombre d’as encore comptés comme 11 après tirage"
                )
            },

            "win_stand": {
                "titre": "Stand (Gagner)",
                "texte": (
                    "Pourcentage estimé de simulations Monte Carlo où l’action Stand "
                    "mène à une victoire.\n\n"
                    "Cela mesure une fréquence de victoire, pas une rentabilité moyenne."
                ),
                "latex": r"\hat{P}(\mathrm{victoire}\mid a)=\frac{\#\mathrm{victoires\ sous}\ a}{N}\times 100",
                "legende": (
                    "P̂ : probabilité estimée par simulation\n\n"
                    "a : action simulée, ici Stand\n\n"
                    "# victoires sous a : nombre de simulations gagnées avec cette action\n\n"
                    "N : nombre total de simulations"
                )
            },

            "win_hit": {
                "titre": "Hit (Gagner)",
                "texte": (
                    "Pourcentage estimé de simulations Monte Carlo où l’action Hit "
                    "mène à une victoire.\n\n"
                    "Cela mesure une fréquence de victoire, pas une valeur attendue."
                ),
                "latex": r"\hat{P}(\mathrm{victoire}\mid a)=\frac{\#\mathrm{victoires\ sous}\ a}{N}\times 100",
                "legende": (
                    "P̂ : probabilité estimée par simulation\n\n"
                    "a : action simulée, ici Hit\n\n"
                    "# victoires sous a : nombre de simulations gagnées avec cette action\n\n"
                    "N : nombre total de simulations"
                )
            },

            "win_double": {
                "titre": "Double (Gagner)",
                "texte": (
                    "Pourcentage estimé de simulations Monte Carlo où l’action Double "
                    "mène à une victoire.\n\n"
                    "Une action peut gagner moins souvent tout en ayant une meilleure EV."
                ),
                "latex": r"\hat{P}(\mathrm{victoire}\mid a)=\frac{\#\mathrm{victoires\ sous}\ a}{N}\times 100",
                "legende": (
                    "P̂ : probabilité estimée par simulation\n\n"
                    "a : action simulée, ici Double\n\n"
                    "# victoires sous a : nombre de simulations gagnées avec cette action\n\n"
                    "N : nombre total de simulations"
                )
            },

            "running_count": {
                "titre": "Running Count",
                "texte": (
                    "Le running count est le compteur brut des cartes vues.\n\n"
                    "Il augmente ou diminue selon les cartes sorties, sans tenir compte "
                    "du nombre de paquets restants."
                ),
                "latex": r"RC=\sum_{i=1}^{n} c_i",
                "legende": (
                    "RC : running count\n\n"
                    "i : indice d’une carte observée\n\n"
                    "n : nombre total de cartes observées\n\n"
                    "c_i : contribution de la iᵉ carte observée au count"
                )
            },

            "true_count": {
                "titre": "True Count",
                "texte": (
                    "Le true count est le running count ajusté selon le nombre de paquets restants.\n\n"
                    "Il donne une meilleure idée de si le sabot actuel avantage le joueur."
                ),
                "latex": r"TC=\frac{RC}{\mathrm{paquets\ restants}}",
                "legende": (
                    "TC : true count\n\n"
                    "RC : running count\n\n"
                    "paquets restants : estimation du nombre de paquets encore dans le sabot"
                )
            },

            "avantage": {
                "titre": "Avantage",
                "texte": (
                    "Estimation simplifiée de l’avantage du joueur à partir du true count.\n\n"
                    "Valeur positive : situation potentiellement favorable.\n"
                    "Valeur négative : situation plutôt défavorable."
                ),
                "latex": r"\mathrm{Avantage}=-0.5+0.5\cdot TC",
                "legende": (
                    "Avantage : estimation simplifiée de l’avantage du joueur, en pourcentage\n\n"
                    "TC : true count"
                )
            },

            "cartes": {
                "titre": "Cartes restantes",
                "texte": (
                    "Indique combien de cartes restent dans le sabot par rapport au total initial."
                ),
                "latex": r"N=\mathrm{cartes\ restantes}",
                "legende": (
                    "N : nombre de cartes restantes dans le sabot"
                )
            },
        }
        self._setup_ui()

    def _latex_vers_pixmap(self, latex, fontsize=16, text_color="white", bg_color="#16213e"):
        fig = Figure(figsize=(6, 1.2), dpi=150)
        fig.patch.set_facecolor(bg_color)

        canvas = FigureCanvasAgg(fig)
        ax = fig.add_subplot(111)
        ax.set_facecolor(bg_color)
        ax.axis("off")

        # Texte centré
        ax.text(
            0.5, 0.5,
            f"${latex}$",
            ha="center",
            va="center",
            fontsize=fontsize,
            color=text_color
        )

        # Ajuster automatiquement la taille
        fig.tight_layout(pad=0.4)

        buffer = io.BytesIO()
        canvas.print_png(buffer)
        buffer.seek(0)

        image = QImage.fromData(buffer.getvalue())
        return QPixmap.fromImage(image)

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
        self.label_dealer.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.label_dealer.setStyleSheet(
            "font-size: 18px; color: white; font-weight: bold;"
        )
        layout_table.addWidget(self.label_dealer)

        self.layout_cartes_dealer = QHBoxLayout()
        self.layout_cartes_dealer.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout_table.addLayout(self.layout_cartes_dealer)

        # Résultat (avec animation)
        self.label_resultat = QLabel("")
        self.label_resultat.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.label_resultat.setStyleSheet(
            "font-size: 26px; color: #FFD700; font-weight: bold; margin: 5px;"
        )
        layout_table.addWidget(self.label_resultat)

        # Zone cartes joueur
        self.label_joueur = QLabel("Vous")
        self.label_joueur.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.label_joueur.setStyleSheet(
            "font-size: 18px; color: white; font-weight: bold;"
        )
        layout_table.addWidget(self.label_joueur)

        self.layout_cartes_joueur = QHBoxLayout()
        self.layout_cartes_joueur.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout_table.addLayout(self.layout_cartes_joueur)

        # Indicateur main active
        self.label_main_active = QLabel("")
        self.label_main_active.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.label_main_active.setStyleSheet("font-size: 14px; color: #FFD700;")
        layout_table.addWidget(self.label_main_active)

        # Boutons actions (JEU)
        self.widget_actions = QWidget()
        layout_actions = QHBoxLayout(self.widget_actions)
        layout_actions.setAlignment(Qt.AlignmentFlag.AlignCenter)

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
        layout_post.setAlignment(Qt.AlignmentFlag.AlignCenter)

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
        layout_mises.setAlignment(Qt.AlignmentFlag.AlignCenter)

        lbl_mises = QLabel("Placez vos mises")
        lbl_mises.setAlignment(Qt.AlignmentFlag.AlignCenter)
        lbl_mises.setStyleSheet("font-size: 18px; color: white; font-weight: bold;")
        layout_mises.addWidget(lbl_mises)

        # Cercle Mise
        layout_cercle = QHBoxLayout()
        layout_cercle.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout_cercle.setSpacing(20)

        self.cercle_principale = CercleMise("Mise")
        self.cercle_principale.cercle_clique.connect(self._on_cercle_clique)
        layout_cercle.addWidget(self.cercle_principale)

        layout_mises.addLayout(layout_cercle)

        # 4 jetons
        layout_jetons = QHBoxLayout()
        layout_jetons.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout_jetons.setSpacing(10)

        for val in [100, 200, 500, 1000]:
            jeton = JetonWidget(val)
            jeton.jeton_clique.connect(self._on_jeton_clique)
            layout_jetons.addWidget(jeton)

        layout_mises.addLayout(layout_jetons)

        # Boutons dealer/reset
        layout_mise_btns = QHBoxLayout()
        layout_mise_btns.setAlignment(Qt.AlignmentFlag.AlignCenter)

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
        layout_sidebar.setAlignment(Qt.AlignmentFlag.AlignTop)

        ligne, self.lbl_true_count = self._creer_ligne_stat_avec_aide(
            "True Count : --", "true_count", "#FFD700"
        )
        layout_sidebar.addWidget(ligne)

        # Label pour l'avantage
        ligne, self.lbl_avantage = self._creer_ligne_stat_avec_aide(
            "Avantage : --", "avantage", "#AAA"
        )
        self.lbl_avantage.setStyleSheet(
            "font-size: 14px; color: #AAA; padding: 4px; font-weight: bold;"
        )
        layout_sidebar.addWidget(ligne)

        lbl_probas = QLabel("Probabilités")
        lbl_probas.setAlignment(Qt.AlignmentFlag.AlignCenter)
        lbl_probas.setStyleSheet(
            "font-size: 16px; font-weight: bold; color: white; padding: 8px;"
        )
        layout_sidebar.addWidget(lbl_probas)

        ligne, self.lbl_bust = self._creer_ligne_stat_avec_aide(
            "Bust : --", "bust", "#ff6b6b"
        )
        layout_sidebar.addWidget(ligne)

        ligne, self.lbl_ameliorer = self._creer_ligne_stat_avec_aide(
            "Améliorer la main : --", "ameliorer", "#51cf66"
        )
        layout_sidebar.addWidget(ligne)

        ligne, self.lbl_reco_ev = self._creer_ligne_stat_avec_aide(
            "Reco / EV : --", "reco_ev", "#ffffff"
        )
        layout_sidebar.addWidget(ligne)

        self.lbl_reco_ev.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignTop)
        self.lbl_reco_ev.setWordWrap(True)

        # % de victoire
        sep_stats = QFrame()
        sep_stats.setFrameShape(QFrame.Shape.HLine)
        sep_stats.setStyleSheet("color: #444;")
        layout_sidebar.addWidget(sep_stats)

        ligne, self.lbl_win_stand = self._creer_ligne_stat_avec_aide(
            "Stand (Gagner) : --", "win_stand", "#FFF"
        )
        layout_sidebar.addWidget(ligne)

        ligne, self.lbl_win_hit = self._creer_ligne_stat_avec_aide(
            "Hit (Gagner) : --", "win_hit", "#FFF"
        )
        layout_sidebar.addWidget(ligne)

        ligne, self.lbl_win_double = self._creer_ligne_stat_avec_aide(
            "Double (Gagner) : --", "win_double", "#FFF"
        )
        layout_sidebar.addWidget(ligne)

        ligne, self.lbl_running_count = self._creer_ligne_stat_avec_aide(
            "Running Count : --", "running_count", "#AAA"
        )
        layout_sidebar.addWidget(ligne)

        sep2 = QFrame()
        sep2.setFrameShape(QFrame.Shape.HLine)
        sep2.setStyleSheet("color: #444;")
        layout_sidebar.addWidget(sep2)

        ligne, self.lbl_cartes_restantes = self._creer_ligne_stat_avec_aide(
            "Cartes : --", "cartes", "#AAA"
        )
        layout_sidebar.addWidget(ligne)

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
        self.cercle_principale.ajouter_mise(valeur)

    def _reset_mises(self):
        self.cercle_principale.reset()
        self.cercle_actif = "Mise"

    def _on_distribuer(self):
        principale = self.cercle_principale.mise
        if principale <= 0:
            return
        self.miser_clique.emit(principale)

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
                    w.setStyleSheet(w.styleSheet() + "border: 4px solid #FFD700;")
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

    def _creer_ligne_stat_avec_aide(self, texte_label, cle_aide, couleur_label="#FFF"):
        container = QWidget()
        layout = QHBoxLayout(container)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(6)

        label = QLabel(texte_label)
        label.setStyleSheet(f"font-size: 14px; color: {couleur_label}; padding: 4px;")
        label.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
        layout.addWidget(label)

        layout.addStretch()

        btn_aide = QToolButton()
        btn_aide.setText("?")
        btn_aide.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_aide.setFixedSize(18, 18)
        btn_aide.setStyleSheet("""
            QToolButton {
                background-color: #2d2d44;
                color: #FFD700;
                border: 1px solid #555;
                border-radius: 9px;
                font-size: 11px;
                font-weight: bold;
            }
            QToolButton:hover {
                border-color: #FFD700;
                background-color: #3d3d5c;
            }
        """)
        btn_aide.clicked.connect(lambda _, key=cle_aide: self._ouvrir_aide_stat(key))
        layout.addWidget(btn_aide)

        return container, label

    def _ouvrir_aide_stat(self, cle_aide):
        aide = self.aides_stats.get(cle_aide)

        if not aide:
            titre = "Aide"
            texte = "Aucune explication disponible pour cette statistique."
            latex = None
            legende = "Aucune légende disponible."
        else:
            titre = aide.get("titre", "Aide")
            texte = aide.get("texte", "")
            latex = aide.get("latex")
            legende = aide.get("legende", "Aucune légende disponible.")

        dialog = QDialog(self)
        dialog.setWindowTitle(titre)
        dialog.setModal(True)
        dialog.setMinimumWidth(520)
        dialog.setWindowFlags(
            Qt.WindowType.Dialog |
            Qt.WindowType.WindowTitleHint |
            Qt.WindowType.CustomizeWindowHint |
            Qt.WindowType.WindowCloseButtonHint
        )

        dialog.setStyleSheet("""
            QDialog {
                background-color: #1a1a2e;
                color: white;
            }
            QLabel {
                color: white;
            }
            QTextEdit {
                background-color: #16213e;
                color: white;
                border: 1px solid #444;
                border-radius: 8px;
                padding: 8px;
                font-size: 13px;
            }
            QPushButton {
                background-color: #2d2d44;
                color: white;
                border: 2px solid #555;
                border-radius: 8px;
                padding: 8px 16px;
                font-weight: bold;
            }
            QPushButton:hover {
                border-color: #FFD700;
            }
        """)

        layout = QVBoxLayout(dialog)
        layout.setSpacing(12)

        lbl_titre = QLabel(titre)
        lbl_titre.setStyleSheet("font-size: 18px; font-weight: bold; color: #FFD700;")
        lbl_titre.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(lbl_titre)

        if latex:
            formule_frame = QFrame()
            formule_frame.setStyleSheet("""
                QFrame {
                    background-color: #16213e;
                    border: 1px solid #444;
                    border-radius: 8px;
                }
            """)
            formule_layout = QVBoxLayout(formule_frame)
            formule_layout.setContentsMargins(10, 10, 10, 10)

            lbl_formule_titre = QLabel("Formule")
            lbl_formule_titre.setStyleSheet(
                "font-size: 13px; font-weight: bold; color: #FFD700;"
            )
            formule_layout.addWidget(lbl_formule_titre)

            lbl_formule = QLabel()
            lbl_formule.setAlignment(Qt.AlignmentFlag.AlignCenter)
            lbl_formule.setSizePolicy(
                QSizePolicy.Policy.Expanding,
                QSizePolicy.Policy.Fixed
            )

            pixmap = self._latex_vers_pixmap(latex)
            lbl_formule.setPixmap(pixmap)
            formule_layout.addWidget(lbl_formule)

            layout.addWidget(formule_frame)

        # ---- LÉGENDE COLLAPSIBLE ----
        btn_legende = QPushButton("▸ Voir la légende")
        btn_legende.setCheckable(True)
        btn_legende.setChecked(False)
        btn_legende.setStyleSheet("""
            QPushButton {
                background-color: #2d2d44;
                color: white;
                border: 2px solid #555;
                border-radius: 8px;
                padding: 8px 12px;
                font-weight: bold;
                text-align: left;
            }
            QPushButton:hover {
                border-color: #FFD700;
            }
        """)
        layout.addWidget(btn_legende)

        legende_frame = QFrame()
        legende_frame.setVisible(False)
        legende_frame.setStyleSheet("""
            QFrame {
                background-color: #16213e;
                border: 1px solid #444;
                border-radius: 8px;
            }
        """)
        layout_legende = QVBoxLayout(legende_frame)
        layout_legende.setContentsMargins(10, 10, 10, 10)

        lbl_legende = QLabel("Légende des variables")
        lbl_legende.setStyleSheet(
            "font-size: 13px; font-weight: bold; color: #FFD700;"
        )
        layout_legende.addWidget(lbl_legende)

        txt_legende = QTextEdit()
        txt_legende.setReadOnly(True)
        txt_legende.setPlainText(legende)
        txt_legende.setMaximumHeight(132 if len(legende) < 180 else 180)
        layout_legende.addWidget(txt_legende)

        layout.addWidget(legende_frame)

        def toggle_legende(checked):
            legende_frame.setVisible(checked)
            btn_legende.setText(
                "▾ Masquer la légende" if checked else "▸ Voir la légende"
            )
            dialog.adjustSize()

        btn_legende.toggled.connect(toggle_legende)

        lbl_explication = QLabel("Explication")
        lbl_explication.setStyleSheet(
            "font-size: 13px; font-weight: bold; color: #FFD700;"
        )
        layout.addWidget(lbl_explication)

        txt = QTextEdit()
        txt.setReadOnly(True)
        txt.setPlainText(texte)
        txt.setMinimumHeight(180)
        layout.addWidget(txt)

        btn_fermer = QPushButton("Fermer")
        btn_fermer.clicked.connect(dialog.accept)

        ligne_btn = QHBoxLayout()
        ligne_btn.addStretch()
        ligne_btn.addWidget(btn_fermer)
        layout.addLayout(ligne_btn)

        dialog.exec()

    def maj_probabilites(self, pct_bust, edge_pct, pct_ameliorer=0.0, stats_actions=None):
        # Bust %
        self.lbl_bust.setText(f"Bust : {pct_bust:.1f}%")
        # Améliorer la main si hit
        self.lbl_ameliorer.setText(f"Améliorer la main : {pct_ameliorer:.1f}%")

        # ---- Couleur Bust ----
        if pct_bust > 50:
            self.lbl_bust.setStyleSheet(
                "font-size: 14px; color: #ff0000; padding: 4px;"
            )
        elif pct_bust > 25:
            self.lbl_bust.setStyleSheet(
                "font-size: 14px; color: #ff6b6b; padding: 4px;"
            )
        else:
            self.lbl_bust.setStyleSheet(
                "font-size: 14px; color: #ffd93d; padding: 4px;"
            )

        # ----- Couleur Amélioration -----
        if pct_ameliorer >= 50:
            self.lbl_ameliorer.setStyleSheet(
                "font-size: 14px; color: #00c853; padding: 4px;"
            )
        elif pct_ameliorer >= 25:
            self.lbl_ameliorer.setStyleSheet(
                "font-size: 14px; color: #51cf66; padding: 4px;"
            )
        else:
            self.lbl_ameliorer.setStyleSheet(
                "font-size: 14px; color: #ffffff; padding: 4px;"
            )

        # ----- Couleur Reco / EV -----
        if edge_pct > 0:
            self.lbl_reco_ev.setStyleSheet(
                "font-size: 14px; color: #00c853; padding: 4px;"
            )
        elif edge_pct < 0:
            self.lbl_reco_ev.setStyleSheet(
                "font-size: 14px; color: #ff5252; padding: 4px;"
            )
        else:
            self.lbl_reco_ev.setStyleSheet(
                "font-size: 14px; color: #ffffff; padding: 4px;"
            )

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
            self.lbl_win_double.setStyleSheet("font-size: 14px; color: #555; padding: 4px;")

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
