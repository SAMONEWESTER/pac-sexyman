"""Abstract base class for entities that move from cell to cell."""

from __future__ import annotations

from abc import ABC
from typing import TYPE_CHECKING, Any

from pygame import Surface
from pygame.sprite import AbstractGroup

from ...grid import Cell, Direction, cell_center
from ..entity import Entity

if TYPE_CHECKING:
    # Only for type hints: importing level at runtime would be circular.
    from ...level import Maze


class Living(Entity, ABC):
    """An entity that moves through the maze, one cell at a time.

    Movement is tile-based: the entity sits in ``cell``, heads in
    ``direction`` and can only turn at cell centers. Walls come straight
    from the maze's cell bits, see ``can_move``.

    Still abstract: subclasses must implement ``update``.

    Args:
        image: What the entity looks like.
        maze: The maze the entity moves in.
        cell: The cell the entity starts and respawns in.
        speed: Movement speed, in cells per second.
        *groups: Sprite groups to add the entity to.
    """

    def __init__(
            self,
            image: Surface,
            maze: Maze,
            cell: Cell,
            speed: float,
            *groups: AbstractGroup[Any],
            ) -> None:
        super().__init__(image, cell_center(cell), *groups)
        self.maze = maze
        self.spawn_cell = cell
        self.cell = cell
        self.direction = Direction.NONE
        self.speed = speed

    def can_move(self, direction: Direction) -> bool:
        """Whether there is no wall between this cell and the next one.

        Args:
            direction: The direction to check.
        """
        if direction is Direction.NONE:
            return False
        x, y = self.cell
        return not self.maze[y][x] & direction.wall

    def respawn(self) -> None:
        """Go back to the spawn cell and stand still."""
        self.cell = self.spawn_cell
        self.direction = Direction.NONE
        center = cell_center(self.cell)
        self.rect.center = (round(center.x), round(center.y))
