from __future__ import annotations

from pygame import Surface
from pygame.transform import scale

from .sprite import Sprite
from ..camera import Camera


class WorldSprite(Sprite):
    def draw(self, surface: Surface, camera: Camera | None = None) -> bool:
        if not self.active or camera is None:
            return False

        image = scale(self.image, camera.size(self.image.get_size()))
        rect = image.get_rect(
            center=camera.point(self.rect.move(self.position))
        )
        surface.blit(image, rect)

        return super().draw(surface, camera)  # Draw children after the parent.
