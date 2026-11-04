"""Message that shows up when a significant point bonus is awarded."""

from __future__ import annotations

from random import uniform
from typing import Any

from pygame import Surface, Vector2, SRCALPHA
from pygame.sprite import AbstractGroup, Sprite

from ...resources import ASSETS


class PointMessage(Sprite):
    """Shows points earned by Pac-Man.

    Args:
        image: What the entity looks like.
        center: Pixel position of the entity's center.
        *groups: Sprite groups to add the entity to.
    """

    def __init__(
            self,
            center: Vector2,
            points: int,
            spawn_time: float,
            *groups: AbstractGroup[Any],
            ) -> None:
        super().__init__(*groups)
        self.pos = Vector2(center)
        self.speed = Vector2(uniform(-0.5, 0.5), uniform(-0.5, -1))
        self.spawn_time = spawn_time

        msg = str(points)
        self.image = Surface((len(msg) * 8, 16), SRCALPHA)
        for i, x in enumerate(msg):
            self.image.blit(ASSETS.numbers[int(x)], (i * 8, 0))
        self.rect = self.image.get_rect(center=center)

    def update(self, dt: float, elapsed: float) -> None:
        """Advance the entity by one frame.

        Args:
            dt: Seconds since the previous frame.
            elapsed: Seconds since the game started.
        """
        self.pos += self.speed
        self.speed *= 0.95
        self.rect.center = (round(self.pos.x), round(self.pos.y - 2))
        if elapsed - self.spawn_time > 1:
            self.kill()
