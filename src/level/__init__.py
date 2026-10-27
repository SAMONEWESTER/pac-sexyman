"""The maze and everything placed in it when a level starts."""

from .maze import Maze
from .pickups import generate_dots, generate_power_pellets
from .spawns import spawn_ghosts, spawn_pac_man

__all__ = [
    'Maze',
    'generate_dots',
    'generate_power_pellets',
    'spawn_ghosts',
    'spawn_pac_man',
]
