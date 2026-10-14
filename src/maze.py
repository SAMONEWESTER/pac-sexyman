from itertools import chain
from collections.abc import Iterator

from pygame import Surface, Color, BLEND_MULT
from pygame.sprite import Sprite

from mazegenerator import MazeGenerator


class Maze(Sprite):
    """Wrapper around the maze generator class, for ease of use.
    Further transforms the maze layout to make it compliant with
    A-Maze-ing specification, and uses a different imperfect maze algorithm."""
    def __init__(
            self,
            tiles: tuple[Surface],
            color: Color,
            size: tuple[int, int] = (15, 15),
            seed: int = 0
            ):
        super().__init__()
        mazegen = MazeGenerator(size, True, seed=seed)
        self.maze = mazegen.maze
        self.size = size

        # Making the maze nicer with post-processing.
        self._open_corners()
        self._open_dead_ends(self._get_protected_cells())

        # Initializing the maze graphics.
        self.image = Surface((size[0] * 32, size[1] * 32))
        self.rect = self.image.get_rect()
        for (x, y), cell in self:
            self.image.blit(tiles[cell], (x * 32, y * 32))
        self.image.fill(color, special_flags=BLEND_MULT)

    def rows(self) -> Iterator[list[int]]:
        "Iterate over rows."
        return iter(self.maze)

    def cells(self) -> Iterator[int]:
        "Iterate over cell values, row by row."
        for row in self.maze:
            yield from row

    def __iter__(self) -> Iterator[tuple[tuple[int, int], int]]:
        "Iterate over `((x, y), cell)` pairs."
        for y, row in enumerate(self.maze):
            for x, cell in enumerate(row):
                yield (x, y), cell

    def __getitem__(self, key: int) -> list[int]:
        "Get a row from the maze."
        return self.maze[key]

    def _get_protected_cells(self) -> set[tuple[int, int]]:
        "Returns cells that should not be modified by maze post-processing."
        # Cells just outside the maze borders.
        result = set(chain(
            ((x, -1) for x in range(self.w)),
            ((-1, y) for y in range(self.h)),
            ((x, self.h) for x in range(self.w)),
            ((self.w, y) for y in range(self.h)),
        ))

        # Cells part of the 42 pattern.
        for (x, y), cell in self:
            if cell == 15:
                result.add((x, y))
        return result

    def _open_corners(self) -> None:
        "Opens the maze corners, so they're never dead ends."
        # Top left.
        self[0][0] &= 9
        self[0][1] &= 7
        self[1][0] &= 14

        # Top right.
        self[0][self.w - 1] &= 3
        self[0][self.w - 2] &= 13
        self[1][self.w - 1] &= 14

        # Bottom left.
        self[self.h - 1][0] &= 12
        self[self.h - 1][1] &= 7
        self[self.h - 2][0] &= 11

        # Bottom right.
        self[self.h - 1][self.w - 1] &= 6
        self[self.h - 1][self.w - 2] &= 13
        self[self.h - 2][self.w - 1] &= 11

    def _open_dead_ends(self, protected_cells: set[tuple[int, int]]) -> None:
        "Opens all dead ends into straight corridors."
        for (x, y), cell in self:
            if cell == 7 and (x + 1, y) not in protected_cells:
                self[y][x] = 5
                self[y][x + 1] &= 7
            elif cell == 11 and (x, y - 1) not in protected_cells:
                self[y][x] = 10
                self[y - 1][x] &= 11
            elif cell == 13 and (x - 1, y) not in protected_cells:
                self[y][x] = 5
                self[y][x - 1] &= 13
            elif cell == 14 and (x, y + 1) not in protected_cells:
                self[y][x] = 10
                self[y + 1][x] &= 14

    @property
    def w(self) -> int:
        return self.size[0]

    @property
    def h(self) -> int:
        return self.size[1]
