"""Abstract base class for entities that move from cell to cell."""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, Any

from pygame import Surface, Vector2
from pygame.sprite import AbstractGroup

from ...config import TILE_SIZE
from ...grid import Cell, Direction, cell_center
from ..entity import Entity

if TYPE_CHECKING:
    # Only for type hints: importing level at runtime would be circular.
    from ...level import Maze

MOVE_DIRECTIONS: tuple[Direction, ...] = (
    Direction.UP, Direction.LEFT, Direction.DOWN, Direction.RIGHT)
"""The four real directions, in the classic tie-break order."""


class Living(Entity, ABC):
    """An entity that moves through the maze, one cell at a time.

    Movement is tile-based: the entity glides from cell center to cell
    center and only decides where to go when it reaches a center.

    ``update`` is a template: it moves, then animates, then places the
    sprite. Subclasses fill in the two abstract steps:

    * ``choose_direction``: where to go next, asked at every cell center.
    * ``animate``: which image to show this frame.

    Args:
        image: What the entity looks like at the start.
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
        self.pos = cell_center(cell)
        self.direction = Direction.NONE
        self.speed = speed
        self.lag = 0.0

    # The two steps every subclass must fill in.
    # -------------------------------------------------------------------------
    @abstractmethod
    def choose_direction(self) -> Direction:
        """Pick the next direction. Called at every cell center.

        Returns:
            Where to go next; ``Direction.NONE`` (or a blocked
            direction) means: stand still.
        """

    @abstractmethod
    def animate(self, dt: float, elapsed: float) -> None:
        """Set ``self.image`` for this frame.

        Args:
            dt: Seconds since the previous frame.
            elapsed: Seconds since the game started.
        """

    # The template.
    # -------------------------------------------------------------------------
    def update(self, dt: float, elapsed: float) -> None:
        """Move, animate, then place the sprite at the new position.

        Args:
            dt: Seconds since the previous frame.
            elapsed: Seconds since the game started.
        """
        self.move(dt)
        self.animate(dt, elapsed)
        self.place()

    # Movement.
    # -------------------------------------------------------------------------
    @property
    def at_center(self) -> bool:
        """Whether the entity sits exactly on its cell's center."""
        return self.pos == cell_center(self.cell)

    @property
    def next_cell(self) -> Cell:
        """The cell the entity is heading to."""
        return (self.cell[0] + self.direction.dx,
                self.cell[1] + self.direction.dy)

    def can_move(self, direction: Direction) -> bool:
        """Whether there is no wall between this cell and the next one.

        Args:
            direction: The direction to check.
        """
        if direction is Direction.NONE:
            return False
        x, y = self.cell
        return not self.maze[y][x] & direction.wall

    def move(self, dt: float) -> None:
        """Glide ``speed * dt`` cells, turning at every center passed.

        Works for any frame rate: a big ``dt`` may pass several centers,
        and the entity still decides at each one.

        Args:
            dt: Seconds since the previous frame.
        """
        self.lag -= dt
        if self.lag > 0.0:
            dt *= 0.75
        remaining = self.speed * TILE_SIZE * dt
        while remaining > 0:
            if self.at_center:
                # Snap exactly: Vector2 == allows tiny float differences.
                self.pos = cell_center(self.cell)
                wanted = self.choose_direction()
                self.direction = (
                    wanted if self.can_move(wanted) else Direction.NONE)
                if self.direction is Direction.NONE:
                    return
            target = cell_center(self.next_cell)
            distance = self.pos.distance_to(target)
            if remaining < distance:
                step = Vector2(self.direction.dx, self.direction.dy)
                self.pos += step * remaining
                return
            self.pos = target
            self.cell = self.next_cell
            remaining -= distance

    def reverse(self) -> None:
        """Turn around on the spot, even halfway between two cells."""
        if self.direction is Direction.NONE:
            return
        if not self.at_center:
            # Heading A -> B becomes heading B -> A.
            self.cell = self.next_cell
        self.direction = self.direction.opposite

    def place(self) -> None:
        """Put the sprite's rect on ``pos``, sized to the current image."""
        center = (round(self.pos.x), round(self.pos.y))
        self.rect = self.image.get_rect(center=center)

    def respawn(self) -> None:
        """Go back to the spawn cell and stand still."""
        self.cell = self.spawn_cell
        self.pos = cell_center(self.cell)
        self.direction = Direction.NONE
        self.place()
