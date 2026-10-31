"""Every config key, its default and its allowed range.

To add a whole-number setting: add a rule to ``INT_RULES``, a field to
``Config`` in ``settings.py`` and one line in ``ConfigValidator.validate``.
"""

from dataclasses import dataclass

from .settings import Config, LevelConfig


@dataclass(frozen=True)
class IntRule:
    """Allowed range and fallback value for a whole-number setting.

    Attributes:
        default: Used when the value is missing or not a whole number.
        minimum: Smaller values are raised to this.
        maximum: Larger values are lowered to this.
    """

    default: int
    minimum: int
    maximum: int


INT_RULES: dict[str, IntRule] = {
    'lives': IntRule(default=3, minimum=0, maximum=9),
    'pacgum': IntRule(default=42, minimum=0, maximum=1000),
    'points_per_pacgum': IntRule(default=10, minimum=0, maximum=100_000),
    'points_per_super_pacgum':
        IntRule(default=50, minimum=0, maximum=100_000),
    'points_per_ghost': IntRule(default=200, minimum=0, maximum=100_000),
    'seed': IntRule(default=42, minimum=0, maximum=2**31 - 1),
    'level_max_time': IntRule(default=90, minimum=10, maximum=3600),
}

# 14x10 is the smallest maze that still fits the 42 pattern,
# 50x30 is a 1600x960 pixel window.
LEVEL_RULES: dict[str, IntRule] = {
    'width': IntRule(default=15, minimum=14, maximum=50),
    'height': IntRule(default=10, minimum=10, maximum=30),
}

DEFAULT_HIGHSCORE_FILENAME: str = 'highscore.txt'
DEFAULT_LEVELS: tuple[LevelConfig, ...] = (
    LevelConfig(width=15, height=10),
    LevelConfig(width=30, height=15),
)

KNOWN_KEYS: frozenset[str] = frozenset(
    {'highscore_filename', 'level', *INT_RULES})


def default_config() -> Config:
    """Return a config where every setting has its default value."""
    return Config(
        highscore_filename=DEFAULT_HIGHSCORE_FILENAME,
        levels=DEFAULT_LEVELS,
        lives=INT_RULES['lives'].default,
        pacgum=INT_RULES['pacgum'].default,
        points_per_pacgum=INT_RULES['points_per_pacgum'].default,
        points_per_super_pacgum=INT_RULES['points_per_super_pacgum'].default,
        points_per_ghost=INT_RULES['points_per_ghost'].default,
        seed=INT_RULES['seed'].default,
        level_max_time=INT_RULES['level_max_time'].default,
    )
