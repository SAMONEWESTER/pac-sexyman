from .....grid import Cell
from .ghost import Ghost
from ..pacman import PacMan


class Pinky(Ghost):
    def chase_target(self, closest_pac_man: PacMan) -> Cell:
        "4 cells ahead of where Pac-Man faces."
        x, y = closest_pac_man.cell
        facing = closest_pac_man.facing
        return x + facing.dx * 4, y + facing.dy * 4
