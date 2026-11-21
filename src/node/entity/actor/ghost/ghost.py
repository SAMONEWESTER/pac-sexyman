"""Abstract base class of the four ghosts."""

from __future__ import annotations

from math import pi
from random import random
from abc import abstractmethod
from enum import Enum, auto
from typing import TYPE_CHECKING

from .....grid import Cell, Direction, MOVEMENT_DIRECTIONS
from ..actor import Actor
from ..pacman import PacMan
from ...sprite.world_sprite import WorldSprite
from ...float_animation import FloatAnimation, FloatStyle
from .....resources import ASSETS

if TYPE_CHECKING:
    from .....level import Maze

EYE_FRAMES: dict[Direction, int] = {
    Direction.NONE: 0,
    Direction.DOWN: 0,
    Direction.UP: 1,
    Direction.RIGHT: 2,
    Direction.LEFT: 3,
}
"""Eye frame per look direction as ``(column in sheet, mirrored)``.

``NONE`` is used when Pac-Man is right on top of the ghost.
"""


class GhostState(Enum):
    """What a ghost is doing."""

    CHASE = auto()
    """Hunting Pac-Man: touching him costs a life."""
    FRIGHTENED = auto()
    """Blue and edible, fleeing from Pac-Man."""
    EATEN = auto()
    """Only the eyes are left, moving towards the corner."""


class Ghost(Actor):
    """A ghost. Subclasses only decide where to hunt (``chase_target``).

    At every crossing the ghost takes the open direction (never straight
    back, unless it is a dead end) with the shortest *walk* to its target.
    While frightened it picks the walk farthest from Pac-Man instead.
    Its eyes always look at Pac-Man.

    Walking distance (not straight-line, as in the original arcade game)
    is used because random mazes have long detours where a straight-line
    ghost can circle forever without reaching its target.

    Parameters
    ----------
    cell: Cell
        Maze cell that this ghost starts in.
    maze: Maze
        Maze this ghost belongs to.
    pacmen: list[PacMan]
        Pacmen available as targets.
    ghosts: list[Ghost]
        Ghosts, including itself.
    """
    def __init__(
            self,
            cell: Cell,
            maze: Maze,
            pacmen: list[PacMan],
            ghosts: list[Ghost],
            ) -> None:
        super().__init__(cell, maze, 1.5)
        self.pacmen = pacmen
        self.ghosts = ghosts

        self.target_pacman = pacmen[0]
        self.state = GhostState.CHASE
        self.timer = 0.0
        self.target = (0, 0)
        self.partner: Ghost | None = None

        pivot = FloatAnimation(FloatStyle.FLOAT, pi * 2 * random(), 2.0, 4.0)
        self.add_child(pivot)
        sprite = WorldSprite(ASSETS.ghosts['blinky'].bodies[0])
        self.children[1].add_child(sprite)

    @abstractmethod
    def chase_target(self, closest_pacman: PacMan) -> Cell:
        "The cell this ghost hunts for. Each ghost has its own idea."

    def frighten(self, seconds: float) -> None:
        """Turn blue, become edible, slow down and turn around.

        Parameters
        ----------
        seconds: float
            How long the ghost stays frightened.
        """
        if self.state is GhostState.EATEN:
            return
        self.timer = seconds
        if self.state is GhostState.FRIGHTENED:
            return
        self.state = GhostState.FRIGHTENED
        self.state_speed_multiplier = 0.5
        self.reverse()

    def calm(self) -> None:
        "Back to normal: hunting, dangerous, full speed."
        self.state = GhostState.CHASE
        self.timer = 0.0
        self.state_speed_multiplier = 1.0

    def get_eaten(self) -> None:
        "Pac-Man ate the ghost: only the eyes wait in the corner."
        self.state = GhostState.EATEN
        self.timer = 5.0
        self.state_speed_multiplier = 4.0

    def update(self, dt: float) -> bool:
        if not self.active:
            return False
        if self.state is GhostState.CHASE:
            return super().update(dt)
        self.timer -= dt
        if self.state is GhostState.EATEN and self.cell != self.spawn_cell:
            return super().update(dt)
        if self.timer <= 0:
            self.calm()
        return super().update(dt)

    def choose_direction(self) -> Direction:
        """Pick the best open direction at a crossing, see the class doc."""
        # Find the closest pac-man.
        self.target_pacman = min(
            self.pacmen,
            key=lambda x: self.maze.distances_from(self.cell)[x.cell])

        options = [
            d for d in MOVEMENT_DIRECTIONS
            if self._can_move(d) and d is not self.direction.opposite]
        if not options:  # Dead end: the only way out is back.
            options = [d for d in MOVEMENT_DIRECTIONS if self._can_move(d)]
        if not options:
            return Direction.NONE

        def next_cell(d: Direction) -> Cell:
            return self.cell[0] + d.dx, self.cell[1] + d.dy

        if self.state is GhostState.FRIGHTENED:
            from_pac_man = self.maze.distances_from(self.target_pacman.cell)
            return max(
                options, key=lambda d: from_pac_man.get(next_cell(d), 0))

        # Targets may lie outside the maze or inside the 42: snap them.
        if self.state is GhostState.EATEN:
            if self.cell == self.spawn_cell:
                return Direction.NONE
            self.target = self.maze.nearest_open_cell(self.spawn_cell)
        else:
            self.target = self.maze.nearest_open_cell(
                self.chase_target(self.target_pacman))
        to_target = self.maze.distances_from(self.target)
        unreachable = self.maze.w * self.maze.h
        wishdir = min(
            options, key=lambda d: to_target.get(next_cell(d), unreachable))
        if wishdir != self.direction:
            self.lag = 0.2
        return wishdir
