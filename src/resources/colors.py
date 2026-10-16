"""Named colors and color helpers."""

from random import randint

from pygame import Color

PAC_MAN_YELLOW: Color = Color(255, 220, 0)
FRIGHTENED_BLUE: Color = Color(40, 40, 255)
EYE_WHITE: Color = Color(240, 240, 255)
PUPIL_BLUE: Color = Color(30, 30, 160)
FRIGHTENED_FACE: Color = Color(255, 200, 160)

GHOST_COLORS: tuple[Color, ...] = (
    Color(255, 0, 0),      # Blinky
    Color(255, 184, 255),  # Pinky
    Color(0, 255, 255),    # Inky
    Color(255, 184, 82),   # Clyde
)
"""Body color of each of the four ghosts."""


def random_color() -> Color:
    """Return a random color that is never too dark to see."""
    return Color(randint(64, 255), randint(64, 255), randint(64, 255))
