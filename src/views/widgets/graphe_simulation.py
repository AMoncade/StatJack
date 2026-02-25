from PySide6.QtWidgets import QDialog, QVBoxLayout
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg
from matplotlib.figure import Figure

from src.models.probabilites import CalculateurProbabilites


class GrapheSimulation(QDialog):

    def __init__(self, sabot, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Simulation Monte Carlo — Loi des grands nombres")
        self.resize(700, 450)

        layout = QVBoxLayout(self)
        fig = Figure(figsize=(7, 4), facecolor="#1a1a2e")
        canvas = FigureCanvasQTAgg(fig)
        layout.addWidget(canvas)

        gains = CalculateurProbabilites.simuler_mains(sabot, nb_simulations=1000)

        ax = fig.add_subplot(111)
        ax.set_facecolor("#1a1a2e")
        ax.plot(range(1, len(gains) + 1), gains, color="#51cf66", linewidth=1)
        ax.axhline(y=0, color="#ff6b6b", linestyle="--", linewidth=0.8)
        ax.set_xlabel("Nombre de mains", color="white")
        ax.set_ylabel("Gain moyen (unités de mise)", color="white")
        ax.set_title("Convergence du gain moyen", color="white", fontsize=13)
        ax.tick_params(colors="white")
        for spine in ax.spines.values():
            spine.set_color("#444")

        fig.tight_layout()
        canvas.draw()
