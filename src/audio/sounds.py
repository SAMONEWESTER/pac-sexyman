"""Every sound and music track the game plays, in one place.

To swap a sound: drop the new file into ``assets/audio/sfx`` (or
``assets/audio/music``) and change its file name here. Volumes are
0.0 to 1.0 and are multiplied by the master volume of the
``SoundManager``, so they only set how loud a sound is compared to
the others.

A file that does not exist yet is skipped with a warning, so the game
runs fine while sounds are still being made.
"""

from dataclasses import dataclass

SFX_FOLDER: str = 'audio/sfx'
"""Sound effect folder, relative to ``assets``."""

MUSIC_FOLDER: str = 'audio/music'
"""Music folder, relative to ``assets``."""


@dataclass(frozen=True)
class SoundEffect:
    """A short sound, loaded into memory once and played on events.

    Attributes:
        file: File name inside ``assets/audio/sfx``.
        volume: Loudness compared to other sounds, 0.0 to 1.0.
    """

    file: str
    volume: float = 1.0


@dataclass(frozen=True)
class MusicTrack:
    """A long track, streamed from disk and looped.

    Attributes:
        file: File name inside ``assets/audio/music``.
        volume: Loudness compared to other tracks, 0.0 to 1.0.
    """

    file: str
    volume: float = 1.0


# Sound effects.
# -----------------------------------------------------------------------------
DOT_EATEN: SoundEffect = SoundEffect('dot_eaten.mp3', 0.3)
"""Pac-Man eats a pac-dot. Plays very often, so keep it short and quiet."""

POWER_PELLET_EATEN: SoundEffect = SoundEffect('power_pellet_eaten.mp3', 0.8)
"""Pac-Man eats a power pellet and the ghosts turn blue."""

GHOST_EATEN: SoundEffect = SoundEffect('ghost_eaten.mp3', 0.8)
"""Pac-Man eats a frightened ghost."""

PLAYER_DIED: SoundEffect = SoundEffect('player_died.mp3', 0.9)
"""A ghost catches Pac-Man and he loses a life."""

PLAYER_OUT: SoundEffect = SoundEffect('player_out.mp3', 0.9)
"""A player loses their last life (other players may still be playing)."""

PLAYER_JOINED: SoundEffect = SoundEffect('player_joined.mp3', 0.8)
"""A player presses confirm to join the game."""

EXTRA_LIFE: SoundEffect = SoundEffect('extra_life.mp3', 0.8)
"""A player reaches another 10,000 points and earns a life."""

LEVEL_CLEARED: SoundEffect = SoundEffect('level_cleared.mp3', 1.0)
"""Every dot of the level has been eaten."""

TIME_UP: SoundEffect = SoundEffect('game_over.mp3', 1.0)
"""The level timer ran out, which ends the game."""

GAME_OVER: SoundEffect = SoundEffect('game_over.mp3', 1.0)
"""Every player is out of lives."""

ALL_SOUND_EFFECTS: tuple[SoundEffect, ...] = (
    DOT_EATEN,
    POWER_PELLET_EATEN,
    GHOST_EATEN,
    PLAYER_DIED,
    PLAYER_OUT,
    PLAYER_JOINED,
    EXTRA_LIFE,
    LEVEL_CLEARED,
    TIME_UP,
    GAME_OVER,
)
"""Every sound effect, loaded at startup. Add new sounds here too."""


# Music.
# -----------------------------------------------------------------------------
LEVEL_MUSIC: tuple[MusicTrack, ...] = (
    MusicTrack('level_01.mp3', 0.6),
    MusicTrack('level_02.mp3', 0.6),
    MusicTrack('level_03.mp3', 0.6),
    MusicTrack('level_04.mp3', 0.6),
    MusicTrack('level_05.mp3', 0.6),
    MusicTrack('level_06.mp3', 0.6),
    MusicTrack('level_07.mp3', 0.6),
    MusicTrack('level_08.mp3', 0.6),
    MusicTrack('level_09.mp3', 0.6),
    MusicTrack('level_10.mp3', 0.6),
    MusicTrack('level_11.mp3', 0.6),
    MusicTrack('level_12.mp3', 0.6),
)
"""One track per level, in level order.

Levels never run out, so after the last track the list starts over.
Add or remove entries freely; the game adapts to the length.
"""


def music_for_level(level: int) -> MusicTrack:
    """The track that plays during a level.

    Args:
        level: Level number, starting at 0. Any size is fine.
    """
    return LEVEL_MUSIC[level % len(LEVEL_MUSIC)]
