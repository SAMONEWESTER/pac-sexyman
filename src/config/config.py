import json
from pathlib import Path
from typing import Annotated

from pydantic import (
    BaseModel,
    Field,
    StringConstraints,
    field_validator,
    ValidationError,
    ConfigDict
)

from ..errors import LOGGER, ConfigError


PlayerName = Annotated[
    str,
    StringConstraints(
        min_length=1,
        max_length=10,
        pattern=r'^[A-Za-z0-9 _-]+$',
        strip_whitespace=True,
        to_upper=True,
    ),
]
"""A leaderboard name: 1 to 10 letters, digits, spaces, ``_`` or ``-``."""

DEFAULT_PLAYER_NAMES: tuple[str, str, str, str] = ('P1', 'P2', 'P3', 'P4')
"""Names used on the leaderboard when the config does not set them."""


class LevelConfig(BaseModel):
    model_config = ConfigDict(extra="forbid")

    size: tuple[
        Annotated[int, Field(ge=1)],
        Annotated[int, Field(ge=1)],
    ] = (15, 11)


class Config(BaseModel):
    model_config = ConfigDict(extra="forbid")

    lives: int = Field(default=3, ge=0)
    points_per_dot: int = Field(default=10, ge=0)
    points_per_powerpellet: int = Field(default=50, ge=0)
    points_per_ghost: int = Field(default=200, ge=0)
    seed: int = Field(default=42)
    time_multiplier: float = Field(default=0.75, ge=0.1, allow_inf_nan=False)
    highscore_filename: Annotated[
        str,
        StringConstraints(
            min_length=1,
            max_length=32,
            pattern=r'^[a-zA-Z0-9_.-]+$',
            strip_whitespace=True,
        ),
    ] = Field(default="highscores.txt")
    cheatmode: bool = False
    online_leaderboard: bool = True
    player_names: tuple[PlayerName, ...] = Field(
        default=DEFAULT_PLAYER_NAMES,
        min_length=1,
        max_length=4,
    )
    levels: tuple[LevelConfig, ...] = Field(
        default=(LevelConfig(),),
        min_length=1,
    )

    @field_validator("highscore_filename")
    @classmethod
    def validate_filename(cls, value: str) -> str:
        if value in {".", ".."}:
            raise ValueError("Invalid filename")
        return value

    def player_name(self, index: int) -> str:
        """Leaderboard name of a player slot, a default one if unset.

        Args:
            index: Player slot, 0 to 3.
        """
        if index < len(self.player_names):
            return self.player_names[index]
        return DEFAULT_PLAYER_NAMES[index]


def load_config(path: str | Path) -> Config:
    """Load and validate a config file. Never raises.

    If the file cannot be used at all, every setting gets its default.
    Smaller problems are repaired one setting at a time. Either way,
    every problem is logged as a warning.

    Args:
        path: Location of the config file.

    Returns:
        A complete config with every value in its safe range.
    """
    if not path:
        LOGGER.info('No config file provided. Using default settings.')
        return Config()

    path = Path(path)
    try:
        return __read_config(path)
    except ConfigError as err:
        LOGGER.warning('%s\nUsing default settings.', err)
        return Config()


def __read_config(path: Path) -> Config:
    """Read a config file, ignoring lines that start with ``#``.

    Comment lines are blanked instead of removed, so line numbers in
    error messages match the real file.

    Args:
        path: Location of the config file.

    Returns:
        The parsed JSON data as a validated Config object.

    Raises:
        ConfigError: If the file cannot be read or is not valid JSON.
    """
    try:
        with open(path, encoding='utf-8') as file:
            lines = [line for line in file.readlines()
                     if not line.strip().startswith("#")]
    except UnicodeDecodeError as e:
        raise ConfigError(f"'{path}' is not a UTF-8 text file") from e
    except OSError as e:
        raise ConfigError(
            f"cannot read config file '{path}' ({e.strerror})") from e

    try:
        return Config(**json.loads(''.join(lines)))
    except ValidationError as e:
        details = "; ".join(
            f"{'.'.join(str(x) for x in err['loc'])}: {err['msg']}"
            for err in e.errors()
        )
        raise ConfigError(f"Invalid configuration: {details}") from e
    except json.JSONDecodeError as e:
        raise ConfigError(
            f'{path}:{e.lineno}: invalid JSON, {e.msg} '
            f'(column {e.colno})') from e
    except RecursionError as e:
        raise ConfigError(f'{path}: JSON is nested too deeply') from e
