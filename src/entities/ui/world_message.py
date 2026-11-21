"""Message that shows up when a significant point bonus is awarded."""

from __future__ import annotations

from random import uniform
from typing import Any

from pygame import Vector2
from pygame.sprite import AbstractGroup, Sprite

from ...resources import text_to_image


class WorldMessage(Sprite):
    def __init__(
            self,
            position: Vector2,
            message: str,
            spawn_time: float,
            *groups: AbstractGroup[Any],
            ) -> None:
        super().__init__(*groups)
        self.pos = Vector2(position) + Vector2(0, -8)
        self.speed = Vector2(uniform(-0.5, 0.5), uniform(-0.5, -1))
        self.spawn_time = spawn_time

        self.image = text_to_image(str(message))
        self.rect = self.image.get_rect(center=position)

    def update(self, dt: float, t: float) -> None:
        """Advance the entity by one frame.

        Args:
            dt: Seconds since the previous frame.
            t: Seconds since the game started.
        """
        self.pos += self.speed
        self.speed *= 0.95
        self.rect.center = (round(self.pos.x), round(self.pos.y - 2))
        if t - self.spawn_time > 1:
            self.kill()
