"""Clyde, the orange ghost: the shy one."""

from ....config import tuning
from ....grid import Cell
from .ghost import Ghost, distance_squared


class Clyde(Ghost):
    """Chases Pac-Man from afar, but runs home when he gets too close."""

    NAME = 'clyde'
    TUNING = tuning.CLYDE

    def chase_target(self) -> Cell:
        """Pac-Man's cell when far away, Clyde's own corner when close."""
        pac_cell = self.pac_men[0].cell
        shy = tuning.CLYDE_SHY_DISTANCE
        if distance_squared(self.cell, pac_cell) > shy * shy:
            return pac_cell
        return self.spawn_cell
