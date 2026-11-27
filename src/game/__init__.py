"""The game window and the main game loop."""

from .game import Game
from .window import create_window
from .player import Player, Players

__all__ = [
    'Game',
    'create_window',
    'Camera',
    'Player',
    'Players',
    'eat',
    'points',
    'touched_ghosts',
]
