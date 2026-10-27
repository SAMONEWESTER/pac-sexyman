"""The maze sprite, built on top of the external maze generator."""

from __future__ import annotations

from collections import deque
from collections.abc import Iterator
from typing import Any, overload

from mazegenerator import MazeGenerator
from pygame import Surface
from pygame.sprite import AbstractGroup, Sprite

from ..config import TILE_SIZE
from ..errors import MazeError
from ..grid import Cell, Direction
from ..resources import ASSETS

WALKING_DIRECTIONS: tuple[Direction, ...] = (
    Direction.UP, Direction.RIGHT, Direction.DOWN, Direction.LEFT)


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
            size: tuple[int, int] = (15, 15),
            theme: int = 0,
            seed: int = 0,
            *groups: AbstractGroup[Any],
            ) -> None:
        super().__init__(*groups)
        try:
            mazegen = MazeGenerator(size, False, seed=seed)
        except Exception as err:  # External package: it may raise anything.
            raise MazeError(
                f'the maze generator failed for a {size[0]}x{size[1]} maze'
            ) from err
        self.maze = mazegen.maze
        self.size = size
        self.theme = theme

        # Special cell coordinates.
        self.borders = \
            {(x, -1) for x in range(self.w)} | \
            {(-1, y) for y in range(self.h)} | \
            {(x, self.h) for x in range(self.w)} | \
            {(self.w, y) for y in range(self.h)}
        self.closed_cells = set(
            (x, y) for (x, y), cell in self if cell == 15)
        self.corners = (
            (0, 0), (self.w - 1, 0), (0, self.h - 1), (self.w - 1, self.h - 1))

        # Making the maze nicer with post-processing.
        self._open_corners()
        self._open_dead_ends(self.borders | self.closed_cells)

        # Cell types stored for convenience.
        self.intersections = set(
            (x, y) for (x, y), cell in self if not cell)
        self.junctions = set(
            (x, y) for (x, y), cell in self if cell in {1, 2, 4, 8})
        self.corridors = set(
            (x, y) for (x, y), cell in self if cell in {5, 10})
        self.bends = set(
            (x, y) for (x, y), cell in self if cell in {3, 6, 9, 12})
        self.dead_ends = set(
            (x, y) for (x, y), cell in self if cell in {7, 11, 13, 14})

        # Initializing the maze graphics.
        self.image = Surface((size[0] * TILE_SIZE, size[1] * TILE_SIZE))
        self.rect = self.image.get_rect()
        tileset = ASSETS.tilesets[theme]
        for (x, y), cell in self:
            self.image.blit(tileset[cell], (x * TILE_SIZE, y * TILE_SIZE))

    def __iter__(self) -> Iterator[tuple[tuple[int, int], int]]:
        """Iterate over ``((x, y), cell)`` pairs."""
        for y, row in enumerate(self.maze):
            for x, cell in enumerate(row):
                yield (x, y), cell

    @overload
    def __getitem__(self, k: int) -> list[int]: ...

    @overload
    def __getitem__(self, k: tuple[int, int]) -> int: ...

    def __getitem__(self, k: int | tuple[int, int]) -> list[int] | int:
        """Get a row or cell from the maze."""
        if isinstance(k, int):
            return self.maze[k]
        return self.maze[k[1]][k[0]]

    @overload
    def __setitem__(self, k: int, v: list[int]) -> None: ...

    @overload
    def __setitem__(self, k: tuple[int, int], v: int) -> None: ...

    def __setitem__(
            self,
            k: int | tuple[int, int],
            v: list[int] | int
            ) -> None:
        """Set a row or cell in the maze."""
        if isinstance(k, int):
            self.maze[k] = v
        self.maze[k[1]][k[0]] = v

    def _open_corners(self) -> None:
        """Open the maze corners, so they are never dead ends."""
        # Top left.
        self[0, 0] &= 9
        self[1, 0] &= 7
        self[0, 1] &= 14

        # Top right.
        self[self.w - 1, 0] &= 3
        self[self.w - 2, 0] &= 13
        self[self.w - 1, 1] &= 14

        # Bottom left.
        self[0, self.h - 1] &= 12
        self[1, self.h - 1] &= 7
        self[0, self.h - 2] &= 11

        # Bottom right.
        self[self.w - 1, self.h - 1] &= 6
        self[self.w - 2, self.h - 1] &= 13
        self[self.w - 1, self.h - 2] &= 11

    def _open_dead_ends(self, protected_cells: set[tuple[int, int]]) -> None:
        """Open all dead ends into straight corridors."""
        for (x, y), cell in self:
            if cell == 7 and (x + 1, y) not in protected_cells:
                self[x, y] = 5
                self[x + 1, y] &= 7
            elif cell == 11 and (x, y - 1) not in protected_cells:
                self[x, y] = 10
                self[x, y - 1] &= 11
            elif cell == 13 and (x - 1, y) not in protected_cells:
                self[x, y] = 5
                self[x - 1, y] &= 13
            elif cell == 14 and (x, y + 1) not in protected_cells:
                self[x, y] = 10
                self[x, y + 1] &= 14

    @property
    def w(self) -> int:
        """Width of the maze, in cells."""
        return self.size[0]

    @property
    def h(self) -> int:
        """Height of the maze, in cells."""
        return self.size[1]

    def nearest_open_cell(self, target: Cell) -> Cell:
        """Return the open cell closest to ``target``.

        Args:
            target: The wanted cell, which may be closed.
        """
        def distance(cell: Cell) -> int:
            return (cell[0] - target[0]) ** 2 + (cell[1] - target[1]) ** 2

        return min(
            ((x, y) for (x, y), _ in self if (x, y) not in self.closed_cells),
            key=distance
        )

    def distances_from(self, start: Cell) -> dict[Cell, int]:
        """Walking distance, in cells, from ``start`` to every reachable cell.

        A breadth-first search that only passes through open walls.

        Args:
            start: Where to measure from.
        """
        result = {start: 0}
        queue = deque([start])
        while queue:
            x, y = queue.popleft()
            for d in WALKING_DIRECTIONS:
                if self[x, y] & d.wall:
                    continue
                neighbour = (x + d.dx, y + d.dy)
                if neighbour not in result:
                    result[neighbour] = result[(x, y)] + 1
                    queue.append(neighbour)
        return result
