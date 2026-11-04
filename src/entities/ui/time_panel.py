from pygame import SRCALPHA, Surface
from pygame.sprite import Sprite

from ...resources import ASSETS


class TimePanel(Sprite):
    def __init__(
        self,
        time: int,
        pos: tuple[int, int],
    ) -> None:
        super().__init__()

        card_size = ASSETS.time_card.get_size()
        self.image = Surface(card_size, SRCALPHA)
        self.rect = self.image.get_rect(topleft=(pos[0] - 8, pos[1] - 8))

        self.time = time
        self.update(time)

    def update(self, time: int) -> None:
        time = int(max(time, 0))
        if time == self.time:
            return
        self.time = time

        self.image.fill((0, 0, 0, 0))
        self.image.blit(ASSETS.time_card, (0, 0))

        content = Surface((64, 16), SRCALPHA)
        content.blit(ASSETS.time, (0, 0))

        for i, digit in enumerate(reversed(str(time))):
            content.blit(ASSETS.numbers[int(digit)], (40 - i * 8, 0))

        self.image.blit(content, (8, 8))
