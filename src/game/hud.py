"""The score, lives and level line drawn over the maze."""

from pygame import Color, Surface

from ..resources import FONTS
from .session import Session

HUD_COLOR: Color = Color(255, 255, 255)
HUD_SHADOW: Color = Color(0, 0, 0)
HUD_MARGIN: tuple[int, int] = (8, 4)


def draw_hud(screen: Surface, session: Session) -> None:
    """Draw score, lives and level in the top left corner.

    Args:
        screen: Where to draw.
        session: The values to show.
    """
    text = (f'SCORE {session.score}   LIVES {session.lives}   '
            f'LEVEL {session.level}')
    x, y = HUD_MARGIN
    screen.blit(FONTS.regular.render(text, False, HUD_SHADOW), (x + 2, y + 2))
    screen.blit(FONTS.regular.render(text, False, HUD_COLOR), (x, y))
