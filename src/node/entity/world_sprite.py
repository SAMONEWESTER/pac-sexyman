from __future__ import annotations

from pygame import Surface, Vector2

from .entity import Entity


class WorldSprite(Entity):
    def __init__(self, position: Vector2, image: Surface) -> None:
        super().__init__(position)
        self.image = image
        self.rect = self.image.get_rect(center=position)

    def draw(self, surface: Surface) -> None:
        if not self.active:
            return
        surface.blit(self.image, self.rect + self.parent.position)
        super().draw(surface)
