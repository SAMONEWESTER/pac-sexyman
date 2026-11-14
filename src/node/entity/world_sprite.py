from __future__ import annotations

from pygame import Surface, Vector2
from pygame.transform import scale

from .entity import Entity
from .camera import Camera


class WorldSprite(Entity):
    def __init__(self, position: Vector2, image: Surface) -> None:
        super().__init__(position)
        self.image = image
        self.rect = self.image.get_rect()

    def draw(self, surface: Surface, camera: Camera | None = None) -> bool:
        if not super().draw(surface, camera) or camera is None:
            return False

        image = scale(self.image, camera.size(self.image.get_size()))
        rect = image.get_rect(
            center=camera.point(self.rect.move(self.position))
        )
        surface.blit(image, rect)

        for child in self.children:
            child.draw(surface, camera)
        return True
