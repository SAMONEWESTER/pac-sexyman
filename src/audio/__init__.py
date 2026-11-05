"""Sound effects and music.

``sounds.py`` lists every sound with its file and volume.
``manager.py`` loads and plays them through ``AUDIO``.
"""

from . import sounds
from .manager import AUDIO, SoundManager
from .sounds import MusicTrack, SoundEffect, music_for_level

__all__ = [
    'AUDIO',
    'MusicTrack',
    'SoundEffect',
    'SoundManager',
    'music_for_level',
    'sounds',
]
