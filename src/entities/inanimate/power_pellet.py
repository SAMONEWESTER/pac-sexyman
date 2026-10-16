"""The big dots (super-pacgums) in the maze corners."""

from __future__ import annotations

from typing import Any

from pygame import Vector2
from pygame.sprite import AbstractGroup

from ...config import FRIGHTENED_SECONDS
from ...resources import ASSETS
from ..components import Edible, IdleAnimation, IdleStyle
from .power_up import PowerUp, PowerUpTarget


class PowerPellet(PowerUp):
    """A super-pacgum: worth points and makes the ghosts edible.

    Args:
        center: Pixel position the pellet rests at.
        style: Idle motion of the pellet.
        points: Score for eating it.
        duration: Seconds the ghosts stay edible.
        *groups: Sprite groups to add the pellet to.
    """

    def __init__(
            self,
            center: Vector2,
            style: IdleStyle,
            points: int,
            duration: float = FRIGHTENED_SECONDS,
            *groups: AbstractGroup[Any],
            ) -> None:
        animation = IdleAnimation(style, phase=(center.x + center.y) / 100)
        super().__init__(ASSETS.power_pellet, center, animation, *groups)
        self.edible = Edible(points)
        self.duration = duration

    def activate(self, target: PowerUpTarget) -> None:
        """Frighten every ghost for ``duration`` seconds."""
        target.frighten_ghosts(self.duration)
