"""The player character."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

import pygame
from pygame.sprite import AbstractGroup

from ...config import tuning
from ...grid import Cell, Direction
from ...resources import ASSETS
from .living import Living

if TYPE_CHECKING:
    from ...level import Maze

CHOMP_ORDER: tuple[int, ...] = (0, 1, 2, 1, 3)
"""Sheet columns played in a loop while moving: stretch, back, squash."""

STILL_FRAME: int = 0
"""Sheet column shown while standing still."""

INVINCIBILITY_TIME: float = 5.0
"""Time in seconds that Pac-Man is invincible after respawning."""


class PacMan(Living):
    """Pac-Man, steered by the player.

    Controls are classic: a direction is remembered (``wanted``) and taken
    at the first cell where it is possible, so turns can be pressed early.
    Pac-Man keeps going until a wall stops him, and can reverse at once.

    Args:
        maze: The maze Pac-Man moves in.
        cell: The cell Pac-Man starts and respawns in.
        *groups: Sprite groups to add Pac-Man to.
    """

    def __init__(
            self,
            maze: Maze,
            cell: Cell,
            player: int,
            *groups: AbstractGroup[Any],
            ) -> None:
        image = ASSETS.pac_man[(player, Direction.DOWN)][STILL_FRAME]
        super().__init__(image, maze, cell, tuning.PAC_MAN_SPEED, *groups)
        self.player = player
        self.wanted = Direction.NONE
        self.facing = Direction.DOWN
        self.chomp_time = 0.0

        self.last_respawn = 0.0

    def is_invincible(self, elapsed: float) -> bool:
        """Whether Pac-Man is invincible after respawning.

        Args:
            elapsed: Seconds since the game started.
        """
        return elapsed - self.last_respawn < INVINCIBILITY_TIME

    def steer(self, direction: Direction) -> None:
        """Ask Pac-Man to go a direction, as soon as the maze allows it.

        Args:
            direction: The direction the player pressed.
        """
        self.wanted = direction
        if direction is self.direction.opposite:
            self.reverse()

    def choose_direction(self) -> Direction:
        """Take the wanted turn if open, else keep going, else stop."""
        if self.can_move(self.wanted):
            return self.wanted
        if self.can_move(self.direction):
            return self.direction
        return Direction.NONE

    def animate(self, dt: float, elapsed: float) -> None:
        """Face the movement direction and chomp while moving.

        Args:
            dt: Seconds since the previous frame.
            elapsed: Seconds since the game started (unused).
        """
        if self.direction is Direction.NONE:
            self.chomp_time = 0.0
            self.image = ASSETS.pac_man[(self.player, self.facing)][0]
            return

        self.facing = self.direction
        self.chomp_time += dt
        step = int(self.chomp_time * tuning.PAC_MAN_ANIMATION_FPS)
        column = CHOMP_ORDER[step % len(CHOMP_ORDER)]
        self.image = ASSETS.pac_man[(self.player, self.facing)][column]
        if self.is_invincible(elapsed):
            self.image = self.image.copy()
            self.image.fill((255, 255, 255, 128), special_flags=pygame.BLEND_RGBA_MULT)

    def respawn(self) -> None:
        """Back to the start cell, facing the player, no wanted turn."""
        super().respawn()
        self.wanted = Direction.NONE
        self.facing = Direction.DOWN
