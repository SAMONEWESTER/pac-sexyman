import math

from .....grid import Cell
from .ghost import Ghost
from ..pacman import PacMan


class Clyde(Ghost):
    def chase_target(self, closest_pac_man: PacMan) -> Cell:
        "Pac-Man's cell when far away, Clyde's own corner when close."
        pac_cell = closest_pac_man.cell
        if math.dist(self.cell, pac_cell) > 6:
            return pac_cell
        return self.spawn_cell
