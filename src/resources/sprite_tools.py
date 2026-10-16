"""Small helpers to turn sprite sheets into ready-to-draw frames."""

import pygame
from pygame import Color, Surface

Frames = tuple[Surface, ...]
"""An animation: frames in play order."""


def split_rows(frames: Frames, columns: int) -> tuple[Frames, ...]:
    """Group a flat list of sheet frames into rows.

    Args:
        frames: Frames left to right, top to bottom (from ``_load_sliced``).
        columns: Frames per row in the sheet.
    """
    return tuple(
        frames[start:start + columns]
        for start in range(0, len(frames), columns))


def mirror(frames: Frames) -> Frames:
    """Flip every frame horizontally (right-facing becomes left-facing)."""
    return tuple(pygame.transform.flip(frame, True, False) for frame in frames)


def rotate(frames: Frames, degrees: float) -> Frames:
    """Rotate every frame; positive degrees turn counter-clockwise."""
    return tuple(pygame.transform.rotate(frame, degrees) for frame in frames)


def tint(frames: Frames, color: Color) -> Frames:
    """Recolor frames, keeping their shading and transparency.

    Each pixel keeps its brightness but takes the hue of ``color``, so a
    red ghost can become a pink, cyan or orange one.

    Args:
        frames: The frames to recolor.
        color: The new main color.
    """
    return tuple(_tint_one(frame, color) for frame in frames)


def _tint_one(frame: Surface, color: Color) -> Surface:
    """Recolor a single frame, see ``tint``."""
    result = frame.copy()
    width, height = result.get_size()
    for x in range(width):
        for y in range(height):
            r, g, b, a = result.get_at((x, y))
            if a == 0:
                continue
            brightness = max(r, g, b) / 255
            result.set_at((x, y), (round(color.r * brightness),
                                   round(color.g * brightness),
                                   round(color.b * brightness), a))
    return result
