from PySide6.QtWidgets import QWidget
from PySide6.QtGui import QPainter, QLinearGradient, QColor


class TableFond(QWidget):

    def __init__(self, parent=None):
        super().__init__(parent)

    def paintEvent(self, event):
        painter = QPainter(self)
        gradient = QLinearGradient(0, 0, 0, self.height())
        gradient.setColorAt(0.0, QColor(20, 80, 40))
        gradient.setColorAt(0.5, QColor(30, 110, 55))
        gradient.setColorAt(1.0, QColor(15, 65, 30))
        painter.fillRect(self.rect(), gradient)
