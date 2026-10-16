"""Placing Pac-Man and the ghosts at their start positions."""

from __future__ import annotations

from pygame.sprite import Group

from ..entities import Blinky, Clyde, Ghost, Inky, PacMan, Pinky
from .maze import Maze


def spawn_pac_man(maze: Maze) -> PacMan:
    """Create Pac-Man in the open cell closest to the maze center.

    The exact center is usually inside the 42 pattern, which is closed.

    Args:
        maze: The maze to spawn in.
    """
    center = (maze.w // 2, maze.h // 2)
    return PacMan(maze, maze.nearest_open_cell(center))


def spawn_ghosts(maze: Maze, pac_man: PacMan, points: int) -> Group[Ghost]:
    """Create the four ghosts, one in each corner of the maze.

    Args:
        maze: The maze to spawn in.
        pac_man: Who the ghosts hunt.
        points: Score for eating a frightened ghost.

    Returns:
        A sprite group holding the four ghosts.
    """
    top_left, top_right, bottom_left, bottom_right = maze.corners
    blinky = Blinky(maze, top_right, pac_man, points)
    pinky = Pinky(maze, top_left, pac_man, points)
    inky = Inky(maze, bottom_right, pac_man, points, partner=blinky)
    clyde = Clyde(maze, bottom_left, pac_man, points)
    return Group(blinky, pinky, inky, clyde)
