"""Everything that lives in a level.

The tree (inheritance, what an entity *is*)::

    Entity (ABC)
    |-- Living (ABC)          moves cell by cell
    |   |-- PacMan
    |   `-- Ghost (ABC)       chase_target() differs per ghost
    |       |-- Blinky
    |       |-- Pinky
    |       |-- Inky
    |       `-- Clyde
    `-- Inanimate             stays at its spot
        |-- Dot
        `-- PowerUp (ABC)
            `-- PowerPellet

The components (composition, what an entity *has*): ``Edible`` and
``IdleAnimation``.
"""

from .components import Edible, IdleAnimation, IdleStyle
from .entity import Entity
from .inanimate import Dot, Inanimate, PowerPellet, PowerUp, PowerUpTarget
from .living import (
    Blinky,
    Clyde,
    Ghost,
    GhostState,
    Inky,
    Living,
    PacMan,
    Pinky,
)

__all__ = [
    'Blinky',
    'Clyde',
    'Dot',
    'Edible',
    'Entity',
    'Ghost',
    'GhostState',
    'IdleAnimation',
    'IdleStyle',
    'Inanimate',
    'Inky',
    'Living',
    'PacMan',
    'Pinky',
    'PowerPellet',
    'PowerUp',
    'PowerUpTarget',
]
