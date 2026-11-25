from .....grid import Cell
from .ghost import Ghost
from ..pacman import PacMan

from .....level import Maze


class Blinky(Ghost):
    def __init__(
            self,
            cell: Cell,
            maze: Maze,
            pacmen: list[PacMan],
            ghosts: list[Ghost]
            ) -> None:
        super().__init__(cell, maze, pacmen, ghosts)
        self.speed *= 1.2

    def chase_target(self, closest_pac_man: PacMan) -> Cell:
        "Pac-Man's own cell."
        return closest_pac_man.cell
