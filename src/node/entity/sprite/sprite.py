from __future__ import annotations

from pygame import Surface

from ..entity import Entity


class Sprite(Entity):
    """Sprite base class that has an image and a rectangle for drawing.

    Parameters
    ----------
    image: Surface
        Image of the sprite.
    """
    def __init__(self, image: Surface) -> None:
        super().__init__()
        self.image = image
        self.rect = self.image.get_rect()
