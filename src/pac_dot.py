import math
import random

from pygame.sprite import Sprite

from .assets import ASSETS


class PacDot(Sprite):
    def __init__(self, pos: tuple[int, int], style: str, *groups):
        super().__init__(*groups)
        # Initializing the pac-dot graphics.
        self.image = ASSETS.pac_dot
        self.rect = self.image.get_rect(center=(0, 0)).move(*pos)

        # Animation.
        self.pos = pos
        self.phase = sum(pos) / 100
        self.style = getattr(self, style)

    def _float(self, elapsed_time: float) -> None:
        self.rect.centery = \
            self.pos[1] + 3 * math.sin(elapsed_time * 1 + self.phase)

    def _swing(self, elapsed_time: float) -> None:
        self.rect.center = (
            self.pos[0] + 3 * math.cos(elapsed_time * 2 + self.phase),
            self.pos[1] + 3 * math.sin(elapsed_time * 2 + self.phase)
        )

    def _bounce(self, elapsed_time: float) -> None:
        self.rect.center = (
            self.pos[0] + 2 * math.cos(elapsed_time * 4 + self.phase),
            self.pos[1] + 5 * -abs(math.sin(elapsed_time * 4 + self.phase))
        )

    def update(self, elapsed_time: float) -> None:
        self.style(elapsed_time)
