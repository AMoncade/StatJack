from src.models.carte import Carte
from src.models.main_joueur import MainJoueur
from src.views.vue_tutoriel import VueTutoriel


ETAPES = [
    {
        "titre": "Étape 1 — Bienvenue",
        "message": (
            "Bienvenue dans le tutoriel de Stats Jack !\n\n"
            "Le Blackjack est un jeu de cartes où le but est de se rapprocher "
            "de 21 sans dépasser. Vous jouez contre le dealer.\n\n"
            "Cliquez sur Continuer pour commencer."
        ),
        "cartes_joueur": [],
        "cartes_dealer": [],
        "actions": False,
    },
    {
        "titre": "Étape 2 — La valeur des cartes",
        "message": (
            "Les cartes 2 à 10 valent leur valeur numérique.\n"
            "Les figures (J, Q, K) valent 10.\n"
            "L'As vaut 11, mais peut devenir 1 si vous dépassez 21.\n\n"
            "Ici, votre main vaut : 10 + 8 = 18"
        ),
        "cartes_joueur": [("K", "♠️"), ("8", "❤️")],
        "cartes_dealer": [("7", "♣️"), ("?", None)],
        "actions": False,
    },
    {
        "titre": "Étape 3 — Hit ou Stand ?",
        "message": (
            "Hit = tirer une carte supplémentaire.\n"
            "Stand = garder votre main actuelle.\n\n"
            "Vous avez 12. Le dealer montre un 10.\n"
            "Essayez de cliquer Hit pour tirer une carte !"
        ),
        "cartes_joueur": [("5", "♦️"), ("7", "♣️")],
        "cartes_dealer": [("10", "♠️"), ("?", None)],
        "actions": True,
        "actions_config": {"hit": True, "stand": True, "double": False, "split": False},
        "attendre_action": "hit",
    },
    {
        "titre": "Étape 4 — Le Double",
        "message": (
            "Le Double permet de doubler votre mise en échange d'une seule carte.\n"
            "C'est avantageux quand vous avez 10 ou 11 et que le dealer a une carte faible.\n\n"
            "Ici vous avez 11, essayez Double !"
        ),
        "cartes_joueur": [("5", "♦️"), ("6", "❤️")],
        "cartes_dealer": [("6", "♣️"), ("?", None)],
        "actions": True,
        "actions_config": {"hit": False, "stand": False, "double": True, "split": False},
        "attendre_action": "double",
    },
    {
        "titre": "Étape 5 — Le Split",
        "message": (
            "Si vos deux premières cartes ont la même valeur, vous pouvez les séparer "
            "en deux mains distinctes (Split).\n"
            "Chaque main reçoit ensuite une nouvelle carte.\n\n"
            "Ici vous avez deux 8, essayez Split !"
        ),
        "cartes_joueur": [("8", "♠️"), ("8", "❤️")],
        "cartes_dealer": [("5", "♦️"), ("?", None)],
        "actions": True,
        "actions_config": {"hit": False, "stand": False, "double": False, "split": True},
        "attendre_action": "split",
    },
    {
        "titre": "Étape 6 — Félicitations !",
        "message": (
            "Vous maîtrisez les bases du Blackjack !\n\n"
            "N'oubliez pas :\n"
            "• Consultez les probabilités dans la barre latérale pendant le jeu\n"
            "• Le True Count vous aide à évaluer l'avantage\n"
            "• Les side bets (PP, 21+3) ajoutent du piment\n\n"
            "Retournez au menu et lancez une partie !"
        ),
        "cartes_joueur": [],
        "cartes_dealer": [],
        "actions": False,
    },
]


class ControleurTutoriel:

    def __init__(self, vue: VueTutoriel):
        self.vue = vue
        self.etape_courante = 0

        self.vue.btn_continuer.clicked.connect(self._etape_suivante)
        self.vue.action_joueur.connect(self._on_action)

    def demarrer(self):
        self.etape_courante = 0
        self._afficher_etape()

    def _afficher_etape(self):
        if self.etape_courante >= len(ETAPES):
            self.vue.quitter_clique.emit()
            return

        etape = ETAPES[self.etape_courante]
        self.vue.afficher_message(etape["titre"], etape["message"])

        # Cartes joueur
        cartes_j = []
        for rang, couleur in etape.get("cartes_joueur", []):
            if rang != "?":
                cartes_j.append(Carte(rang, couleur))
        self.vue.afficher_cartes_joueur(cartes_j)

        # Cartes dealer
        cartes_d = []
        reveler = True
        for rang, couleur in etape.get("cartes_dealer", []):
            if rang == "?":
                reveler = False
            else:
                cartes_d.append(Carte(rang, couleur))
        if cartes_d:
            if not reveler:
                cartes_d.append(Carte("2", "♣️"))  # carte cachee
            self.vue.afficher_cartes_dealer(cartes_d, reveler=reveler)
        else:
            self.vue.afficher_cartes_dealer([], reveler=True)

        # Actions
        if etape.get("actions"):
            cfg = etape.get("actions_config", {})
            self.vue.montrer_actions(
                True,
                hit=cfg.get("hit", True),
                stand=cfg.get("stand", True),
                double=cfg.get("double", False),
                split=cfg.get("split", False),
            )
            self.vue.btn_continuer.setVisible(False)
        else:
            self.vue.montrer_actions(False)
            self.vue.btn_continuer.setVisible(True)

    def _etape_suivante(self):
        self.etape_courante += 1
        self._afficher_etape()

    def _on_action(self, action):
        etape = ETAPES[self.etape_courante]
        attendu = etape.get("attendre_action")
        if attendu and action == attendu:
            self.vue.montrer_actions(False)
            self.vue.btn_continuer.setVisible(True)
            self.vue.afficher_message(
                etape["titre"],
                etape["message"] + "\n\nBravo ! Cliquez Continuer."
            )
