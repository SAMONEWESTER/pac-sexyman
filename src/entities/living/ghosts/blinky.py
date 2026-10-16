"""Blinky, the red ghost: the hunter."""

from ....config import tuning
from ....grid import Cell
from .ghost import Ghost


class Blinky(Ghost):
    """Goes straight for the cell Pac-Man is in."""

    NAME = 'blinky'
    TUNING = tuning.BLINKY

    def chase_target(self) -> Cell:
        """Pac-Man's own cell."""
        return self.pac_man.cell
