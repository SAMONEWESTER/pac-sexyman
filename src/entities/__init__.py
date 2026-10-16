"""Everything that lives in a level.

The tree (inheritance, what an entity *is*)::

    Entity (ABC)
    |-- Living (ABC)          moves cell by cell
    |   |-- PacMan
    |   `-- Ghost
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
from .living import Ghost, Living, PacMan

__all__ = [
    'Dot',
    'Edible',
    'Entity',
    'Ghost',
    'IdleAnimation',
    'IdleStyle',
    'Inanimate',
    'Living',
    'PacMan',
    'PowerPellet',
    'PowerUp',
    'PowerUpTarget',
]
