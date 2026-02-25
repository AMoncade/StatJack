from src.models.main_joueur import MainJoueur
from collections import Counter





class CalculateurProbabilites:

    @staticmethod
    def _total_apres_ajout(main_joueur, valeur, est_as=False):
        total = 0
        nb_as = 0

        for c in main_joueur.cartes:
            total += c.valeur_blackjack()
            if c.rang == "A":
                nb_as += 1

        total += valeur
        if est_as:
            nb_as += 1

        while total > 21 and nb_as > 0:
            total -= 10
            nb_as -= 1

        return total

    @staticmethod
    def _etat_main(main_joueur):
        # Retourne (total, soft_aces) pour la main actuelle. soft_aces = nb d'As encore comptés comme 11 après ajustement.
        total = 0
        soft_aces = 0
        for c in main_joueur.cartes:
            v = c.valeur_blackjack()
            total += v
            if c.rang == "A":
                soft_aces += 1

        while total > 21 and soft_aces > 0:
            total -= 10
            soft_aces -= 1

        return total, soft_aces

    @staticmethod
    def total_avec_carte(main_joueur, carte):
        return CalculateurProbabilites._total_apres_ajout(
            main_joueur,
            valeur=carte.valeur_blackjack(),
            est_as=(carte.rang == "A")
        )

    @staticmethod
    def total_avec_valeur(main_joueur, valeur):
        return CalculateurProbabilites._total_apres_ajout(
            main_joueur,
            valeur=valeur,
            est_as=(valeur == 11)
        )

    @staticmethod
    def distribution_nouveau_total_si_hit(main_joueur, sabot):
        cartes_restantes = sabot.cartes_restantes()
        if cartes_restantes == 0:
            return {}

        # On part de la distribution des valeurs (2..11, 10)
        dist_valeurs = CalculateurProbabilites.distribution_prochaine_carte(sabot)

        dist_totaux = {}
        for valeur, proba in dist_valeurs.items():
            nouveau_total = CalculateurProbabilites.total_avec_valeur(main_joueur, valeur)
            key = "bust" if nouveau_total > 21 else nouveau_total
            dist_totaux[key] = dist_totaux.get(key, 0) + proba

        sorted_keys = [k for k in sorted([x for x in dist_totaux.keys() if x != "bust"])]
        if "bust" in dist_totaux:
            sorted_keys.append("bust")
        return {k: dist_totaux[k] for k in sorted_keys}

    @staticmethod
    def distribution_prochaine_carte(sabot):
        cartes_restantes = sabot.cartes_restantes()
        if cartes_restantes == 0:
            return {}

        compteur = {}
        for carte in sabot.cartes:
            v = carte.valeur_blackjack()
            compteur[v] = compteur.get(v, 0) + 1

        return {v: count / cartes_restantes for v, count in sorted(compteur.items())}

    @staticmethod
    def dealer_distribution(sabot, dealer_upcard, nb_simulations=5000):
        outcomes = Counter()

        for _ in range(nb_simulations):
            s = sabot.clone()

            # Simulation aléatoire
            s.melanger_sans_reset()

            main_d = MainJoueur()
            main_d.ajouter_carte(dealer_upcard)
            main_d.ajouter_carte(s.tirer())  # hole

            while main_d.valeur_totale() < 17:
                main_d.ajouter_carte(s.tirer())

            t = main_d.valeur_totale()
            outcomes["bust" if t > 21 else t] += 1

        total = sum(outcomes.values()) or 1
        return {k: v / total for k, v in outcomes.items()}

    @staticmethod
    def ev_stand(total_joueur, dealer_dist):
        ev = dealer_dist.get("bust", 0.0) * 1.0
        for r in (17, 18, 19, 20, 21):
            p = dealer_dist.get(r, 0.0)
            if total_joueur > r:
                ev += p * 1.0
            elif total_joueur < r:
                ev += p * -1.0
        return ev

    @staticmethod
    def ev_hit_une_fois_puis_stand(main_joueur, sabot, dealer_dist):
        dist_valeurs = CalculateurProbabilites.distribution_prochaine_carte(sabot)
        ev = 0.0
        for valeur, proba in dist_valeurs.items():
            new_total = CalculateurProbabilites.total_avec_valeur(main_joueur, valeur)
            if new_total > 21:
                ev += proba * -1.0
            else:
                ev += proba * CalculateurProbabilites.ev_stand(new_total, dealer_dist)
        return ev

    @staticmethod
    def ev_hit_recursive(total,soft_aces, dealer_dist, dist_valeurs, memo=None):
        # Calcul EV optimal pour hit
        if memo is None:
            memo = {}

        # Bust
        if total > 21:
            return -1.0

        key = (total, soft_aces)
        if key in memo:
            return memo[key]

        # EV si on stand maintenant (soft_aces ne change rien si on stand)
        ev_stand = CalculateurProbabilites.ev_stand(total, dealer_dist)

        # EV si on hit encore
        ev_hit = 0.0
        for valeur, proba in dist_valeurs.items():
            new_total = total + valeur
            new_soft = soft_aces + (1 if valeur == 11 else 0)

            # Ajustement des As soft si on dépasse 21
            while new_total > 21 and new_soft > 0:
                new_total -= 10
                new_soft -= 1

            ev_hit += proba * CalculateurProbabilites.ev_hit_recursive(
                new_total, new_soft, dealer_dist, dist_valeurs, memo
            )

        ev_opt = max(ev_stand, ev_hit)
        memo[key] = ev_opt
        return ev_opt

    @staticmethod
    def ev_optimal(main_joueur, sabot_cond, dealer_dist):
        total_initial, soft_aces_initial = CalculateurProbabilites._etat_main(main_joueur)
        dist_valeurs = CalculateurProbabilites.distribution_prochaine_carte(sabot_cond)

        return CalculateurProbabilites.ev_hit_recursive(
            total_initial, soft_aces_initial, dealer_dist, dist_valeurs
        )

    @staticmethod
    def resume_spot(main_joueur, dealer_upcard, sabot, nb_simulations_dealer=5000):

        sabot_cond = sabot.clone()
        if hasattr(sabot_cond, "retirer_cartes"):
            sabot_cond.retirer_cartes(main_joueur.cartes)
            sabot_cond.retirer_carte(dealer_upcard)

        dist_hit = CalculateurProbabilites.distribution_nouveau_total_si_hit(main_joueur, sabot_cond)
        p_bust = dist_hit.get("bust", 0.0)

        dealer_dist = CalculateurProbabilites.dealer_distribution(sabot_cond, dealer_upcard, nb_simulations_dealer)

        t = main_joueur.valeur_totale()
        ev_stand = CalculateurProbabilites.ev_stand(t, dealer_dist)
        ev_opt = CalculateurProbabilites.ev_optimal(main_joueur, sabot_cond, dealer_dist)

        reco = "HIT" if ev_opt > ev_stand else "STAND"

        return {
            "total_joueur": t,
            "distribution_total_si_hit": dist_hit,
            "p_bust_si_hit": p_bust,
            "dealer_distribution": dealer_dist,
            "ev_stand": ev_stand,
            "ev_optimal": ev_opt,
            "recommandation": reco,
        }

    @staticmethod
    def simuler_mains(sabot, nb_simulations=1000):
        resultats = []
        gains_cumules = []
        total = 0

        for i in range(nb_simulations):
            sabot_temp = sabot.clone()
            sabot_temp.melanger_sans_reset()

            main_j = MainJoueur()
            main_d = MainJoueur()
            for _ in range(2):
                main_j.ajouter_carte(sabot_temp.tirer())
                main_d.ajouter_carte(sabot_temp.tirer())

            # Strategie de base simplifiee
            while main_j.valeur_totale() < 17:
                main_j.ajouter_carte(sabot_temp.tirer())

            while main_d.valeur_totale() < 17:
                main_d.ajouter_carte(sabot_temp.tirer())

            score_j = main_j.valeur_totale()
            score_d = main_d.valeur_totale()

            if score_j > 21:
                gain = -1
            elif main_j.est_blackjack():
                gain = 1.5
            elif score_d > 21:
                gain = 1
            elif score_j > score_d:
                gain = 1
            elif score_j < score_d:
                gain = -1
            else:
                gain = 0

            total += gain
            resultats.append(gain)
            gains_cumules.append(total / (i + 1))

        return gains_cumules
