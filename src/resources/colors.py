"""Color helpers."""

from random import randint

from pygame import Color


def random_color() -> Color:
    """Return a random color that is never too dark to see."""
    return Color(randint(64, 255), randint(64, 255), randint(64, 255))
