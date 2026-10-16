"""The ghosts that chase Pac-Man."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from pygame import Surface
from pygame.sprite import AbstractGroup

from ...config import GHOST_SPEED
from ...grid import Cell
from ...resources import ASSETS
from ..components import Edible
from .living import Living

if TYPE_CHECKING:
    from ...level import Maze


class Ghost(Living):
    """A ghost: dangerous normally, edible while frightened.

    Edibility is a component that comes and goes: ``frighten`` gives
    the ghost an ``Edible``, ``calm`` takes it away again.

    Args:
        maze: The maze the ghost moves in.
        cell: The cell the ghost starts and respawns in.
        image: The ghost's normal look.
        points: Score for eating the ghost while it is frightened.
        *groups: Sprite groups to add the ghost to.
    """

    def __init__(
            self,
            maze: Maze,
            cell: Cell,
            image: Surface,
            points: int,
            *groups: AbstractGroup[Any],
            ) -> None:
        super().__init__(image, maze, cell, GHOST_SPEED, *groups)
        self.normal_image = image
        self.points = points
        self.frightened_left = 0.0

    @property
    def is_frightened(self) -> bool:
        """Whether the ghost is currently scared and edible."""
        return self.frightened_left > 0

    def frighten(self, seconds: float) -> None:
        """Make the ghost edible and scared for a while.

        Args:
            seconds: How long the effect lasts.
        """
        self.frightened_left = seconds
        self.edible = Edible(self.points)
        self.image = ASSETS.ghost_frightened

    def calm(self) -> None:
        """End the frightened state: no longer edible."""
        self.frightened_left = 0.0
        self.edible = None
        self.image = self.normal_image

    def update(self, dt: float, elapsed: float) -> None:
        """Count down the frightened timer. Movement comes later.

        Args:
            dt: Seconds since the previous frame.
            elapsed: Seconds since the game started (unused for now).
        """
        if self.is_frightened:
            self.frightened_left -= dt
            if self.frightened_left <= 0:
                self.calm()
