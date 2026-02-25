from PySide6.QtWidgets import QFrame, QLabel, QVBoxLayout
from PySide6.QtCore import Qt, Signal


class CercleMise(QFrame):
    cercle_clique = Signal(str)

    def __init__(self, nom, parent=None):
        super().__init__(parent)
        self.nom = nom
        self.mise = 0
        self.setFixedSize(90, 90)
        self.setCursor(Qt.PointingHandCursor)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        self.label_nom = QLabel(nom)
        self.label_nom.setAlignment(Qt.AlignCenter)
        self.label_nom.setStyleSheet("color: #FFD700; font-size: 10px; font-weight: bold;")
        layout.addWidget(self.label_nom)

        self.label_mise = QLabel("$0")
        self.label_mise.setAlignment(Qt.AlignCenter)
        self.label_mise.setStyleSheet("color: white; font-size: 14px; font-weight: bold;")
        layout.addWidget(self.label_mise)

        self._mettre_a_jour_style()

    def _mettre_a_jour_style(self):
        bordure = "#FFD700" if self.mise > 0 else "#888"
        self.setStyleSheet(f"""
            CercleMise {{
                background-color: rgba(0, 0, 0, 100);
                border: 3px solid {bordure};
                border-radius: 45px;
            }}
        """)

    def set_mise(self, montant):
        self.mise = montant
        self.label_mise.setText(f"${montant}" if montant > 0 else "$0")
        self._mettre_a_jour_style()

    def ajouter_mise(self, montant):
        self.mise += montant
        self.set_mise(self.mise)

    def reset(self):
        self.set_mise(0)

    def mousePressEvent(self, event):
        self.cercle_clique.emit(self.nom)
        super().mousePressEvent(event)
