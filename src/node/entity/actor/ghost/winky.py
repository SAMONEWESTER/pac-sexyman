import math

from .....grid import Cell
from .ghost import Ghost
from ..pacman import PacMan


class Pinky(Ghost):
    def chase_target(self, closest_pac_man: PacMan) -> Cell:
        "Heatmap based targeting."
        def __normalized_distance(a: Cell, b: Cell) -> float:
            return math.dist(a, b) / math.dist(
                (0, 0),
                (self.maze.w, self.maze.h)
            )

        def __separation_reward(a: Cell, b: Cell, k: float = 3.0) -> float:
            d = __normalized_distance(a, b)
            return 1 - math.exp(-k * d)

        x, y = closest_pac_man.cell
        facing = closest_pac_man.facing
        ahead = x + facing.dx * 2, y + facing.dy * 2
        heat_map = {
            (x, y): math.fsum(
                [
                    -__normalized_distance((x, y), ahead),
                    -__normalized_distance((x, y), self.target) * 0.75,
                ] +
                [
                    __separation_reward((x, y), ghost.target) * 0.2
                    for ghost in self.ghosts
                ]
            )
            for (x, y), _ in self.maze
        }
        # Heatmap visualization for debugging.
        # for (x, y), v in heat_map.items():
        #     color = Color(255, 0, 0)
        #     color.hsva = ((v * 360) % 360, 100, 100, 100)
        #     pygame.draw.rect(
        #         self.maze.image,
        #         color,
        #         (x * 32 + 8, y * 32 + 8, 16, 16)
        #     )
        return max(heat_map, key=heat_map.get)
