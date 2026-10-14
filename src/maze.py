from itertools import chain

from pygame import Surface, Color, BLEND_MULT
from pygame.sprite import Sprite

from mazegenerator import MazeGenerator


class Maze(Sprite):
    def __init__(
            self,
            tiles: list[Surface],
            color: Color,
            size: tuple[int, int] = (15, 15),
            seed: int = 0
            ):
        super().__init__()
        mazegen = MazeGenerator(size, seed=seed)
        self.maze = mazegen.maze
        self.size = size

        # Initializing the maze graphics.
        self.image = Surface((self.w * 32, self.h * 32))
        self.rect = self.image.get_rect()
        for y, row in enumerate(self.maze):
            for x, cell in enumerate(row):
                self.image.blit(tiles[cell], (x * 32, y * 32))
        self.image.fill(color, special_flags=BLEND_MULT)

    def _find_protected_cells(self) -> set[tuple[int, int]]:
        """Returns a set of cells that should not
        be modified by maze post-processing."""
        # Cells just outside the maze borders.
        result = set(chain(
            ((x, -1) for x in range(self.w)),
            ((-1, y) for y in range(self.h)),
            ((x, self.h) for x in range(self.w)),
            ((self.w, y) for y in range(self.h)),
        ))

        # Cells part of the 42 pattern.
        for y, row in enumerate(self.maze):
            for x, cell in enumerate(row):
                if cell == 15:
                    result.add((x, y))
        return result

    def _close_loops(self) -> None:
        "Closes loops "

    def _open_corners(self) -> None:
        ...

    def _open_dead_ends(self) -> None:
        ...

    @property
    def w(self) -> int:
        return self.size[0]

    @property
    def h(self) -> int:
        return self.size[1]
