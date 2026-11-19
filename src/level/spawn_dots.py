"""Placing dots and power pellets in a maze."""

from __future__ import annotations

from pygame import Vector2

from ..config import HALF_TILE
from .maze import Maze
from ..node.entity.float_animation import FloatStyle
from ..node.entity.item.dot import Dot


def spawn_dots(
        maze: Maze,
        float_style: FloatStyle,
        ) -> list[Dot]:
    """Put dots in open cells and between open neighbours.

    Dead ends and their directly attached cells are excluded.
    """
    corners = set(maze.corners)
    to_east = Vector2(HALF_TILE, 0)
    to_south = Vector2(0, HALF_TILE)
    result: list[Dot] = []
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
        center = maze.cell_center(pos)

        # Cell dot: only exclude forbidden cells.
        if pos not in forbidden_cells and pos not in corners:
            if pos not in maze.closed_cells:
                result.append(Dot(center, float_style, maze.theme))

        # East edge dot: both cells must be allowed.
        east = (x + 1, y)
        if not cell & 2 and pos not in forbidden_cells \
                and east not in forbidden_cells:
            result.append(Dot(center + to_east, float_style, maze.theme))

        # South edge dot: both cells must be allowed.
        south = (x, y + 1)
        if not cell & 4 and pos not in forbidden_cells \
                and south not in forbidden_cells:
            result.append(Dot(center + to_south, float_style, maze.theme))

    return result
