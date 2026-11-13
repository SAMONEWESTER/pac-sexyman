"""Gameplay balance: every speed, timer and distance in one place.

Change a number here to tweak how the game feels. Speeds are in cells
per second, times in seconds, distances in cells unless noted.
"""

from dataclasses import dataclass


# Pac-Man.
# -----------------------------------------------------------------------------
PAC_MAN_SPEED: float = 3.5
"""Pac-Man's speed, in cells per second."""

PAC_MAN_ANIMATION_FPS: float = 24.0
"""Animation frames per second while Pac-Man moves."""

EAT_RADIUS: float = 10.0
"""Pixels between Pac-Man's center and a dot's center to eat it."""


# Ghosts, shared.
# -----------------------------------------------------------------------------
FRIGHTENED_SECONDS: float = 7.0
"""How long ghosts stay edible after a power pellet is eaten."""

GHOST_RESPAWN_SECONDS: float = 5.0
"""How long an eaten ghost waits in its corner before coming back."""

GHOST_HIT_RADIUS: float = 10.0
"""Pixels between Pac-Man's and a ghost's center for them to touch."""

GHOST_BODY_FPS: float = 12.0
"""Body wobble frames per second."""

GHOST_SPEED: float = 2.5
"""A ghost's speed, in cells per second."""

FRIGHTENED_GHOST_SPEED: float = 1.25
"""A ghost's speed, in cells per second."""

EATEN_GHOST_SPEED: float = 5.0
"""A ghost's eyes' speed, in cells per second."""


# Ghosts, one by one.
# -----------------------------------------------------------------------------

@dataclass(frozen=True)
class GhostTuning:
    """Speeds of one ghost.

    Attributes:
        speed: Normal speed, in cells per second.
        frightened_speed: Speed while edible, in cells per second.
    """

    speed: float


BLINKY: GhostTuning = GhostTuning(GHOST_SPEED * 1.2)

PINKY: GhostTuning = GhostTuning(GHOST_SPEED)

INKY: GhostTuning = GhostTuning(GHOST_SPEED)

CLYDE: GhostTuning = GhostTuning(GHOST_SPEED)

WINKY: GhostTuning = GhostTuning(GHOST_SPEED * 1.1)
