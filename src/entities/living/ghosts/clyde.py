"""Clyde, the orange ghost: the shy one."""

import math

from ..pac_man import PacMan

from ....config import tuning
from ....grid import Cell
from .ghost import Ghost


class Clyde(Ghost):
    """Chases Pac-Man from afar, but runs home when he gets too close."""

    NAME = 'clyde'
    TUNING = tuning.CLYDE

    def chase_target(self, closest_pac_man: PacMan) -> Cell:
        """Pac-Man's cell when far away, Clyde's own corner when close."""
        pac_cell = closest_pac_man.cell
        if math.dist(self.cell, pac_cell) > 6:
            return pac_cell
        return self.spawn_cell
