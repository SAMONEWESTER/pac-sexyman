"""The score, lives and level line drawn over the maze."""

from pygame import Surface, SRCALPHA

from ..resources import ASSETS
from .player import Player


def blit_player_stats(
        screen: Surface,
        player: Player,
        index: int,
        elapsed: float,
        pos: tuple[int, int]
        ) -> None:
    image = Surface((64, 32), SRCALPHA)
    for i, x in enumerate(reversed(str(max(player.score, 0)))):
        image.blit(ASSETS.numbers[int(x)], (56 - i * 8, 0))
    for i in reversed(range(min(player.lives, 7))):
        image.blit(ASSETS.extra_life[index], (i * 8, 16))

    screen.blit(
        ASSETS.player_card[index + player.is_over * 2],
        (pos[0] - 8, pos[1] - 8))
    if player.is_over:
        image.blit(ASSETS.prompt_shift[int(elapsed / 2) % 2], (32, 16))
    screen.blit(image, pos)


def blit_time(
        screen: Surface,
        time: int,
        pos: tuple[int, int]
        ) -> None:
    image = Surface((64, 16), SRCALPHA)
    image.blit(ASSETS.time, (0, 0))
    for i, x in enumerate(reversed(str(time))):
        image.blit(ASSETS.numbers[int(x)], (40 - i * 8, 0))

    screen.blit(ASSETS.time_card, (pos[0] - 8, pos[1] - 8))
    screen.blit(image, pos)
