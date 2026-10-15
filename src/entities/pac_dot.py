"""The small dots pac-man eats for points."""

from __future__ import annotations

import math
from collections.abc import Callable
from typing import Any

from pygame.sprite import AbstractGroup, Sprite

from ..resources import ASSETS

DOT_STYLES: tuple[str, ...] = ('_float', '_swing', '_bounce')
"""Names of the available idle animations, see ``PacDot``."""


class PacDot(Sprite):
    """An animated pac-dot sitting at a fixed position.

    Args:
        pos: Center of the dot when it is at rest, in pixels.
        style: Name of the idle animation, one of ``DOT_STYLES``.
        *groups: Sprite groups to add the dot to.
    """

    def __init__(
            self,
            pos: tuple[int, int],
            style: str,
            *groups: AbstractGroup[Any],
            ) -> None:
        super().__init__(*groups)
        # Initializing the pac-dot graphics.
        self.image = ASSETS.pac_dot
        self.rect = self.image.get_rect(center=(0, 0)).move(*pos)

        # Animation.
        self.pos = pos
        self.phase = sum(pos) / 100
        self.style: Callable[[float], None] = getattr(self, style)

    def _float(self, elapsed_time: float) -> None:
        """Bob slowly up and down."""
        self.rect.centery = round(
            self.pos[1] + 3 * math.sin(elapsed_time * 1 + self.phase))

    def _swing(self, elapsed_time: float) -> None:
        """Move in a small circle."""
        self.rect.center = (
            round(self.pos[0] + 3 * math.cos(elapsed_time * 2 + self.phase)),
            round(self.pos[1] + 3 * math.sin(elapsed_time * 2 + self.phase)),
        )

    def _bounce(self, elapsed_time: float) -> None:
        """Hop up and down while swaying sideways."""
        self.rect.center = (
            round(self.pos[0] + 2 * math.cos(elapsed_time * 4 + self.phase)),
            round(self.pos[1]
                  + 5 * -abs(math.sin(elapsed_time * 4 + self.phase))),
        )

    def update(self, elapsed_time: float) -> None:
        """Advance the idle animation.

        Args:
            elapsed_time: Seconds since the game started.
        """
        self.style(elapsed_time)
