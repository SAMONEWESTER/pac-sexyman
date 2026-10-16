"""Placing dots and power pellets in a maze."""

from __future__ import annotations

from pygame import Vector2
from pygame.sprite import Group

from ..config import HALF_TILE
from ..entities import Dot, IdleStyle, PowerPellet
from ..grid import cell_center
from .maze import Maze


def generate_dots(maze: Maze, style: IdleStyle, points: int) -> Group[Dot]:
    """Put a dot in every open cell and between open neighbours.

    The four corner cells are skipped: power pellets go there.

    Args:
        maze: The maze to fill.
        style: Idle motion of every dot.
        points: Score for eating one dot.

    Returns:
        A sprite group holding all created dots.
    """
    corners = set(maze.corners)
    to_east, to_south = Vector2(HALF_TILE, 0), Vector2(0, HALF_TILE)
    result: Group[Dot] = Group()
    for (x, y), cell in maze:
        center = cell_center((x, y))
        if maze.is_open((x, y)) and (x, y) not in corners:
            result.add(Dot(center, style, points))
        if not cell & 2:  # No east wall: dot halfway to the right.
            result.add(Dot(center + to_east, style, points))
        if not cell & 4:  # No south wall: dot halfway down.
            result.add(Dot(center + to_south, style, points))
    return result


def generate_power_pellets(
        maze: Maze, style: IdleStyle, points: int) -> Group[PowerPellet]:
    """Put a power pellet in each of the four corners.

    Args:
        maze: The maze to fill.
        style: Idle motion of every pellet.
        points: Score for eating one pellet.

    Returns:
        A sprite group holding the four pellets.
    """
    return Group(*(
        PowerPellet(cell_center(corner), style, points)
        for corner in maze.corners
    ))
