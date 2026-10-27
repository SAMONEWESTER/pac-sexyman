"""Placing dots and power pellets in a maze."""

from __future__ import annotations

from pygame import Vector2
from pygame.sprite import Group

from ..config import HALF_TILE
from ..entities import Dot, IdleStyle, PowerPellet
from ..grid import cell_center
from .maze import Maze


def generate_dots(maze: Maze, style: IdleStyle, points: int) -> Group[Dot]:
    """Put dots in open cells and between open neighbours.

    Dead ends and their directly attached cells are excluded.
    """
    corners = set(maze.corners)
    to_east = Vector2(HALF_TILE, 0)
    to_south = Vector2(0, HALF_TILE)
    result: Group[Dot] = Group()

    forbidden_cells = maze.dead_ends.copy()

    directions = {
        1: (0, -1),  # north
        2: (1, 0),   # east
        4: (0, 1),   # south
        8: (-1, 0),  # west
    }

    for x, y in maze.dead_ends:
        cell = maze[x, y]
        for wall, (dx, dy) in directions.items():
            if not cell & wall:
                forbidden_cells.add((x + dx, y + dy))

    for (x, y), cell in maze:
        pos = (x, y)
        center = cell_center(pos)

        # Cell dot: only exclude forbidden cells.
        if pos not in forbidden_cells and pos not in corners:
            if pos not in maze.closed_cells:
                result.add(Dot(center, style, points, maze.theme))

        # East edge dot: both cells must be allowed.
        east = (x + 1, y)
        if not cell & 2 and pos not in forbidden_cells \
                and east not in forbidden_cells:
            result.add(Dot(center + to_east, style, points, maze.theme))

        # South edge dot: both cells must be allowed.
        south = (x, y + 1)
        if not cell & 4 and pos not in forbidden_cells \
                and south not in forbidden_cells:
            result.add(Dot(center + to_south, style, points, maze.theme))

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
        PowerPellet(cell_center(corner), style, points, maze.theme)
        for corner in maze.corners
    ))
