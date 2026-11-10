"""Loading and playing of sound effects and music.

The game never crashes over audio: no sound card, a missing file or a
broken file only logs a warning and that sound stays silent.
"""

from pathlib import Path

import pygame
from pygame import error as PygameError

from ..errors import LOGGER
from ..resources import asset_path
from .sounds import (
    ALL_SOUND_EFFECTS,
    LEVEL_MUSIC,
    MUSIC_FOLDER,
    SFX_FOLDER,
    MusicTrack,
    SoundEffect,
)

MIXER_CHANNELS: int = 32
"""Sounds that can play at the same time (4 players eat a lot of dots)."""

DEFAULT_MUSIC_VOLUME: float = 0.5
"""Master music volume at startup, 0.0 to 1.0."""

DEFAULT_SFX_VOLUME: float = 0.7
"""Master sound effect volume at startup, 0.0 to 1.0."""


def _clamp(volume: float) -> float:
    """Keep a volume between 0.0 and 1.0."""
    return max(0.0, min(1.0, volume))


class SoundManager:
    """Plays every sound in ``sounds.py``. Use the shared ``AUDIO``.

    Call ``load_all()`` once after ``pygame.init()``, then::

        AUDIO.play(sounds.DOT_EATEN)
        AUDIO.play_music(sounds.music_for_level(level))
    """

    def __init__(self) -> None:
        self.enabled = False
        "False when there is no working audio device."
        self.music_volume = DEFAULT_MUSIC_VOLUME
        self.sfx_volume = DEFAULT_SFX_VOLUME
        self.music_muted = False
        self.sfx_muted = False

        self._sounds: dict[SoundEffect, pygame.mixer.Sound] = {}
        self._track: MusicTrack | None = None
        "The track that is playing (or would be, if unmuted)."
        self._reported: set[str] = set()
        "Files already warned about, so each warning shows only once."

    # Loading.
    # -------------------------------------------------------------------------
    def load_all(self) -> None:
        """Start the mixer and load every sound effect.

        Never raises: without an audio device the game runs silently.
        """
        try:
            if not pygame.mixer.get_init():
                pygame.mixer.init()
            pygame.mixer.set_num_channels(MIXER_CHANNELS)
        except PygameError as err:
            LOGGER.warning('no audio device (%s). Playing without sound.',
                           err)
            return
        self.enabled = True

        for effect in ALL_SOUND_EFFECTS:
            self._load_sound(effect)
        self._check_music_files()

        missing = len(self._reported)
        if missing:
            LOGGER.warning(
                '%d audio file(s) missing or unreadable, they stay silent.'
                ' See the log file for the list.', missing)

    def _load_sound(self, effect: SoundEffect) -> None:
        """Load one sound effect into memory, or note why it can't."""
        path = asset_path(f'{SFX_FOLDER}/{effect.file}')
        if not Path(path).is_file():
            self._report(path, 'missing')
            return
        try:
            sound = pygame.mixer.Sound(path)
        except PygameError as err:
            self._report(path, str(err))
            return
        sound.set_volume(effect.volume * self.sfx_volume)
        self._sounds[effect] = sound

    def _check_music_files(self) -> None:
        """Note missing tracks now, instead of when their level starts."""
        for track in LEVEL_MUSIC:
            path = asset_path(f'{MUSIC_FOLDER}/{track.file}')
            if not Path(path).is_file():
                self._report(path, 'missing')

    def _report(self, path: str, reason: str) -> None:
        """Log a file problem to the log file, once per file."""
        if path in self._reported:
            return
        self._reported.add(path)
        LOGGER.info("audio file '%s' skipped: %s", path, reason)

    # Sound effects.
    # -------------------------------------------------------------------------
    def play(self, effect: SoundEffect) -> None:
        """Play a sound effect once. Silent if it could not be loaded.

        Args:
            effect: A sound from ``sounds.py``.
        """
        if self.sfx_muted:
            return
        sound = self._sounds.get(effect)
        if sound is not None:
            sound.play()

    # Music.
    # -------------------------------------------------------------------------
    def play_music(self, track: MusicTrack, loops: int = -1) -> None:
        """Switch to a track and start it from the beginning.

        Args:
            track: A track from ``sounds.py``.
            loops: Extra times to repeat; -1 repeats forever.
        """
        self._track = track
        if not self.enabled:
            return
        pygame.mixer.music.stop()
        if self.music_muted:
            return
        path = asset_path(f'{MUSIC_FOLDER}/{track.file}')
        if not Path(path).is_file():
            self._report(path, 'missing')
            return
        try:
            pygame.mixer.music.load(path)
        except PygameError as err:
            self._report(path, str(err))
            return
        pygame.mixer.music.set_volume(track.volume * self.music_volume)
        pygame.mixer.music.play(loops)

    def stop_music(self) -> None:
        """Stop the music. ``play_music`` starts it again."""
        self._track = None
        if self.enabled:
            pygame.mixer.music.stop()

    def pause_music(self) -> None:
        """Pause the music where it is."""
        if self.enabled:
            pygame.mixer.music.pause()

    def resume_music(self) -> None:
        """Continue paused music from where it stopped."""
        if self.enabled:
            pygame.mixer.music.unpause()

    # Volume.
    # -------------------------------------------------------------------------
    def set_music_volume(self, volume: float) -> None:
        """Set the master music volume, 0.0 to 1.0."""
        self.music_volume = _clamp(volume)
        if self.enabled and self._track is not None:
            pygame.mixer.music.set_volume(
                self._track.volume * self.music_volume)

    def set_sfx_volume(self, volume: float) -> None:
        """Set the master sound effect volume, 0.0 to 1.0."""
        self.sfx_volume = _clamp(volume)
        for effect, sound in self._sounds.items():
            sound.set_volume(effect.volume * self.sfx_volume)

    # Mute.
    # -------------------------------------------------------------------------
    def toggle_music(self) -> None:
        """Mute or unmute the music. Unmuting restarts the current track."""
        self.music_muted = not self.music_muted
        if self._track is not None:
            self.play_music(self._track)

    def toggle_sfx(self) -> None:
        """Mute or unmute sound effects."""
        self.sfx_muted = not self.sfx_muted
        if self.sfx_muted and self.enabled:
            pygame.mixer.stop()


AUDIO = SoundManager()
"""The game's one sound manager. Call ``AUDIO.load_all()`` at startup."""
