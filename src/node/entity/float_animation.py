"""Small looping motions that make still objects feel alive."""

from math import sin, cos, fabs
from enum import Enum, auto

from pygame import Vector2

from .entity import Entity
from ..utils import get_time


class FloatStyle(Enum):
    """The available idle motions."""

    FLOAT = auto()
    SWING = auto()
    BOUNCE = auto()

    @classmethod
    def from_index(cls, index: int):
        """Returns the FloatStyle corresponding to the given index,
        wrapping around if necessary."""
        members = list(cls)
        return members[index % len(members)]


class FloatAnimation(Entity):
    """Computes how far an object drifts from its rest position.

    Args:
        style: Which motion to play.
        phase: Time offset in seconds, so neighbours do not move in sync.
    """

    def __init__(
            self,
            offset: Vector2,
            style: FloatStyle,
            phase: float = 0.0,
            frequency: float = 1.0,
            ) -> None:
        super().__init__(offset)
        match style:
            case FloatStyle.FLOAT:
                self.style = self.animate_float
            case FloatStyle.SWING:
                self.style = self.animate_swing
            case _:
                self.style = self.animate_bounce
        self.phase = phase
        self.frequency = frequency

    def animate_float(self) -> tuple[float, float]:
        return (0.0, 3 * sin((self.frequency * get_time()) + self.phase) - 2)

    def animate_swing(self) -> tuple[float, float]:
        angle = self.frequency * get_time() * 2 + self.phase
        return 3 * cos(angle), 3 * sin(angle)

    def animate_bounce(self) -> tuple[float, float]:
        angle = self.frequency * get_time() * 4 + self.phase
        return 2 * cos(angle), -5 * fabs(sin(angle))

    def update(self, dt: float) -> bool:
        if not super().update(dt):
            return False

        self.position = (
            self.parent.position + self.offset + Vector2(self.style()))

        return True
