from PySide6.QtWidgets import (QWidget, QVBoxLayout, QLabel, QPushButton,
                               QCheckBox, QSpinBox, QHBoxLayout, QMessageBox)
from PySide6.QtCore import Signal, Qt


class VueParametres(QWidget):
    retour_clique = Signal()

    def __init__(self, settings, banque, audio_manager, parent=None):
        super().__init__(parent)
        self.settings = settings
        self.banque = banque
        self.audio_manager = audio_manager

        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignCenter)
        layout.setSpacing(15)

        titre = QLabel("Paramètres")
        titre.setAlignment(Qt.AlignCenter)
        titre.setStyleSheet("font-size: 32px; font-weight: bold; color: #FFD700;")
        layout.addWidget(titre)

        layout.addSpacing(20)

        style_label = "font-size: 16px; color: white;"
        style_check = "font-size: 16px; color: white; spacing: 10px;"

        self.check_musique = QCheckBox("Musique de fond")
        self.check_musique.setStyleSheet(style_check)
        self.check_musique.setChecked(settings.get("musique"))
        self.check_musique.toggled.connect(self.audio_manager.toggle_musique)
        layout.addWidget(self.check_musique, alignment=Qt.AlignCenter)

        self.check_sons = QCheckBox("Effets sonores")
        self.check_sons.setStyleSheet(style_check)
        self.check_sons.setChecked(settings.get("sons"))
        self.check_sons.toggled.connect(self.audio_manager.toggle_sons)
        layout.addWidget(self.check_sons, alignment=Qt.AlignCenter)

        layout.addSpacing(10)

        row_paquets = QHBoxLayout()
        row_paquets.setAlignment(Qt.AlignCenter)
        lbl_paquets = QLabel("Nombre de paquets :")
        lbl_paquets.setStyleSheet(style_label)
        row_paquets.addWidget(lbl_paquets)

        self.spin_paquets = QSpinBox()
        self.spin_paquets.setRange(1, 8)
        self.spin_paquets.setValue(settings.get("nb_paquets"))
        self.spin_paquets.setStyleSheet(
            "font-size: 16px; padding: 5px; min-width: 60px; "
            "background: #2d2d44; color: white; border: 1px solid #555;"
        )
        self.spin_paquets.valueChanged.connect(
            lambda v: self.settings.set("nb_paquets", v)
        )
        row_paquets.addWidget(self.spin_paquets)
        layout.addLayout(row_paquets)

        layout.addSpacing(20)

        style_btn = """
            QPushButton {
                background-color: #2d2d44; color: white;
                border: 2px solid #555; border-radius: 10px;
                font-size: 16px; font-weight: bold;
                padding: 10px 30px; min-width: 200px;
            }
            QPushButton:hover { background-color: #3d3d5c; border-color: #FFD700; }
        """

        btn_reset = QPushButton("Réinitialiser l'argent ($10 000)")
        btn_reset.setStyleSheet(style_btn.replace("#2d2d44", "#8B0000"))
        btn_reset.clicked.connect(self._reset_argent)
        layout.addWidget(btn_reset, alignment=Qt.AlignCenter)

        layout.addSpacing(10)

        btn_retour = QPushButton("Retour")
        btn_retour.setStyleSheet(style_btn)
        btn_retour.clicked.connect(self.retour_clique.emit)
        layout.addWidget(btn_retour, alignment=Qt.AlignCenter)

    def _reset_argent(self):
        reponse = QMessageBox.question(
            self, "Confirmer",
            "Réinitialiser le solde à $10 000 ?",
            QMessageBox.Yes | QMessageBox.No
        )
        if reponse == QMessageBox.Yes:
            self.banque.reset()
