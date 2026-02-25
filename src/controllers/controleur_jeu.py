from src.models.jeu import Jeu
from src.models.probabilites import CalculateurProbabilites
from src.views.vue_jeu import VueJeu, PHASE_MISE, PHASE_JEU, PHASE_RESULTAT
from src.views.widgets.graphe_simulation import GrapheSimulation


class ControleurJeu:

    def __init__(self, vue: VueJeu, jeu: Jeu, audio_manager):
        self.vue = vue
        self.jeu = jeu
        self.audio = audio_manager

        self.vue.hit_clique.connect(self.action_hit)
        self.vue.stand_clique.connect(self.action_stand)
        self.vue.double_clique.connect(self.action_double)
        self.vue.split_clique.connect(self.action_split)
        self.vue.miser_clique.connect(self.action_miser)
        self.vue.prochaine_manche_clique.connect(self.prochaine_manche)
        self.vue.voir_graphe_clique.connect(self.voir_graphe)

    def action_miser(self, principale):
        if self.jeu.manche_en_cours:
            return
        if not self.jeu.placer_mises(principale):
            self.vue.label_resultat.setText("Fonds insuffisants !")
            return
        self.jeu.demarrer_manche()
        self.audio.jouer_son_carte()
        self.vue.set_phase(PHASE_JEU)
        self._rafraichir(reveler=False)

        self._verifier_blackjack()

    def _verifier_blackjack(self):
        main = self.jeu.joueur
        if main.est_blackjack():
            self._finir_manche()

    def action_hit(self):
        self.jeu.joueur_tire()
        self.audio.jouer_son_carte()
        self._rafraichir(reveler=False)
        if self.jeu.joueur.est_busted():
            if not self.jeu.passer_main_suivante():
                self._finir_manche()
            else:
                self._rafraichir(reveler=False)

    def action_stand(self):
        if not self.jeu.passer_main_suivante():
            self._finir_manche()
        else:
            self._rafraichir(reveler=False)

    def action_double(self):
        if not self.jeu.joueur.peut_double():
            return
        carte = self.jeu.joueur_double()
        if carte is None:
            return
        self.audio.jouer_son_carte()
        self._rafraichir(reveler=False)
        if self.jeu.joueur.est_busted():
            if not self.jeu.passer_main_suivante():
                self._finir_manche()
            else:
                self._rafraichir(reveler=False)
        else:
            self.action_stand()

    def action_split(self):
        if not self.jeu.joueur.peut_split():
            return
        if not self.jeu.joueur_split():
            return
        self.audio.jouer_son_carte()
        self._rafraichir(reveler=False)

    def _finir_manche(self):
        resultats = self.jeu.calculer_resultats()
        self.vue.set_phase(PHASE_RESULTAT)
        self._rafraichir(reveler=True)

        # Animation et son selon résultat
        a_gagne = any("Gagné" in r or "Blackjack" in r for r in resultats)
        a_perdu = any("Perdu" in r or "Bust" in r for r in resultats)
        egalite = all("Égalité" in r for r in resultats)

        if egalite:
            self.vue.animer_egalite()
        elif a_gagne and not a_perdu:
            self.vue.animer_victoire()
            self.audio.jouer_son_victoire()
        elif a_perdu and not a_gagne:
            self.vue.animer_defaite()
            self.audio.jouer_son_defaite()
        elif a_gagne:
            self.vue.animer_victoire()
            self.audio.jouer_son_victoire()
        else:
            self.vue.animer_defaite()
            self.audio.jouer_son_defaite()

    def prochaine_manche(self):
        self.vue.set_phase(PHASE_MISE)
        self.vue.label_resultat.setText("")
        self.vue._reset_mises()
        self._vider_cartes()
        self._rafraichir_argent()

    def voir_graphe(self):
        dialog = GrapheSimulation(self.jeu.sabot, self.vue)
        dialog.exec()

    def _rafraichir(self, reveler):
        self.vue.afficher_cartes_dealer(self.jeu.dealer.cartes, reveler=reveler)
        self.vue.afficher_cartes_joueur(
            self.jeu.mains_joueur, self.jeu.index_main_active
        )
        self.vue.afficher_infos_dealer(self.jeu.dealer, reveler=reveler)
        self.vue.afficher_infos_joueur(self.jeu.joueur)
        self._rafraichir_argent()

        # Probabilites
        if not reveler:
            pct_bust = CalculateurProbabilites.probabilite_bust(
                self.jeu.joueur, self.jeu.sabot) * 100
            pct_am = CalculateurProbabilites.probabilite_ameliorer(
                self.jeu.joueur, self.jeu.sabot) * 100
            self.vue.maj_probabilites(pct_bust, pct_am)
        else:
            self.vue.maj_probabilites(0, 0)
            self.vue.lbl_bust.setText("Bust : --")
            self.vue.lbl_ameliorer.setText("Améliorer (17-21) : --")

        # Comptage
        sabot = self.jeu.sabot
        total = sabot.nb_paquets * 52
        self.vue.maj_comptage(
            sabot.running_count,
            sabot.true_count(),
            sabot.cartes_restantes(),
            total,
        )

        # Boutons contextuels
        if not reveler:
            self.vue.activer_split(self.jeu.joueur.peut_split())
            self.vue.activer_double(self.jeu.joueur.peut_double())

    def _rafraichir_argent(self):
        if self.jeu.banque:
            self.vue.afficher_argent(self.jeu.banque.solde)

    def _vider_cartes(self):
        self.vue._vider_layout(self.vue.layout_cartes_dealer)
        self.vue._vider_layout(self.vue.layout_cartes_joueur)
        self.vue.label_dealer.setText("Dealer")
        self.vue.label_joueur.setText("Vous")
        self.vue.label_main_active.setText("")
