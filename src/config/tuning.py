"""Gameplay balance: every speed, timer and distance in one place.

Change a number here to tweak how the game feels. Speeds are in cells
per second, times in seconds, distances in cells unless noted.
"""

from dataclasses import dataclass


GLOBAL_SPEED: float = 0.5

# Pac-Man.
# -----------------------------------------------------------------------------
PAC_MAN_SPEED: float = 7.0 * GLOBAL_SPEED
"""Pac-Man's speed, in cells per second."""

PAC_MAN_ANIMATION_FPS: float = 48.0 * GLOBAL_SPEED
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

GHOST_BODY_FPS: float = 24.0 * GLOBAL_SPEED
"""Body wobble frames per second."""

GHOST_SPEED: float = 5.0 * GLOBAL_SPEED
"""A ghost's speed, in cells per second."""

FRIGHTENED_GHOST_SPEED: float = 3.0 * GLOBAL_SPEED
"""A ghost's speed, in cells per second."""

EATEN_GHOST_SPEED: float = 10.0 * GLOBAL_SPEED
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


BLINKY_SPEED_MULTIPLIER: float = 1.2
"""How much faster Blinky moves relative to the other ghosts."""

PINKY_LOOK_AHEAD: int = 4
"""Pinky aims this many cells in front of Pac-Man, to cut him off."""

INKY_LOOK_AHEAD: int = 2
"""Inky mirrors Blinky around the cell this far in front of Pac-Man."""

CLYDE_SHY_DISTANCE: float = 8.0
"""Closer than this to Pac-Man, Clyde gets shy and runs to his corner."""

BLINKY: GhostTuning = GhostTuning(GHOST_SPEED * BLINKY_SPEED_MULTIPLIER)

PINKY: GhostTuning = GhostTuning(GHOST_SPEED)

INKY: GhostTuning = GhostTuning(GHOST_SPEED)

CLYDE: GhostTuning = GhostTuning(GHOST_SPEED)
