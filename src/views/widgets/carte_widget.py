from PySide6.QtWidgets import QLabel
from PySide6.QtCore import Qt
from PySide6.QtGui import QPixmap


class CarteWidget(QLabel):
    LARGEUR = 120
    HAUTEUR = 180

    def __init__(self, carte=None, face_cachee=False, parent=None):
        super().__init__(parent)
        self.setFixedSize(self.LARGEUR, self.HAUTEUR)
        if face_cachee:
            self.afficher_dos()
        elif carte:
            self.afficher_carte(carte)

    def afficher_carte(self, carte):
        chemin = carte.get_image_path()
        pixmap = QPixmap(chemin)
        if not pixmap.isNull():
            pixmap = pixmap.scaled(self.LARGEUR, self.HAUTEUR,
                                   Qt.KeepAspectRatio, Qt.SmoothTransformation)
            self.setPixmap(pixmap)
        else:
            self.setText(str(carte))
            self.setAlignment(Qt.AlignCenter)
            self.setStyleSheet(
                "background: white; border: 2px solid #333; border-radius: 8px; "
                "font-size: 16px; font-weight: bold;"
            )

    def afficher_dos(self):
        self.setStyleSheet(
            "background-color: #8B0000; border-radius: 8px; "
            "border: 2px solid #FFD700;"
        )
        self.setText("")
