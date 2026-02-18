import json
from pathlib import Path


class Settings:
    chemin_dossier = Path.home() / ".statjack"
    chemin_fichier = chemin_dossier / "settings.json"

    defaut = {
        "musique": True,
        "sons": True,
        "nb_paquets": 6,
        "argent": 10000,
    }

    def __init__(self):
        self._data = dict(self.defaut)
        self.charger()

    def charger(self):
        if self.chemin_fichier.exists():
            try:
                with open(self.chemin_fichier, "r") as f:
                    sauvegarde = json.load(f)
                for cle, defaut in self.defaut.items():
                    self._data[cle] = sauvegarde.get(cle, defaut)
            except (json.JSONDecodeError, OSError):
                self._data = dict(self.defaut)

    def sauvegarder(self):
        self.chemin_dossier.mkdir(parents=True, exist_ok=True)
        with open(self.chemin_fichier, "w") as f:
            json.dump(self._data, f, indent=2)

    def get(self, cle):
        return self._data.get(cle, self.defaut.get(cle))

    def set(self, cle, valeur):
        self._data[cle] = valeur
        self.sauvegarder()

    def reset(self):
        self._data = dict(self.defaut)
        self.sauvegarder()
