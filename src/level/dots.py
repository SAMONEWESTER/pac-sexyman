"""Placing pac-dots in the corridors of a maze."""

from __future__ import annotations

from pygame import Vector2
from pygame.sprite import Group

from ..config import HALF_TILE, TILE_SIZE
from ..entities import PacDot
from .maze import Maze


def generate_dots(maze: Maze, style: str) -> Group[PacDot]:
    """Create a pac-dot in every open cell and between open neighbours.

    Args:
        maze: The maze to fill.
        style: Idle animation for every dot, one of ``DOT_STYLES``.

    Returns:
        A sprite group holding all created dots.
    """
    result: Group[PacDot] = Group()
    for (x, y), cell in maze:
        left, top = x * TILE_SIZE, y * TILE_SIZE
        if cell != 15:
            result.add(PacDot(Vector2(left + HALF_TILE, top + HALF_TILE), style))
        if not (cell & 2):
            result.add(PacDot(Vector2(left + TILE_SIZE, top + HALF_TILE), style))
        if not (cell & 4):
            result.add(PacDot(Vector2(left + HALF_TILE, top + TILE_SIZE), style))
    return result

    # TODO: power pellets in the four corners.
    # maze.image.blit(
    #     ASSETS.power_pellet, (8, 8))
    # maze.image.blit(
    #     ASSETS.power_pellet, ((maze.w - 1) * 32 + 8, 8))
    # maze.image.blit(
    #     ASSETS.power_pellet, (8, (maze.h - 1) * 32 + 8))
    # maze.image.blit(
    #     ASSETS.power_pellet, ((maze.w - 1) * 32 + 8, (maze.h - 1) * 32 + 8))
