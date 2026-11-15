from __future__ import annotations

import pygame
from pygame import Surface, Vector2

from .sprite import Sprite
from ..camera import Camera


class CanvasSprite(Sprite):
    def __init__(
            self,
            position: Vector2,
            image: Surface,
            scale: int,
            ) -> None:
        super().__init__(position, image)
        self.scale = scale

    def draw(self, surface: Surface, camera: Camera | None = None) -> bool:
        if not self.active or camera is None:
            return False

        w, h = self.image.get_size()
        image = pygame.transform.scale(
            self.image, (w * self.scale, h * self.scale))
        rect = image.get_rect(topleft=self.rect.topleft)
        surface.blit(image, rect)

        return super().draw(surface, camera)  # Draw children after the parent.
