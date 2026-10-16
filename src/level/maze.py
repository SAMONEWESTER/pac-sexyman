"""The maze sprite, built on top of the external maze generator."""

from __future__ import annotations

from collections.abc import Iterator
from itertools import chain
from typing import Any

from mazegenerator import MazeGenerator
from pygame import BLEND_MULT, Color, Surface
from pygame.sprite import AbstractGroup, Sprite

from ..config import TILE_SIZE
from ..errors import MazeError
from ..grid import Cell

CLOSED_CELL: int = 15
"""A cell with all four walls: part of the 42 pattern."""


class Maze(Sprite):
    """Wrapper around the maze generator class, for ease of use.

    Further transforms the maze layout to make it compliant with
    A-Maze-ing specification, and uses a different imperfect maze algorithm.

    Each cell is a 4-bit wall mask, and ``15`` marks a fully closed cell
    that belongs to the 42 pattern.

    Args:
        tiles: One tile image per wall mask, indexed 0 to 15.
        color: Tint applied to the whole maze.
        size: Width and height of the maze, in cells.
        seed: Generator seed, ``0`` for a random maze.
        *groups: Sprite groups to add the maze to.

    Raises:
        MazeError: If the external maze generator fails.
    """

    def __init__(
            self,
            tiles: tuple[Surface, ...],
            color: Color,
            size: tuple[int, int] = (15, 15),
            seed: int = 0,
            *groups: AbstractGroup[Any],
            ) -> None:
        super().__init__(*groups)
        try:
            mazegen = MazeGenerator(size, True, seed=seed)
        except Exception as err:  # External package: it may raise anything.
            raise MazeError(
                f'the maze generator failed for a {size[0]}x{size[1]} maze'
            ) from err
        self.maze: list[list[int]] = mazegen.maze
        self.size = size

        # Making the maze nicer with post-processing.
        self._open_corners()
        self._open_dead_ends(self._get_protected_cells())

        # Initializing the maze graphics.
        self.image = Surface((size[0] * TILE_SIZE, size[1] * TILE_SIZE))
        self.rect = self.image.get_rect()
        for (x, y), cell in self:
            self.image.blit(tiles[cell], (x * TILE_SIZE, y * TILE_SIZE))
        self.image.fill(color, special_flags=BLEND_MULT)

    def rows(self) -> Iterator[list[int]]:
        """Iterate over rows."""
        return iter(self.maze)

    def cells(self) -> Iterator[int]:
        """Iterate over cell values, row by row."""
        for row in self.maze:
            yield from row

    def __iter__(self) -> Iterator[tuple[tuple[int, int], int]]:
        """Iterate over ``((x, y), cell)`` pairs."""
        for y, row in enumerate(self.maze):
            for x, cell in enumerate(row):
                yield (x, y), cell

    def __getitem__(self, key: int) -> list[int]:
        """Get a row from the maze."""
        return self.maze[key]

    def _get_protected_cells(self) -> set[tuple[int, int]]:
        """Return cells that should not be modified by post-processing."""
        # Cells just outside the maze borders.
        result = set(chain(
            ((x, -1) for x in range(self.w)),
            ((-1, y) for y in range(self.h)),
            ((x, self.h) for x in range(self.w)),
            ((self.w, y) for y in range(self.h)),
        ))

        # Cells part of the 42 pattern.
        for (x, y), cell in self:
            if cell == CLOSED_CELL:
                result.add((x, y))
        return result

    def _open_corners(self) -> None:
        """Open the maze corners, so they are never dead ends."""
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
        """Open all dead ends into straight corridors."""
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
        """Width of the maze, in cells."""
        return self.size[0]

    @property
    def h(self) -> int:
        """Height of the maze, in cells."""
        return self.size[1]

    @property
    def corners(self) -> tuple[Cell, Cell, Cell, Cell]:
        """The four corner cells: top left, top right, bottom left/right."""
        right, bottom = self.w - 1, self.h - 1
        return (0, 0), (right, 0), (0, bottom), (right, bottom)

    def is_open(self, cell: Cell) -> bool:
        """Whether a cell can be entered (not part of the 42 pattern)."""
        x, y = cell
        return self.maze[y][x] != CLOSED_CELL

    def nearest_open_cell(self, target: Cell) -> Cell:
        """Return the open cell closest to ``target``.

        Args:
            target: The wanted cell, which may be closed.
        """
        def distance(cell: Cell) -> int:
            return (cell[0] - target[0]) ** 2 + (cell[1] - target[1]) ** 2

        open_cells = (cell for cell, _ in self if self.is_open(cell))
        return min(open_cells, key=distance)
