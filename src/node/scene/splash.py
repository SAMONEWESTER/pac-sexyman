from __future__ import annotations
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from ...game import Game

from pygame import Surface

from ...game.player import Players
from .scene import Scene
from .level import Level
from ..entity.sprite.world_sprite import WorldSprite
from ..entity.camera import Camera
from ...resources import ASSETS
from ...utils.get_time import get_time


class Splash(Scene):
    def __init__(self, game: Game):
        super().__init__(game)
        self.camera = Camera((256, 256))
        image = WorldSprite(ASSETS.splash_image)
        image.offset.update((128, 128))
        self.add_child(image)

    def update(self, dt: float) -> bool:
        if not self.active:
            return False
        if get_time() > 1.0:
            self.next_scene = Level(self.game, 0)
        return super().update(dt)

    def draw(self) -> bool:
        if not self.active:
            return False
        return super().draw(self.game.screen, self.camera)

    def handle_key(self, key: int) -> None:
        pass
