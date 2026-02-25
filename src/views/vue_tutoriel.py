from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel,
                               QPushButton, QMessageBox)
from PySide6.QtCore import Signal, Qt

from src.views.widgets.carte_widget import CarteWidget
from src.views.widgets.table_fond import TableFond


class VueTutoriel(QWidget):
    quitter_clique = Signal()
    action_joueur = Signal(str)  # "hit", "stand", "double", "split"

    def __init__(self, parent=None):
        super().__init__(parent)
        self._setup_ui()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        self.table = TableFond()
        layout_table = QVBoxLayout(self.table)
        layout_table.setContentsMargins(20, 15, 20, 15)
        layout.addWidget(self.table)

        # Titre
        self.label_etape = QLabel("Tutoriel")
        self.label_etape.setAlignment(Qt.AlignCenter)
        self.label_etape.setStyleSheet(
            "font-size: 24px; font-weight: bold; color: #FFD700;"
        )
        layout_table.addWidget(self.label_etape)

        # Zone cartes dealer
        self.label_dealer = QLabel("Dealer")
        self.label_dealer.setAlignment(Qt.AlignCenter)
        self.label_dealer.setStyleSheet("font-size: 16px; color: white;")
        layout_table.addWidget(self.label_dealer)

        self.layout_cartes_dealer = QHBoxLayout()
        self.layout_cartes_dealer.setAlignment(Qt.AlignCenter)
        layout_table.addLayout(self.layout_cartes_dealer)

        # Message
        self.label_message = QLabel("")
        self.label_message.setAlignment(Qt.AlignCenter)
        self.label_message.setWordWrap(True)
        self.label_message.setStyleSheet(
            "font-size: 16px; color: white; background: rgba(0,0,0,120); "
            "border-radius: 10px; padding: 15px; margin: 10px;"
        )
        layout_table.addWidget(self.label_message)

        # Zone cartes joueur
        self.label_joueur = QLabel("Vous")
        self.label_joueur.setAlignment(Qt.AlignCenter)
        self.label_joueur.setStyleSheet("font-size: 16px; color: white;")
        layout_table.addWidget(self.label_joueur)

        self.layout_cartes_joueur = QHBoxLayout()
        self.layout_cartes_joueur.setAlignment(Qt.AlignCenter)
        layout_table.addLayout(self.layout_cartes_joueur)

        # Boutons actions
        self.widget_actions = QWidget()
        layout_actions = QHBoxLayout(self.widget_actions)
        layout_actions.setAlignment(Qt.AlignCenter)

        style_btn = """
            QPushButton {{
                background-color: {bg}; color: white;
                border: 2px solid #555; border-radius: 8px;
                font-size: 14px; font-weight: bold;
                padding: 8px 16px;
            }}
            QPushButton:hover {{ border-color: #FFD700; }}
            QPushButton:disabled {{ background-color: #333; color: #666; }}
        """

        self.btn_hit = QPushButton("Hit")
        self.btn_hit.setStyleSheet(style_btn.format(bg="#2E7D32"))
        self.btn_hit.clicked.connect(lambda: self.action_joueur.emit("hit"))
        layout_actions.addWidget(self.btn_hit)

        self.btn_stand = QPushButton("Stand")
        self.btn_stand.setStyleSheet(style_btn.format(bg="#C62828"))
        self.btn_stand.clicked.connect(lambda: self.action_joueur.emit("stand"))
        layout_actions.addWidget(self.btn_stand)

        self.btn_double = QPushButton("Double")
        self.btn_double.setStyleSheet(style_btn.format(bg="#D4A017"))
        self.btn_double.clicked.connect(lambda: self.action_joueur.emit("double"))
        layout_actions.addWidget(self.btn_double)

        self.btn_split = QPushButton("Split")
        self.btn_split.setStyleSheet(style_btn.format(bg="#7B2D8E"))
        self.btn_split.clicked.connect(lambda: self.action_joueur.emit("split"))
        layout_actions.addWidget(self.btn_split)

        layout_table.addWidget(self.widget_actions)

        # Bouton continuer + quitter
        layout_bas = QHBoxLayout()
        layout_bas.setAlignment(Qt.AlignCenter)

        self.btn_continuer = QPushButton("Continuer")
        self.btn_continuer.setStyleSheet(
            "font-size: 16px; background: #2d2d44; color: white; "
            "border: 2px solid #FFD700; border-radius: 8px; "
            "padding: 10px 30px; font-weight: bold;"
        )
        layout_bas.addWidget(self.btn_continuer)

        btn_quitter = QPushButton("Quitter le tutoriel")
        btn_quitter.setStyleSheet(
            "font-size: 14px; background: #8B0000; color: white; "
            "border-radius: 8px; padding: 8px 20px;"
        )
        btn_quitter.clicked.connect(self.quitter_clique.emit)
        layout_bas.addWidget(btn_quitter)

        layout_table.addLayout(layout_bas)

    def afficher_message(self, titre, message):
        self.label_etape.setText(titre)
        self.label_message.setText(message)

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

    def afficher_cartes_joueur(self, cartes):
        self._vider_layout(self.layout_cartes_joueur)
        for c in cartes:
            self.layout_cartes_joueur.addWidget(CarteWidget(c))

    def montrer_actions(self, visible, hit=True, stand=True, double=False, split=False):
        self.widget_actions.setVisible(visible)
        self.btn_hit.setEnabled(hit)
        self.btn_stand.setEnabled(stand)
        self.btn_double.setEnabled(double)
        self.btn_split.setEnabled(split)

    def _vider_layout(self, layout):
        while layout.count():
            item = layout.takeAt(0)
            w = item.widget()
            if w:
                w.deleteLater()
