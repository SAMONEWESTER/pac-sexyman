"""Configuration loading, validation and project-wide constants."""

from .constants import FPS, HALF_TILE, TILE_SIZE, WINDOW_TITLE
from .loader import load_config
from .schema import default_config
from .settings import Config, LevelConfig

__all__ = [
    'Config',
    'FPS',
    'HALF_TILE',
    'LevelConfig',
    'TILE_SIZE',
    'WINDOW_TITLE',
    'default_config',
    'load_config',
]
