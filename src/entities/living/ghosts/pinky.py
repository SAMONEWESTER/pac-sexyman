"""Pinky, the pink ghost: the ambusher."""

from ....config import tuning
from ....grid import Cell
from .ghost import Ghost


class Pinky(Ghost):
    """Aims a few cells in front of Pac-Man, to cut him off."""

    NAME = 'pinky'
    TUNING = tuning.PINKY

    def chase_target(self) -> Cell:
        """``PINKY_LOOK_AHEAD`` cells ahead of where Pac-Man faces."""
        x, y = self.pac_men[0].cell
        facing = self.pac_men[0].facing
        ahead = tuning.PINKY_LOOK_AHEAD
        return x + facing.dx * ahead, y + facing.dy * ahead
