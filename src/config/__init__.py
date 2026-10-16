"""Configuration loading, validation and project-wide constants."""

from .constants import (
    FPS,
    FRIGHTENED_SECONDS,
    GHOST_SPEED,
    HALF_TILE,
    PAC_MAN_SPEED,
    TILE_SIZE,
    WINDOW_TITLE,
)
from .loader import load_config
from .schema import default_config
from .settings import Config, LevelConfig

__all__ = [
    'Config',
    'FPS',
    'FRIGHTENED_SECONDS',
    'GHOST_SPEED',
    'HALF_TILE',
    'LevelConfig',
    'PAC_MAN_SPEED',
    'TILE_SIZE',
    'WINDOW_TITLE',
    'default_config',
    'load_config',
]
