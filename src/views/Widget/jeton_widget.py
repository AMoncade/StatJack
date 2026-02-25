from PySide6.QtWidgets import QPushButton
from PySide6.QtCore import Signal


COULEURS_JETONS = {
    100: ("#FFFFFF", "#333333"),
    200: ("#FF4444", "#FFFFFF"),
    500: ("#4444FF", "#FFFFFF"),
    1000: ("#FFD700", "#333333"),
}


class JetonWidget(QPushButton):
    jeton_clique = Signal(int)

    def __init__(self, valeur, parent=None):
        super().__init__(parent)
        self.valeur = valeur
        self.setFixedSize(70, 70)
        bg, fg = COULEURS_JETONS.get(valeur, ("#888", "#FFF"))
        self.setText(f"${valeur}")
        self.setStyleSheet(f"""
            QPushButton {{
                background-color: {bg};
                color: {fg};
                border: 3px solid #333;
                border-radius: 35px;
                font-size: 13px;
                font-weight: bold;
            }}
            QPushButton:hover {{
                border: 3px solid #FFD700;
            }}
            QPushButton:pressed {{
                background-color: #555;
            }}
        """)
        self.clicked.connect(lambda: self.jeton_clique.emit(self.valeur))
