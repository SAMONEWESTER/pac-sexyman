"""Inky, the cyan ghost: the unpredictable one."""

from __future__ import annotations
from typing import TYPE_CHECKING, Any

from pygame.sprite import AbstractGroup, Group

from ....config import tuning
from ....grid import Cell
from ..pac_man import PacMan
from .ghost import Ghost

if TYPE_CHECKING:
    from ....level import Maze


class Inky(Ghost):
    """Teams up with a partner ghost to trap Pac-Man from the other side.

    Inky takes the cell a little in front of Pac-Man and mirrors his
    partner (Blinky) around it. The closer Blinky gets, the closer Inky
    aims, so the two squeeze Pac-Man between them.

    Args:
        maze: The maze the ghost moves in.
        cell: The corner the ghost starts and respawns in.
        pac_man: Who to hunt.
        points: Score for eating the ghost while it is frightened.
        partner: The ghost Inky mirrors, normally Blinky.
        *groups: Sprite groups to add the ghost to.
    """

    NAME = 'inky'
    TUNING = tuning.INKY

    def init__(
            self,
            maze: Maze,
            cell: Cell,
            pacmen: Group[PacMan],
            points: int,
            ghosts: Group[Ghost],
            *groups: AbstractGroup[Any],
            ) -> None:
        super().__init__(maze, cell, pacmen, points, ghosts, *groups)
        for ghost in ghosts:
            if ghost.partner is None:
                self.partner = ghost
                ghost.partner = self
                break

    def chase_target(self, closest_pac_man: PacMan) -> Cell:
        """The partner's cell, mirrored around the cell ahead of Pac-Man."""
        x, y = closest_pac_man.cell
        facing = closest_pac_man.facing
        pivot_x, pivot_y = x + facing.dx * 2, y + facing.dy * 2
        partner_x, partner_y = self.ghosts.sprites()[0].cell
        return 2 * pivot_x - partner_x, 2 * pivot_y - partner_y
