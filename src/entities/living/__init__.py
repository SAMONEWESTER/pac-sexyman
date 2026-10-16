"""Entities that move through the maze on their own: Pac-Man and ghosts."""

from .ghost import Ghost
from .living import Living
from .pac_man import PacMan

__all__ = ['Ghost', 'Living', 'PacMan']
