import math

from pygame import Vector2
from pygame.sprite import Sprite

from .assets import ASSETS


class PacDot(Sprite):
    amplitude = 4.0
    speed = 1.0

    def __init__(self, pos: tuple[int, int], *groups):
        super().__init__(*groups)
        # Initializing the pac-dot graphics.
        self.image = ASSETS.pac_dot
        self.rect = self.image.get_rect(center=(0, 0)).move(*pos)

        # Animation.
        self.base_y = pos[1]
        self.phase = sum(pos) / 100

    def update(self, elapsed_time: float) -> None:
        self.rect.centery = round(
            self.base_y + 3 * math.sin(elapsed_time * 2 + self.phase))
