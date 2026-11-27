"""The player character."""

from __future__ import annotations

from math import pi
from random import random
from typing import TYPE_CHECKING

from ....game.player import Player
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
    def __init__(self, cell: Cell, maze: Maze, player: Player) -> None:
        super().__init__(cell, maze, 4.0)
        self.player = player

        self.wanted = Direction.NONE
        self.facing = Direction.S

        self.collider.layer = CollisionLayer.PACMAN
        self.collider.mask = CollisionLayer.ITEM | CollisionLayer.GHOST

        pivot = FloatAnimation(FloatStyle.FLOAT, pi * 2 * random(), 3.0, 4.0)
        self.add_child(pivot)

        index = self.player.index
        self.sprite = WorldSprite(ASSETS.pacman[index, self.facing, 0][0])
        self.sprite.offset.update((0.0, -2.0))
        pivot.add_child(self.sprite)

        self.animator = Animator(self.sprite, ASSETS.pacmanimations[index])
        self.sprite.add_child(self.animator)

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

    # Overridden methods.
    # --------------------------------------------------------------------------
    def update(self, dt):
        if not self.active:
            return False

        if self.is_invincible:
            is_visible = get_time() % 0.1 > 0.05
        else:
            is_visible = True
        self.sprite.active = is_visible

        return super().update(dt)

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
            if self.wanted != self.direction:
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
