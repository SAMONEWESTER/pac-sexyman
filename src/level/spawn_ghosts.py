"""Placing Pac-Man and the ghosts at their start positions."""

from __future__ import annotations

from ..node.entity.actor.ghost import (
    Ghost,
    Blinky,
    Pinky,
    Inky,
    Clyde,
    Winky
)
from ..node.entity.actor.pacman import PacMan
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
        pacmen: list[PacMan],
        ghost_names: tuple[str, str, str, str] = _DEFAULT_GHOSTS,
        ) -> list[Ghost]:
    """Create the four ghosts, one in each corner of the maze.

    Parameters
    ----------
    maze: Maze
        Maze to spawn in.
    pacmen: list[PacMan]
        Who the ghosts hunt.
    ghost_names: tuple[str, str, str, str], optional
        Names of the ghosts to spawn.
        By default `"blinky"`, `"pinky"`, `"inky"`, and `"clyde"`.

    Returns
    -------
    list[Ghost]
        A sprite group holding the four ghosts.
    """
    result = []

    for i, ghost_name in enumerate(ghost_names):
        factory = _NAME_TO_GHOST[ghost_name]
        result.append(factory(maze.corners[i], maze, pacmen, result))
    return result
