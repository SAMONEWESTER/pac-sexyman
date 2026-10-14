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
        mazegen = MazeGenerator(size, True, seed=seed)
        self.maze = mazegen.maze
        self.size = size

        self._open_dead_ends(self._get_protected_cells())

        # Initializing the maze graphics.
        self.image = Surface((self.w * 32, self.h * 32))
        self.rect = self.image.get_rect()
        for y, row in enumerate(self.maze):
            for x, cell in enumerate(row):
                self.image.blit(tiles[cell], (x * 32, y * 32))
        self.image.fill(color, special_flags=BLEND_MULT)

    def _get_protected_cells(self) -> set[tuple[int, int]]:
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

    def _open_dead_ends(self, protected_cells: set[tuple[int, int]]) -> None:
        # Opening the maze corners, so they're never dead ends.
        self.maze[0][0] &= 9
        self.maze[self.w - 1][0] &= 3
        self.maze[0][self.h - 1] &= 12
        self.maze[self.w - 1][self.h - 1] &= 6

        # Opening all dead ends into straight corridors.
        for y, row in enumerate(self.maze):
            for x, cell in enumerate(row):
                if cell == 7 and self.maze[y][x + 1] not in protected_cells:
                    self.maze[y][x] = 5
                    self.maze[y][x + 1] &= 7
                elif cell == 11 and self.maze[y - 1][x] not in protected_cells:
                    self.maze[y][x] = 10
                    self.maze[y - 1][x] &= 11
                elif cell == 13 and self.maze[y][x - 1] not in protected_cells:
                    self.maze[y][x] = 5
                    self.maze[y][x - 1] &= 13
                elif cell == 14 and self.maze[y + 1][x] not in protected_cells:
                    self.maze[y][x] = 10
                    self.maze[y + 1][x] &= 14

    @property
    def w(self) -> int:
        return self.size[0]

    @property
    def h(self) -> int:
        return self.size[1]
