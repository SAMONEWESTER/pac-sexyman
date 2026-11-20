"""Abstract base class for entities that move from cell to cell."""

from __future__ import annotations

from abc import abstractmethod
from typing import TYPE_CHECKING

from pygame import Vector2

from ....config import TILE_SIZE
from ....grid import Cell, Direction
from ..entity import Entity
from ..collider import Collider, CollisionLayer
from ...utils import get_time

if TYPE_CHECKING:
    from ....level import Maze


class Actor(Entity):
    """Acting entity that moves through the maze, one cell at a time.

    Movement is tile-based: the entity glides from cell center to cell
    center and only decides where to go when it reaches a center.

    Subclasses fill in ``choose_direction``:
    where to go next, asked at every cell center.

    Parameters
    ----------
    cell: Cell
        Cell the entity starts and respawns in.
    maze: Maze
        Maze the entity moves in.
    speed: float
        Movement speed, in cells per second.
    """
    def __init__(
            self,
            cell: Cell,
            maze: Maze,
            speed: float,
            ) -> None:
        super().__init__()
        self.offset.update(maze.cell_center(cell))
        self.spawn_cell = cell
        self.cell = cell
        self.maze = maze
        self.speed = speed

        col = Collider(Vector2(8, 8))
        col.owner = self
        col.layer = CollisionLayer.PACMAN
        col.mask = CollisionLayer.ITEM | CollisionLayer.GHOST
        self.add_child(col)

        

        self.direction = Direction.NONE
        self.speed_multiplier = 1.0
        self.lag = 0.0

    @abstractmethod
    def choose_direction(self) -> Direction:
        """Pick the next direction. Called at every cell center.

        Returns
        -------
        Direction
            Where to go next.
            ``Direction.NONE`` (or a blocked direction) means: stand still.
        """

    def update(self, dt: float) -> bool:
        if not self.active:
            return False
        self.move(dt)
        return super().update(dt)

    @property
    def at_center(self) -> bool:
        "Whether the entity sits exactly on its cell's center."
        return self.offset == self.maze.cell_center(self.cell)

    @property
    def next_cell(self) -> Cell:
        "The cell the entity is heading to."
        return (self.cell[0] + self.direction.dx,
                self.cell[1] + self.direction.dy)

    def move(self, dt: float) -> None:
        """Glide ``speed * dt`` cells, turning at every center passed.

        Works for any frame rate: a big ``dt`` may pass several centers,
        and the entity still decides at each one.

        Parameters
        ----------
        dt : float
            Seconds since the previous frame.
        """
        self.lag -= dt
        if self.lag > 0.0:
            dt *= 0.5
        remaining = self.speed * TILE_SIZE * dt * self.speed_multiplier
        while remaining > 0:
            if self.at_center:
                # Snap exactly: Vector2 == allows tiny float differences.
                self.offset.update(self.maze.cell_center(self.cell))
                wanted = self.choose_direction()
                self.direction = (
                    wanted if self._can_move(wanted) else Direction.NONE)
                if self.direction is Direction.NONE:
                    return
            target = self.maze.cell_center(self.next_cell)
            distance = self.offset.distance_to(target)
            if remaining < distance:
                step = Vector2(self.direction.dx, self.direction.dy)
                self.offset += step * remaining
                return
            self.offset.update(target)
            self.cell = self.next_cell
            remaining -= distance

    def reverse(self) -> None:
        "Turn around on the spot, even halfway between two cells."
        if self.direction is Direction.NONE:
            return
        if not self.at_center:
            # Heading A -> B becomes heading B -> A.
            self.cell = self.next_cell
        self.direction = self.direction.opposite

    def respawn(self) -> None:
        "Go back to the spawn cell and stand still."
        self.cell = self.spawn_cell
        self.offset.update(self.maze.cell_center(self.cell))
        self.direction = Direction.NONE
        self.start_time = get_time()

    def _can_move(self, direction: Direction) -> bool:
        """Whether there is no wall between this cell and the next one.

        Parameters
        ----------
        direction : Direction
            Direction to check.
        """
        if direction is Direction.NONE:
            return False
        return not self.maze[self.cell] & direction.wall
