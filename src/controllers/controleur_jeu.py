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
            # main active (si split)
            try:
                main_active = self.jeu.mains_joueur[self.jeu.index_main_active]
            except Exception:
                main_active = self.jeu.joueur  # fallback

            dealer_upcard = self.jeu.dealer.cartes[0] if self.jeu.dealer.cartes else None

            if dealer_upcard is None:
                self.vue.maj_probabilites(0, 0)
                self.vue.lbl_bust.setText("Bust : --")
                self.vue.lbl_ameliorer.setText("Recommendation / EV : --")
            else:
                try:
                    spot = CalculateurProbabilites.resume_spot(
                        main_joueur=main_active,
                        dealer_upcard=dealer_upcard,
                        sabot=self.jeu.sabot,
                        nb_simulations_dealer=5000
                    )

                    pct_bust = spot.get("p_bust_si_hit", 0.0) * 100.0

                    reco = spot.get("recommandation", "--")
                    ev_stand = spot.get("ev_stand", 0.0)

                    # NOTE: dans ton module actuel, "ev_hit_1x" = EV optimal (hit récursif vs stand)
                    ev_opt = spot.get("ev_hit_1x", 0.0)

                    edge_pct = (ev_opt - ev_stand) * 100.0

                    # On conserve la signature existante (2 nombres)
                    self.vue.maj_probabilites(pct_bust, edge_pct)

                    self.vue.lbl_bust.setText(f"Bust : {pct_bust:.1f}%")
                    self.vue.lbl_ameliorer.setText(
                        f"Reco : {reco} | EV stand : {ev_stand:+.3f} | EV opt : {ev_opt:+.3f}"
                    )

                    # Optionnel : si ta vue a un widget pour afficher la distribution de hit
                    if hasattr(self.vue, "maj_distribution_hit"):
                        self.vue.maj_distribution_hit(
                            spot.get("distribution_total_si_hit", {})
                        )

                except Exception:
                    # Si clone/retirer_* ou autre n'est pas dispo, on ne casse pas l'UI
                    self.vue.maj_probabilites(0, 0)
                    self.vue.lbl_bust.setText("Bust : --")
                    self.vue.lbl_ameliorer.setText("Reco / EV : --")
        else:
            self.vue.maj_probabilites(0, 0)
            self.vue.lbl_bust.setText("Bust : --")
            self.vue.lbl_ameliorer.setText("Reco / EV : --")

        # Comptage
        sabot = self.jeu.sabot
        total = sabot.nb_paquets * 52

        # Calcul de l'avantage
        tc = sabot.true_count()
        avantage_joueur = -0.5 + (tc * 0.5)

        self.vue.maj_comptage(
            sabot.running_count,
            tc,
            sabot.cartes_restantes(),
            total,
            avantage_joueur
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
