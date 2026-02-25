from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QPushButton, QHBoxLayout
from PySide6.QtCore import Signal, Qt


class MenuPrincipal(QWidget):
    jouer_clique = Signal()
    tutoriel_clique = Signal()
    parametres_clique = Signal()
    quitter_clique = Signal()

    def __init__(self, banque, parent=None):
        super().__init__(parent)
        self.banque = banque

        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignCenter)
        layout.setSpacing(20)

        self.label_titre = QLabel("Stats Jack")
        self.label_titre.setAlignment(Qt.AlignCenter)
        self.label_titre.setStyleSheet(
            "font-size: 52px; font-weight: bold; color: #FFD700; "
            "font-family: 'Georgia'; letter-spacing: 4px;"
        )
        layout.addWidget(self.label_titre)

        self.label_sous_titre = QLabel("Le Laboratoire de Blackjack")
        self.label_sous_titre.setAlignment(Qt.AlignCenter)
        self.label_sous_titre.setStyleSheet(
            "font-size: 18px; color: #AAA; font-style: italic;"
        )
        layout.addWidget(self.label_sous_titre)

        self.label_argent = QLabel()
        self.label_argent.setAlignment(Qt.AlignCenter)
        self.label_argent.setStyleSheet(
            "font-size: 22px; color: #51cf66; font-weight: bold; margin: 10px;"
        )
        layout.addWidget(self.label_argent)

        layout.addSpacing(20)

        style_btn = """
            QPushButton {
                background-color: #2d2d44;
                color: white;
                border: 2px solid #555;
                border-radius: 12px;
                font-size: 18px;
                font-weight: bold;
                padding: 14px 40px;
                min-width: 250px;
            }
            QPushButton:hover {
                background-color: #3d3d5c;
                border-color: #FFD700;
            }
        """

        boutons = [
            ("Tutoriel", self.tutoriel_clique),
            ("Jouer", self.jouer_clique),
            ("Paramètres", self.parametres_clique),
            ("Quitter", self.quitter_clique),
        ]

        for texte, signal in boutons:
            btn = QPushButton(texte)
            btn.setStyleSheet(style_btn)
            btn.clicked.connect(signal.emit)
            layout.addWidget(btn, alignment=Qt.AlignCenter)

        self.rafraichir_argent()

    def rafraichir_argent(self):
        self.label_argent.setText(f"Solde : ${self.banque.solde}")
