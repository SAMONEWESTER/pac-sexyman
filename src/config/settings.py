"""The validated settings the rest of the game reads from."""

from dataclasses import dataclass


@dataclass(frozen=True)
class LevelConfig:
    """Settings for one level.

    Attributes:
        width: Maze width, in cells.
        height: Maze height, in cells.
    """

    width: int
    height: int

    @property
    def size(self) -> tuple[int, int]:
        """Maze size as ``(width, height)``, in cells."""
        return self.width, self.height


@dataclass(frozen=True)
class Config:
    """All game settings, always complete and within safe ranges.

    See ``schema.py`` for every default and allowed range.
    """

    highscore_filename: str
    levels: tuple[LevelConfig, ...]
    lives: int
    pacgum: int
    points_per_pacgum: int
    points_per_super_pacgum: int
    points_per_ghost: int
    seed: int
    level_max_time: int
