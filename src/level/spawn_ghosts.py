"""Placing Pac-Man and the ghosts at their start positions."""

from __future__ import annotations

from pygame.sprite import Group

from ..entities import Blinky, Clyde, Ghost, Inky, PacMan, Pinky, Winky
from .maze import Maze


_DEFAULT_GHOSTS = ('blinky', 'pinky', 'inky', 'clyde')

_NAME_TO_GHOST: dict[str, Ghost] = {
    'blinky': Blinky,
    'pinky': Pinky,
    'inky': Inky,
    'clyde': Clyde,
    'winky': Winky,
}


def spawn_ghosts(
        maze: Maze,
        pac_men: Group[PacMan],
        points: int,
        ghost_names: tuple[str, str, str, str] = _DEFAULT_GHOSTS,
        ) -> Group[Ghost]:
    """Create the four ghosts, one in each corner of the maze.

    Args:
        maze: The maze to spawn in.
        pac_man: Who the ghosts hunt.
        points: Score for eating a frightened ghost.

    Returns:
        A sprite group holding the four ghosts.
    """
    result = Group()

    for i, ghost_name in enumerate(ghost_names):
        factory = _NAME_TO_GHOST[ghost_name]
        result.add(factory(maze, maze.corners[i], pac_men, points, result))
    return result
