from collections import Counter
from src.models.main_joueur import MainJoueur


class CalculateurProbabilites:

    @staticmethod
    def _sabot_vue_joueur(sabot, dealer_hole_card=None):
        s = sabot.clone()

        # Casino réaliste :
        # On remet la vraie hole card dans le sabot simulé pour qu'elle redevienne une possibilité inconnue
        if dealer_hole_card is not None:
            s.cartes.append(dealer_hole_card)

        return s

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
        # Retourne (total, soft_aces) pour la main actuelle.
        # soft_aces = nb d'As encore comptés comme 11 après ajustement.
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
    def _etat_apres_valeur(total, soft_aces, valeur):
        new_total = total + valeur
        new_soft = soft_aces + (1 if valeur == 11 else 0)

        while new_total > 21 and new_soft > 0:
            new_total -= 10
            new_soft -= 1

        return new_total, new_soft

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

            carte_cachee = s.tirer()
            if carte_cachee is None:
                continue

            main_d.ajouter_carte(carte_cachee)

            while main_d.valeur_totale() < 17:
                carte = s.tirer()
                if carte is None:
                    break
                main_d.ajouter_carte(carte)

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
    def ev_hit_recursive_counts(total, soft_aces, counts, dealer_dist, memo=None):
        if memo is None:
            memo = {}

        if total > 21:
            return -1.0

        key = (
            total,
            soft_aces,
            tuple(sorted(counts.items()))
        )

        if key in memo:
            return memo[key]

        ev_stand = CalculateurProbabilites.ev_stand(total, dealer_dist)

        # Coupure logique : inutile d'explorer hit sur 19, 20 ou 21
        if total >= 19:
            memo[key] = ev_stand
            return ev_stand

        cartes_restantes = sum(counts.values())
        if cartes_restantes == 0:
            memo[key] = ev_stand
            return ev_stand

        ev_hit = 0.0

        for valeur, nb in list(counts.items()):
            if nb <= 0:
                continue

            proba = nb / cartes_restantes

            new_total, new_soft = CalculateurProbabilites._etat_apres_valeur(
                total, soft_aces, valeur
            )

            counts[valeur] -= 1
            if counts[valeur] == 0:
                del counts[valeur]

            ev_hit += proba * CalculateurProbabilites.ev_hit_recursive_counts(
                new_total,
                new_soft,
                counts,
                dealer_dist,
                memo
            )

            counts[valeur] = nb

        ev_opt = max(ev_stand, ev_hit)
        memo[key] = ev_opt
        return ev_opt

    @staticmethod
    def ev_optimal(main_joueur, sabot_cond, dealer_dist):
        total, soft_aces = CalculateurProbabilites._etat_main(main_joueur)
        counts = Counter(c.valeur_blackjack() for c in sabot_cond.cartes)

        return CalculateurProbabilites.ev_hit_recursive_counts(
            total,
            soft_aces,
            counts,
            dealer_dist
        )

    @staticmethod
    def resume_spot(main_joueur, dealer_upcard, sabot, nb_simulations_dealer=5000, dealer_hole_card=None):

        sabot_cond = CalculateurProbabilites._sabot_vue_joueur(sabot, dealer_hole_card)

        dist_hit = CalculateurProbabilites.distribution_nouveau_total_si_hit(main_joueur, sabot_cond)
        p_bust = dist_hit.get("bust", 0.0)

        t = main_joueur.valeur_totale()
        p_ameliorer = 0.0
        for total_final, prob in dist_hit.items():
            if total_final != "bust" and t < total_final <= 21:
                p_ameliorer += prob

        dealer_dist = CalculateurProbabilites.dealer_distribution(sabot_cond, dealer_upcard, nb_simulations_dealer)

        t = main_joueur.valeur_totale()
        ev_stand = CalculateurProbabilites.ev_stand(t, dealer_dist)
        ev_opt = CalculateurProbabilites.ev_optimal(main_joueur, sabot_cond, dealer_dist)

        reco = "HIT" if ev_opt > ev_stand else "STAND"

        return {
            "total_joueur": t,
            "distribution_total_si_hit": dist_hit,
            "p_bust_si_hit": p_bust,
            "p_ameliorer_si_hit": p_ameliorer,
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

    @staticmethod
    def simuler_monte_carlo(main_joueur, dealer, sabot, nb_simulations=1000, dealer_hole_card=None):
        if not dealer.cartes or not main_joueur.cartes:
            return {}

        stats = {}
        actions_possibles = ["Stand", "Hit"]
        if main_joueur.peut_double():
            actions_possibles.append("Double")

        for action in actions_possibles:
            victoires = 0

            for _ in range(nb_simulations):
                # Cloner l'état du sabot pour simuler une manche réaliste
                s = CalculateurProbabilites._sabot_vue_joueur(
                    sabot,
                    dealer_hole_card
                )
                s.melanger_sans_reset()

                # Recréer la main du joueur à partir de la vraie main actuelle
                sim_joueur = MainJoueur()
                for carte in main_joueur.cartes:
                    sim_joueur.ajouter_carte(carte)

                # Le joueur joue son action virtuelle
                if action == "Hit" or action == "Double":
                    carte_tiree = s.tirer()
                    if carte_tiree is not None:
                        sim_joueur.ajouter_carte(carte_tiree)

                if sim_joueur.est_busted():
                    continue  # Défaite automatique (Bust)

                sim_dealer = MainJoueur()
                sim_dealer.ajouter_carte(dealer.cartes[0])

                carte_cachee = s.tirer()
                if carte_cachee is None:
                    continue

                sim_dealer.ajouter_carte(carte_cachee)

                # Le dealer joue (règle: s'arrête à 17)
                while sim_dealer.valeur_totale() < 17:
                    carte_dealer = s.tirer()
                    if carte_dealer is None:
                        break
                    sim_dealer.ajouter_carte(carte_dealer)

                # Qui gagne ?
                total_joueur = sim_joueur.valeur_totale()
                total_dealer = sim_dealer.valeur_totale()

                if total_dealer > 21 or total_joueur > total_dealer:
                    victoires += 1

            # Calcul du pourcentage de victoire
            stats[action] = (victoires / nb_simulations) * 100

        return stats
