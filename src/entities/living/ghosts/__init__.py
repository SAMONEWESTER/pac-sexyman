"""The four ghosts. They share ``Ghost`` and differ in where they hunt."""

from .blinky import Blinky
from .clyde import Clyde
from .ghost import EYE_FRAMES, Ghost, GhostState
from .inky import Inky
from .pinky import Pinky

__all__ = [
    'Blinky',
    'Clyde',
    'EYE_FRAMES',
    'Ghost',
    'GhostState',
    'Inky',
    'Pinky',
]
