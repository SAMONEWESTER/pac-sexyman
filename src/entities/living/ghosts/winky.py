"""Winky, the lavender ghost: the hunter."""

# import pygame
# from pygame import Color

from ..pac_man import PacMan

from ....config import tuning
from ....grid import Cell
from .ghost import Ghost, distance_squared


class Winky(Ghost):
    """Goes straight for the cell Pac-Man is in."""

    NAME = 'winky'
    TUNING = tuning.WINKY

    def chase_target(self, closest_pac_man: PacMan) -> Cell:
        """Pac-Man's own cell."""
        x, y = closest_pac_man.cell
        facing = closest_pac_man.facing
        ahead = x + facing.dx * 2, y + facing.dy * 2
        heat_map: dict[tuple[int, int], float] = {
            (x, y): sum(
                [
                    -distance_squared((x, y), ahead),
                    -distance_squared((x, y), self.target) * 0.75
                ] +
                [
                    distance_squared((x, y), ghost.target) * 0.1875
                    for ghost in self.ghosts
                ]
            )
            for (x, y), _ in self.maze
        }
        # Heatmap visualization for debugging.
        # for (x, y), v in heat_map.items():
        #     color = Color(255, 0, 0)
        #     color.hsva = ((v * 2) % 360, 100, 100, 100)
        #     pygame.draw.rect(
        #         self.maze.image,
        #         color,
        #         (x * 32 + 8, y * 32 + 8, 16, 16)
        #     )
        return max(heat_map, key=heat_map.get)
