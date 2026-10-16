"""The player character."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from pygame.sprite import AbstractGroup

from ...config import PAC_MAN_SPEED
from ...grid import Cell
from ...resources import ASSETS
from .living import Living

if TYPE_CHECKING:
    from ...level import Maze

CHOMP_FRAMES: tuple[int, ...] = (0, 1, 2, 1)
"""Order of the mouth frames in one chomp."""

CHOMPS_PER_SECOND: float = 3.0


class PacMan(Living):
    """Pac-Man, steered by the player.

    Args:
        maze: The maze Pac-Man moves in.
        cell: The cell Pac-Man starts and respawns in.
        *groups: Sprite groups to add Pac-Man to.
    """

    def __init__(
            self,
            maze: Maze,
            cell: Cell,
            *groups: AbstractGroup[Any],
            ) -> None:
        super().__init__(ASSETS.pac_man[0], maze, cell, PAC_MAN_SPEED,
                         *groups)

    def update(self, dt: float, elapsed: float) -> None:
        """Play the chomp animation. Movement comes in a later step.

        Args:
            dt: Seconds since the previous frame (unused for now).
            elapsed: Seconds since the game started.
        """
        step = int(elapsed * CHOMPS_PER_SECOND * len(CHOMP_FRAMES))
        self.image = ASSETS.pac_man[CHOMP_FRAMES[step % len(CHOMP_FRAMES)]]
