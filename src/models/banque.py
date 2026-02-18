class Banque:

    def __init__(self, settings):
        self.settings = settings
        self.solde = settings.get("argent")

    def placer_mise(self, montant):
        if montant <= 0 or montant > self.solde:
            return False
        self.solde -= montant
        self.sauvegarder()
        return True

    def payer(self, montant):
        self.solde += montant
        self.sauvegarder()

    def sauvegarder(self):
        self.settings.set("argent", self.solde)

    def reset(self):
        self.solde = self.settings.DEFAUTS["argent"]
        self.sauvegarder()