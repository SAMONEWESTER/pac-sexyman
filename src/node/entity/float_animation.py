"""Small looping motions that make still objects feel alive."""

from math import sin, cos, fabs
from enum import Enum, auto

from pygame import Vector2

from .entity import Entity
from ...utils.get_time import get_time


class FloatStyle(Enum):
    """The available idle motions."""

    FLOAT = 0
    SWING = auto()
    BOUNCE = auto()

    @classmethod
    def from_index(cls, index: int):
        """Returns the FloatStyle corresponding to the given index,
        wrapping around if necessary."""
        members = list(cls)
        return members[index % len(members)]


class FloatAnimation(Entity):
    """Moves its offset in a looping motion.

    Parameters
    ----------
    style: FloatStyle
        Which motion to play.
    phase: float
        Time offset in seconds, so neighbours do not move in sync.
    frequency: float
        How many cycles per second the motion should complete.
    """
    def __init__(
            self,
            style: FloatStyle,
            phase: float = 0.0,
            amplitude: float = 2.0,
            frequency: float = 1.0,
            ) -> None:
        super().__init__()
        match style:
            case FloatStyle.FLOAT:
                self.style = self.animate_float
            case FloatStyle.SWING:
                self.style = self.animate_swing
            case _:
                self.style = self.animate_bounce
        self.phase = phase
        self.amplitude = amplitude
        self.frequency = frequency

    def animate_float(self) -> tuple[float, float]:
        return (
            0.0,
            sin((self.frequency * get_time()) + self.phase) - self.amplitude
        )

    def animate_swing(self) -> tuple[float, float]:
        angle = self.frequency * get_time() * 2 + self.phase
        return cos(angle), sin(angle)

    def animate_bounce(self) -> tuple[float, float]:
        angle = self.frequency * get_time() * 4 + self.phase
        return cos(angle), -2.5 * fabs(sin(angle))

    def update(self, dt: float) -> bool:
        if not self.active:
            return False
        self.offset.update(Vector2(self.style()) * self.amplitude)
        return super().update(dt)
