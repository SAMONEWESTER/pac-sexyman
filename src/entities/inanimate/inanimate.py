"""Base class for entities that never leave their spot."""

from __future__ import annotations

from typing import Any

from pygame import Surface, Vector2
from pygame.sprite import AbstractGroup

from ..components import IdleAnimation
from ..entity import Entity


class Inanimate(Entity):
    """An entity that stays at a fixed rest position.

    It may still wiggle around that spot with an optional
    ``IdleAnimation`` (composition), which ``update`` plays.

    Args:
        image: What the entity looks like.
        center: Pixel position the entity rests at.
        animation: Idle motion to play, or ``None`` to stay still.
        *groups: Sprite groups to add the entity to.
    """

    def __init__(
            self,
            image: Surface,
            center: Vector2,
            animation: IdleAnimation | None = None,
            *groups: AbstractGroup[Any],
            ) -> None:
        super().__init__(image, center, *groups)
        self.rest = Vector2(center)
        self.animation = animation

    def update(self, dt: float, elapsed: float) -> None:
        """Play the idle animation around the rest position.

        Args:
            dt: Seconds since the previous frame (unused).
            elapsed: Seconds since the game started.
        """
        if self.animation is None:
            return
        dx, dy = self.animation.offset(elapsed)
        self.rect.center = (round(self.rest.x + dx),
                            round(self.rest.y + dy - 2))
