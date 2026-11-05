"""Configuration loading, validation and project-wide constants.

Gameplay balance numbers live in ``tuning``: ``from ..config import tuning``.
"""

from . import tuning
from .constants import FPS, HALF_TILE, TILE_SIZE
from .config import Config, load_config

__all__ = [
    'Config',
    'load_config',
    'FPS',
    'HALF_TILE',
    'TILE_SIZE',
    'tuning',
]
