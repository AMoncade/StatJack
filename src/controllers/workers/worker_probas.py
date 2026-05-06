import copy

from PySide6.QtCore import QThread, Signal

from src.models.probabilites import CalculateurProbabilites


class WorkerProbas(QThread):
    termine = Signal(int, dict)
    erreur = Signal(int, str)

    def __init__(self, id_calcul, main_joueur, dealer, sabot, parent=None):
        super().__init__(parent)
        self.id_calcul = id_calcul

        # Copies indépendantes pour éviter que le jeu change pendant le calcul
        self.main_joueur = copy.deepcopy(main_joueur)
        self.dealer = copy.deepcopy(dealer)
        self.sabot = sabot.clone()

    def run(self):
        try:
            if not self.dealer.cartes or not self.main_joueur.cartes:
                self.termine.emit(self.id_calcul, {})
                return

            dealer_upcard = self.dealer.cartes[0]
            dealer_hole_card = (
                self.dealer.cartes[1]
                if len(self.dealer.cartes) >= 2
                else None
            )

            spot = CalculateurProbabilites.resume_spot(
                main_joueur=self.main_joueur,
                dealer_upcard=dealer_upcard,
                sabot=self.sabot,
                nb_simulations_dealer=5000,
                dealer_hole_card=dealer_hole_card,
            )

            stats_action = CalculateurProbabilites.simuler_monte_carlo(
                main_joueur=self.main_joueur,
                dealer=self.dealer,
                sabot=self.sabot,
                nb_simulations=500,
                dealer_hole_card=dealer_hole_card,
            )

            self.termine.emit(self.id_calcul, {
                "spot": spot,
                "stats_action": stats_action,
            })

        except Exception as e:
            self.erreur.emit(self.id_calcul, str(e))