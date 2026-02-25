import struct
import wave
import math
import tempfile
import subprocess
import sys
from pathlib import Path

from PySide6.QtCore import QTimer, QObject


DOSSIER_AUDIO = Path(tempfile.gettempdir()) / "statjack_audio"


def _generer_wav(chemin, echantillons, sample_rate=44100):
    chemin.parent.mkdir(parents=True, exist_ok=True)
    with wave.open(str(chemin), "w") as f:
        f.setnchannels(1)
        f.setsampwidth(2)
        f.setframerate(sample_rate)
        for s in echantillons:
            val = max(-32767, min(32767, int(s * 32767)))
            f.writeframes(struct.pack("<h", val))


def _generer_musique():
    chemin = DOSSIER_AUDIO / "musique.wav"
    if chemin.exists():
        return chemin
    sr = 44100
    duree = 30
    samples = []
    accords = [
        (0, [261.63, 329.63, 392.00]),
        (7.5, [293.66, 369.99, 440.00]),
        (15, [246.94, 311.13, 369.99]),
        (22.5, [261.63, 329.63, 392.00]),
    ]
    for i in range(sr * duree):
        t = i / sr
        idx = 0
        for j, (debut, _) in enumerate(accords):
            if t >= debut:
                idx = j
        freqs = accords[idx][1]
        val = 0
        for freq in freqs:
            val += 0.15 * math.sin(2 * math.pi * freq * t)
        fade_in = min(t / 0.5, 1.0)
        fade_out = min((duree - t) / 0.5, 1.0)
        val *= fade_in * fade_out
        samples.append(val)
    _generer_wav(chemin, samples, sr)
    return chemin


def _generer_son_carte():
    chemin = DOSSIER_AUDIO / "carte.wav"
    if chemin.exists():
        return chemin
    sr = 44100
    duree = 0.15
    samples = []
    import random
    random.seed(42)
    for i in range(int(sr * duree)):
        t = i / sr
        bruit = random.uniform(-1, 1)
        envelope = max(0, 1 - t / duree)
        samples.append(bruit * envelope * 0.4)
    _generer_wav(chemin, samples, sr)
    return chemin


def _generer_son_victoire():
    chemin = DOSSIER_AUDIO / "victoire.wav"
    if chemin.exists():
        return chemin
    sr = 44100
    duree = 0.6
    samples = []
    notes = [523.25, 659.25, 783.99]
    for i in range(int(sr * duree)):
        t = i / sr
        idx = min(int(t / (duree / 3)), 2)
        freq = notes[idx]
        envelope = max(0, 1 - (t % (duree / 3)) / (duree / 3) * 0.5)
        samples.append(0.35 * math.sin(2 * math.pi * freq * t) * envelope)
    _generer_wav(chemin, samples, sr)
    return chemin


def _generer_son_defaite():
    chemin = DOSSIER_AUDIO / "defaite.wav"
    if chemin.exists():
        return chemin
    sr = 44100
    duree = 0.4
    samples = []
    for i in range(int(sr * duree)):
        t = i / sr
        freq = 300 - 150 * (t / duree)
        envelope = max(0, 1 - t / duree)
        samples.append(0.3 * math.sin(2 * math.pi * freq * t) * envelope)
    _generer_wav(chemin, samples, sr)
    return chemin


class AudioManager(QObject):

    def __init__(self, settings, parent=None):
        super().__init__(parent)
        self.settings = settings
        self._chemin_musique = None
        self._chemin_carte = None
        self._chemin_victoire = None
        self._chemin_defaite = None
        self._process_musique = None

    def _init_fichiers(self):
        # Supprimer les anciens fichiers 22050Hz pour forcer la regénération en 44100Hz
        for nom in ["musique.wav", "carte.wav", "victoire.wav", "defaite.wav"]:
            p = DOSSIER_AUDIO / nom
            if p.exists():
                try:
                    with wave.open(str(p), "r") as f:
                        if f.getframerate() != 44100:
                            p.unlink()
                except Exception:
                    pass

        if self._chemin_musique is None:
            self._chemin_musique = _generer_musique()
        if self._chemin_carte is None:
            self._chemin_carte = _generer_son_carte()
        if self._chemin_victoire is None:
            self._chemin_victoire = _generer_son_victoire()
        if self._chemin_defaite is None:
            self._chemin_defaite = _generer_son_defaite()

    def _jouer_afplay(self, chemin):
        if sys.platform == "darwin":
            try:
                subprocess.Popen(
                    ["afplay", str(chemin)],
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL,
                )
            except FileNotFoundError:
                pass
        else:
            try:
                subprocess.Popen(
                    ["aplay", str(chemin)],
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL,
                )
            except FileNotFoundError:
                pass

    def jouer_musique(self):
        if not self.settings.get("musique"):
            return
        self._init_fichiers()
        self.arreter_musique()
        self._boucle_musique()

    def _boucle_musique(self):
        if not self.settings.get("musique"):
            return
        if sys.platform == "darwin":
            try:
                self._process_musique = subprocess.Popen(
                    ["afplay", str(self._chemin_musique)],
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL,
                )
                self._verifier_fin_musique()
            except FileNotFoundError:
                pass

    def _verifier_fin_musique(self):
        if self._process_musique and self._process_musique.poll() is not None:
            if self.settings.get("musique"):
                self._boucle_musique()
        elif self._process_musique:
            QTimer.singleShot(1000, self._verifier_fin_musique)

    def arreter_musique(self):
        if self._process_musique:
            try:
                self._process_musique.terminate()
            except Exception:
                pass
            self._process_musique = None

    def jouer_son_carte(self):
        if not self.settings.get("sons"):
            return
        self._init_fichiers()
        self._jouer_afplay(self._chemin_carte)

    def jouer_son_victoire(self):
        if not self.settings.get("sons"):
            return
        self._init_fichiers()
        self._jouer_afplay(self._chemin_victoire)

    def jouer_son_defaite(self):
        if not self.settings.get("sons"):
            return
        self._init_fichiers()
        self._jouer_afplay(self._chemin_defaite)

    def toggle_musique(self, actif):
        self.settings.set("musique", actif)
        if actif:
            self.jouer_musique()
        else:
            self.arreter_musique()

    def toggle_sons(self, actif):
        self.settings.set("sons", actif)
