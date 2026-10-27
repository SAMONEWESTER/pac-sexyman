"""The small dots (pacgums) Pac-Man eats for points."""

from __future__ import annotations

from typing import Any

from pygame import Vector2
from pygame.sprite import AbstractGroup

from ...resources import ASSETS
from ..components import Edible, IdleAnimation, IdleStyle
from .inanimate import Inanimate


class Dot(Inanimate):
    """A pacgum: always edible, worth a few points.

    Args:
        center: Pixel position the dot rests at.
        style: Idle motion of the dot.
        points: Score for eating it.
        *groups: Sprite groups to add the dot to.
    """

    def __init__(
            self,
            center: Vector2,
            idle_style: IdleStyle,
            points: int,
            theme: int,
            *groups: AbstractGroup[Any],
            ) -> None:
        # The phase spreads the motion out, so dots ripple like a wave.
        animation = IdleAnimation(
            idle_style, phase=(center.x + center.y) / 100)
        super().__init__(ASSETS.pac_dots[theme], center, animation, *groups)
        self.edible = Edible(points)
