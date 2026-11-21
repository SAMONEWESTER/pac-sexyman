from .....grid import Cell
from .ghost import Ghost
from ..pacman import PacMan


class Blinky(Ghost):
    def chase_target(self, closest_pac_man: PacMan) -> Cell:
            """Pac-Man's own cell."""
            return closest_pac_man.cell
