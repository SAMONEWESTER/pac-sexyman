"""Placing Pac-Man and the ghosts at their start positions."""

from __future__ import annotations

from pygame.sprite import Group

from ..entities import Blinky, Clyde, Ghost, Inky, PacMan, Pinky
from .maze import Maze


def spawn_ghosts(
        maze: Maze,
        pac_men: Group[PacMan],
        points: int
        ) -> Group[Ghost]:
    """Create the four ghosts, one in each corner of the maze.

    Args:
        maze: The maze to spawn in.
        pac_man: Who the ghosts hunt.
        points: Score for eating a frightened ghost.

    Returns:
        A sprite group holding the four ghosts.
    """
    top_left, top_right, bottom_left, bottom_right = maze.corners
    blinky = Blinky(maze, top_right, pac_men, points)
    pinky = Pinky(maze, top_left, pac_men, points)
    inky = Inky(maze, bottom_right, pac_men, points, partner=blinky)
    clyde = Clyde(maze, bottom_left, pac_men, points)
    return Group(blinky, pinky, inky, clyde)
