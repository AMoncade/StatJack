from PySide6.QtGui import QIcon
from PySide6.QtWidgets import QMainWindow, QStackedWidget


PAGE_MENU = 0
PAGE_JEU = 1
PAGE_PARAMETRES = 2
PAGE_TUTORIEL = 3


class AppWindow(QMainWindow):

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Stats Jack — Le Laboratoire de Blackjack")
        self.resize(1200, 800)
        self.logo = QIcon("logo/SJlogo.png")
        self.setWindowIcon(self.logo)
        self.stack = QStackedWidget()
        self.setCentralWidget(self.stack)

    def ajouter_page(self, widget):
        self.stack.addWidget(widget)

    def aller_a(self, index):
        self.stack.setCurrentIndex(index)

    def closeEvent(self, event):
        if hasattr(self, "audio_manager") and self.audio_manager:
            self.audio_manager.cleanup()
        super().closeEvent(event)
