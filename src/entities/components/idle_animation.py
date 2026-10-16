"""Small looping motions that make still objects feel alive."""

import math
from enum import Enum


class IdleStyle(Enum):
    """The available idle motions."""

    FLOAT = 'float'
    SWING = 'swing'
    BOUNCE = 'bounce'


class IdleAnimation:
    """Computes how far an object drifts from its rest position.

    Args:
        style: Which motion to play.
        phase: Time offset in seconds, so neighbours do not move in sync.
    """

    def __init__(self, style: IdleStyle, phase: float = 0.0) -> None:
        self.style = style
        self.phase = phase

    def offset(self, elapsed: float) -> tuple[float, float]:
        """Return the ``(dx, dy)`` drift in pixels at a moment in time.

        Args:
            elapsed: Seconds since the game started.
        """
        if self.style is IdleStyle.FLOAT:
            return 0.0, 3 * math.sin(elapsed + self.phase)
        if self.style is IdleStyle.SWING:
            angle = elapsed * 2 + self.phase
            return 3 * math.cos(angle), 3 * math.sin(angle)
        angle = elapsed * 4 + self.phase
        return 2 * math.cos(angle), -5 * abs(math.sin(angle))
