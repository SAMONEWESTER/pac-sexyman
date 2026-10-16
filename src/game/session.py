"""Score, lives and level of the current play-through."""

from dataclasses import dataclass


@dataclass
class Session:
    """Everything that carries over from one level to the next.

    Attributes:
        lives: Lives left; the game is over at 0.
        score: Points scored so far.
        level: Current level number, starting at 1.
    """

    lives: int
    score: int = 0
    level: int = 1

    @property
    def is_over(self) -> bool:
        """Whether all lives are lost."""
        return self.lives <= 0
