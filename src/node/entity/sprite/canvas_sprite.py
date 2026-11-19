from __future__ import annotations

import pygame
from pygame import Surface

from .sprite import Sprite
from ..camera import Camera


class CanvasSprite(Sprite):
    """Sprite that is drawn in canvas coordinates,
    and scaled to the camera's view.

    Parameters
    ----------
    image: Surface
        Image of the sprite.
    scale: int
        Scale factor for the sprite.
    """
    def __init__(self, image: Surface, scale: int) -> None:
        super().__init__(image)
        self.scale = scale

    def draw(self, surface: Surface, camera: Camera | None = None) -> bool:
        """Returns whether the sprite is active and should be drawn.
        The sprite is drawn in screen coordinates,
        and scaled to the camera's view."""
        if not self.active or camera is None:
            return False

        w, h = self.image.get_size()
        image = pygame.transform.scale(
            self.image, (w * self.scale, h * self.scale))
        rect = image.get_rect(topleft=self.rect.topleft)
        surface.blit(image, rect)

        return super().draw(surface, camera)  # Draw children after the parent.
