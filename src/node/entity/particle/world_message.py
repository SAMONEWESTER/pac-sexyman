from random import uniform

from pygame import Vector2

from ..entity import Entity
from ..sprite.world_sprite import WorldSprite
from ....resources import text_to_image
from ....utils.get_time import get_time


class WorldMessage(Entity):
    def __init__(self, message: str) -> None:
        super().__init__()
        self.speed = Vector2(uniform(-0.5, 0.5), uniform(-0.5, -1))

        sprite = WorldSprite(text_to_image(message))
        self.add_child(sprite)

    def update(self, dt: float) -> bool:
        if not self.active:
            return False

        self.offset += self.speed
        self.speed *= 0.95
        if get_time() - self.start_time > 1.0:
            self.kill()
            return False

        return super().update(dt)
