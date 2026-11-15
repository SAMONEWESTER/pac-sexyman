"""Placing dots and power pellets in a maze."""

from __future__ import annotations

from pygame import Vector2
from pygame.sprite import Group

from ..resources import ASSETS
from ..node.entity import Entity, FloatAnimation, FloatStyle
from ..node.entity.sprite import WorldSprite
from ..config import HALF_TILE
from ..entities import Dot, IdleStyle
from ..grid import cell_center
from .maze import Maze


def new_dot(
        center: Vector2,
        style: FloatStyle,
        theme: int
        ) -> Entity:
    result = Entity(center)
    result.add_child(
        FloatAnimation(Vector2(0, 0), style, (center.x + center.y) / 100))
    result[0].add_child(
        WorldSprite(Vector2(0, 0), ASSETS.pac_dots[theme]))
    return result


def spawn_dots_node(
        maze: Maze,
        level: int,
        ) -> list[Entity]:
    """Put dots in open cells and between open neighbours.

    Dead ends and their directly attached cells are excluded.
    """
    corners = set(maze.corners)
    to_east = Vector2(HALF_TILE, 0)
    to_south = Vector2(0, HALF_TILE)
    result: list[Entity] = []
    forbidden_cells = maze.dead_ends.copy()
    style = FloatStyle.from_index(level)
    theme = (level // 3) % len(ASSETS.tilesets)

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
                result.append(new_dot(center, style, theme))

        # East edge dot: both cells must be allowed.
        east = (x + 1, y)
        if not cell & 2 and pos not in forbidden_cells \
                and east not in forbidden_cells:
            result.append(new_dot(center + to_east, style, theme))

        # South edge dot: both cells must be allowed.
        south = (x, y + 1)
        if not cell & 4 and pos not in forbidden_cells \
                and south not in forbidden_cells:
            result.append(new_dot(center + to_south, style, theme))

    return result


def spawn_dots(maze: Maze, style: IdleStyle, points: int) -> Group[Dot]:
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
