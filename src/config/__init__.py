"""Configuration loading and project-wide constants."""

from .constants import CONFIG_PATH, FPS, HALF_TILE, TILE_SIZE, WINDOW_TITLE
from .loader import load_config

__all__ = [
    'CONFIG_PATH',
    'FPS',
    'HALF_TILE',
    'TILE_SIZE',
    'WINDOW_TITLE',
    'load_config',
]
