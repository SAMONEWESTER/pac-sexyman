"""The big dots (super-pacgums) in the maze corners."""

from __future__ import annotations

from typing import Any

from pygame import Vector2
from pygame.sprite import AbstractGroup

from ...resources import ASSETS
from ..components import Edible, IdleAnimation, IdleStyle
from .inanimate import Inanimate


class Fruit(Inanimate):
    def __init__(
            self,
            center: Vector2,
            points: int,
            level: int,
            *groups: AbstractGroup[Any],
            ) -> None:
        super().__init__(
            ASSETS.fruits[level % len(ASSETS.fruits)],
            center,
            IdleAnimation(IdleStyle.FLOAT, phase=(center.x + center.y) / 100),
            *groups)
        self.edible = Edible(points)
