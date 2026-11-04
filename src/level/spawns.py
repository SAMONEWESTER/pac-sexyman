"""Placing Pac-Man and the ghosts at their start positions."""

from __future__ import annotations

from pygame.sprite import Group

from ..entities import Blinky, Clyde, Ghost, Inky, PacMan, Pinky
from .maze import Maze


_DEFAULT_GHOSTS = ('blinky', 'pinky', 'inky', 'clyde')

_NAME_TO_GHOST = {
    'blinky': Blinky,
    'pinky': Pinky,
    'inky': Inky,
    'clyde': Clyde,
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
    partnered_ghosts = [False, False, False, False]

    for i, ghost_name in enumerate(ghost_names):
        if ghost_name == 'inky':
            # Inky needs a partner to mirror, so find the first ghost that
            # has already been spawned and give it to Inky.
            partnered_ghosts[i] = True
            for j, partnered in enumerate(partnered_ghosts):
                if partnered:
                    continue
                partnered_ghosts[j] = True
                break
            if j >= i:
                raise ValueError("Inky tried to partner with itself"
                                 " or a ghost after it in the queue.")
            result.add(Inky(
                maze,
                maze.corners[i],
                pac_men,
                points,
                result.sprites()[j]))
            continue
        ghost_factory = _NAME_TO_GHOST[ghost_name]
        result.add(ghost_factory(maze, maze.corners[i], pac_men, points))
    return result
