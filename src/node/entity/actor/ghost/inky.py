from .....grid import Cell
from .ghost import Ghost
from ..pacman import PacMan


class Inky(Ghost):
    def __init__(self, cell, maze, pacmen, ghosts):
        super().__init__(cell, maze, pacmen, ghosts)
        for ghost in ghosts:
            if ghost.partner is None:
                self.partner = ghost
                ghost.partner = self
                return
        self.partner = self

    def chase_target(self, closest_pac_man: PacMan) -> Cell:
        "The partner's cell, mirrored around the cell ahead of Pac-Man."
        x, y = closest_pac_man.cell
        facing = closest_pac_man.facing
        pivot_x, pivot_y = x + facing.dx * 2, y + facing.dy * 2
        partner_x, partner_y = self.partner.cell
        return 2 * pivot_x - partner_x, 2 * pivot_y - partner_y
