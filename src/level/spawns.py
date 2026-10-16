"""Placing Pac-Man and the ghosts at their start positions."""

from __future__ import annotations

from pygame.sprite import Group

from ..entities import Ghost, PacMan
from ..resources import ASSETS
from .maze import Maze


def spawn_pac_man(maze: Maze) -> PacMan:
    """Create Pac-Man in the open cell closest to the maze center.

    The exact center is usually inside the 42 pattern, which is closed.

    Args:
        maze: The maze to spawn in.
    """
    center = (maze.w // 2, maze.h // 2)
    return PacMan(maze, maze.nearest_open_cell(center))


def spawn_ghosts(maze: Maze, points: int) -> Group[Ghost]:
    """Create one ghost in each corner of the maze.

    Args:
        maze: The maze to spawn in.
        points: Score for eating a frightened ghost.

    Returns:
        A sprite group holding the four ghosts.
    """
    return Group(*(
        Ghost(maze, corner, image, points)
        for corner, image in zip(maze.corners, ASSETS.ghosts)
    ))
