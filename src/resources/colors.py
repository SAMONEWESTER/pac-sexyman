"""Named colors and color helpers."""

from random import randint

from pygame import Color

FRIGHTENED_BLUE: Color = Color(60, 80, 255)
"""Body color of every ghost while it is edible."""

GHOST_TINTS: dict[str, Color] = {
    'pinky': Color(255, 150, 220),
    'inky': Color(60, 230, 255),
    'clyde': Color(255, 170, 60),
}
"""Recolor for ghosts that have no sprite sheet of their own yet.

They reuse ``blinky.png`` in this color until ``<name>.png`` exists.
"""


def random_color() -> Color:
    """Return a random color that is never too dark to see."""
    return Color(255, randint(192, 255), randint(192, 255))
