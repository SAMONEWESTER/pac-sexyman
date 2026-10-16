"""Simple drawn sprites, used until real artwork exists."""

import math

import pygame
from pygame import SRCALPHA, Color, Surface

from .colors import EYE_WHITE, FRIGHTENED_FACE, PAC_MAN_YELLOW, PUPIL_BLUE

TRANSPARENT: Color = Color(0, 0, 0, 0)


def draw_pac_man(size: int, mouth_degrees: float) -> Surface:
    """Draw Pac-Man facing right.

    Args:
        size: Width and height of the sprite, in pixels.
        mouth_degrees: How wide the mouth is open, 0 for closed.
    """
    surface = Surface((size, size), SRCALPHA)
    radius = size // 2
    pygame.draw.circle(surface, PAC_MAN_YELLOW, (radius, radius), radius)
    if mouth_degrees > 0:
        half = math.radians(mouth_degrees / 2)
        reach = size * 2
        tip_x = radius + reach * math.cos(half)
        pygame.draw.polygon(surface, TRANSPARENT, [
            (radius, radius),
            (tip_x, radius - reach * math.sin(half)),
            (tip_x, radius + reach * math.sin(half)),
        ])
    return surface


def draw_ghost(size: int, body: Color, frightened: bool = False) -> Surface:
    """Draw a ghost: round head, wavy skirt and eyes.

    Args:
        size: Width and height of the sprite, in pixels.
        body: Body color.
        frightened: Draw the scared face instead of normal eyes.
    """
    surface = Surface((size, size), SRCALPHA)
    radius = size // 2
    foot = size // 6

    # Head, body and three round feet.
    pygame.draw.circle(surface, body, (radius, radius), radius)
    pygame.draw.rect(surface, body, (0, radius, size, radius - foot))
    for i in range(3):
        center_x = round(size * (i + 0.5) / 3)
        pygame.draw.circle(surface, body, (center_x, size - foot), foot + 1)

    eye_y = round(size * 0.4)
    for side in (-1, 1):
        eye_x = radius + side * round(size * 0.2)
        if frightened:
            pygame.draw.rect(surface, FRIGHTENED_FACE,
                             (eye_x - 2, eye_y - 2, 4, 4))
        else:
            pygame.draw.circle(surface, EYE_WHITE, (eye_x, eye_y),
                               round(size * 0.14))
            pygame.draw.circle(surface, PUPIL_BLUE, (eye_x + 2, eye_y),
                               round(size * 0.07))
    return surface
