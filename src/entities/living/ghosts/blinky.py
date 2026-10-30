"""Blinky, the red ghost: the hunter."""

from ..pac_man import PacMan

from ....config import tuning
from ....grid import Cell
from .ghost import Ghost


class Blinky(Ghost):
    """Goes straight for the cell Pac-Man is in."""

    NAME = 'blinky'
    TUNING = tuning.BLINKY

    def chase_target(self, closest_pac_man: PacMan) -> Cell:
        """Pac-Man's own cell."""
        return closest_pac_man.cell
