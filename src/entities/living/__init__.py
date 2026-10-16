"""Entities that move through the maze on their own: Pac-Man and ghosts."""

from .ghosts import Blinky, Clyde, Ghost, GhostState, Inky, Pinky
from .living import Living
from .pac_man import PacMan

__all__ = [
    'Blinky',
    'Clyde',
    'Ghost',
    'GhostState',
    'Inky',
    'Living',
    'PacMan',
    'Pinky',
]
