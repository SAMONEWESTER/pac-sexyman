"""The player character."""

from __future__ import annotations

from math import pi
from random import random
from typing import TYPE_CHECKING

from ....grid import Direction, Cell
from ....resources import ASSETS
from .actor import Actor
from ..sprite.world_sprite import WorldSprite
from ...animator import Animator
from ..collider import CollisionLayer
from ..float_animation import FloatAnimation, FloatStyle
from ....utils.get_time import get_time

if TYPE_CHECKING:
    from ....level import Maze

INVINCIBILITY_TIME: float = 5.0
"""Time in seconds that Pac-Man is invincible after respawning."""


class PacMan(Actor):
    """Pac-Man, steered by the player.

    Controls are classic: a direction is remembered (``wanted``) and taken
    at the first cell where it is possible, so turns can be pressed early.
    Pac-Man keeps going until a wall stops him, and can reverse at once.

    Parameters
    ----------
    cell: Cell
        Cell Pac-Man starts and respawns in.
    maze: Maze
        Maze Pac-Man moves in.
    player: int
        Player this Pac-Man belongs to, for multiplayer.
    """
    def __init__(
            self,
            cell: Cell,
            maze: Maze,
            player: int,
            ) -> None:
        super().__init__(cell, maze, 2.0)
        self.player = player

        self.wanted = Direction.NONE
        self.facing = Direction.S

        self.col.layer = CollisionLayer.PACMAN
        self.col.mask = CollisionLayer.ITEM | CollisionLayer.GHOST

        pivot = FloatAnimation(FloatStyle.FLOAT, pi * 2 * random(), 2.0, 4.0)
        self.add_child(pivot)

        sprite = WorldSprite(ASSETS.pacman[self.player, self.facing, 0][0])
        sprite.offset.update((0.0, -2.0))
        pivot.add_child(sprite)

        self.animator = Animator(sprite, ASSETS.pacmanimations[player])
        sprite.add_child(self.animator)

    @property
    def is_invincible(self) -> bool:
        "Whether Pac-Man is invincible after respawning."
        return get_time() - self.start_time < INVINCIBILITY_TIME

    def steer(self, direction: Direction) -> None:
        """Ask Pac-Man to go a direction, as soon as the maze allows it.

        Parameters
        ----------
        direction: Direction
            Direction Pac-Man should go, if possible.
        """
        self.wanted = direction
        if direction is self.direction.opposite:
            self.reverse()

    def award(self, points: int, major = False) -> None:
        ...

    # Overridden methods.
    # --------------------------------------------------------------------------
    def respawn(self) -> None:
        super().respawn()
        self.wanted = Direction.NONE
        self.facing = Direction.S

    def reverse(self) -> None:
        super().reverse()
        self.animator.play(('walk', self.direction))

    def choose_direction(self) -> Direction:
        "Take the wanted turn if open, else keep going, else stop."
        if self._can_move(self.wanted):
            self.animator.play(('walk', self.wanted))
            return self.wanted
        if self._can_move(self.direction):
            return self.direction
        self.animator.stop()
        return Direction.NONE

    def on_collision(self, other: Actor) -> None:
        "Pac-Man dies when colliding with a ghost, unless invincible."
        # if isinstance(other, Ghost):
        #     if other.state == GhostState.FRIGHTENED:
        #         other.get_eaten()
        #     elif not self.is_invincible:
        #         self.respawn()
