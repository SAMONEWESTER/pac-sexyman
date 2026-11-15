"""The maze and everything placed in it when a level starts."""

from .maze import Maze
from .spawn_dots import spawn_dots, spawn_dots_node
from .spawn_ghosts import spawn_ghosts

__all__ = [
    'Maze',
    'spawn_dots',
    'spawn_dots_node',
    'spawn_ghosts',
]
