import os
import sys
from pathlib import Path

from PySide6.QtCore import QObject, QUrl
from PySide6.QtWidgets import QApplication
from PySide6.QtMultimedia import QSoundEffect, QMediaPlayer, QAudioOutput


AUDIO_DIR = Path(__file__).resolve().parent.parent.parent / "audio"


class AudioManager(QObject):
    def __init__(self, settings, parent=None):
        super().__init__(parent)
        self.settings = settings

        self.theme = AUDIO_DIR / "theme(placeholder).wav"
        self.card_path = AUDIO_DIR / "card1.wav"
        self.shuffle_path = AUDIO_DIR / "shuffle.wav"
        self.win_path = AUDIO_DIR / "win.wav"
        self.lose_path = AUDIO_DIR / "lose.wav"

        self.audio_output = QAudioOutput(self)
        self.audio_output.setVolume(0.4)

        self.music_player = QMediaPlayer(self)
        self.music_player.setAudioOutput(self.audio_output)

        devnull = os.open(os.devnull, os.O_WRONLY)
        old_stderr = os.dup(2)
        os.dup2(devnull, 2)
        self.music_player.setSource(QUrl.fromLocalFile(str(self.theme.resolve())))
        os.dup2(old_stderr, 2)
        os.close(devnull)
        os.close(old_stderr)

        # Essaie ceci d'abord si ta version le supporte
        try:
            self.music_player.setLoops(-1)
        except Exception:
            self.music_player.mediaStatusChanged.connect(self._gerer_boucle_musique)

        self.card_sound = self._creer_sound_effect(self.card_path)
        self.shuffle_sound = self._creer_sound_effect(self.shuffle_path)
        self.win_sound = self._creer_sound_effect(self.win_path)
        self.lose_sound = self._creer_sound_effect(self.lose_path)

        app = QApplication.instance()
        if app is not None:
            app.aboutToQuit.connect(self.cleanup)

    def _creer_sound_effect(self, chemin, volume=0.8):
        sound = QSoundEffect(self)
        sound.setSource(QUrl.fromLocalFile(str(chemin.resolve())))
        sound.setVolume(volume)
        return sound

    def _gerer_boucle_musique(self, status):
        if status == QMediaPlayer.EndOfMedia:
            self.music_player.setPosition(0)
            self.music_player.play()

    def jouer_musique(self):
        if not self.settings.get("musique"):
            return

        if self.music_player.playbackState() != QMediaPlayer.PlayingState:
            self.music_player.play()

    def arreter_musique(self):
        self.music_player.stop()

    def jouer_son_hit(self):
        if not self.settings.get("sons"):
            return
        if self.card_sound.isLoaded():
            self.card_sound.play()

    def jouer_son_shuffle(self):
        if not self.settings.get("sons"):
            return
        if self.shuffle_sound.isLoaded():
            self.shuffle_sound.play()

    def jouer_son_victoire(self):
        if not self.settings.get("sons"):
            return
        if self.win_sound.isLoaded():
            self.win_sound.play()

    def jouer_son_defaite(self):
        if not self.settings.get("sons"):
            return
        if self.lose_sound.isLoaded():
            self.lose_sound.play()

    def toggle_musique(self, actif):
        self.settings.set("musique", actif)
        if actif:
            self.jouer_musique()
        else:
            self.arreter_musique()

    def toggle_sons(self, actif):
        self.settings.set("sons", actif)

    def cleanup(self):
        self.music_player.stop()