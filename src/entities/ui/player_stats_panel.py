from __future__ import annotations

from typing import TYPE_CHECKING

from pygame import SRCALPHA, Surface
from pygame.sprite import Sprite

from ...resources import ASSETS

if TYPE_CHECKING:
    from ...game.player import Player


class PlayerStatsPanel(Sprite):
    def __init__(
        self,
        player: Player,
        index: int,
        pos: tuple[int, int],
    ) -> None:
        super().__init__()
        self.player = player
        self.index = index

        # image includes the card and content; pos is the old content position.
        self.image = Surface(ASSETS.player_card[index].get_size(), SRCALPHA)
        self.rect = self.image.get_rect(topleft=(pos[0] - 8, pos[1] - 8))

        self._last_key: tuple[int, int, bool, int] | None = None
        self.update(0.0, 0.0)

    def update(self, dt: float, elapsed: float) -> None:
        player = self.player
        is_over = player.is_over

        # The join prompt blinks every two seconds while the player is out.
        blink = int(elapsed / 2) % 2 if is_over else 0
        key = (player.score, player.lives, is_over, blink)
        if key == self._last_key:
            return
        self._last_key = key

        self.image.fill((0, 0, 0, 0))
        self.image.blit(
            ASSETS.player_card[self.index + int(is_over) * 4],
            (0, 0),
        )

        # Draw the old 64x32 content area at the card's (8, 8) offset.
        content = Surface((64, 32), SRCALPHA)

        for i, digit in enumerate(reversed(str(max(player.score, 0)))):
            content.blit(ASSETS.numbers[int(digit)], (56 - i * 8, 0))

        for i in reversed(range(min(player.lives, 7))):
            content.blit(ASSETS.extra_life[self.index], (i * 8, 16))

        if is_over:
            prompt_index = self.index + blink * 4
            content.blit(ASSETS.player_join_prompt[prompt_index], (32, 16))

        self.image.blit(content, (8, 8))
