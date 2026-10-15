"""Loading the config file into a validated ``Config``."""

from pathlib import Path

from ..errors import LOGGER, ConfigError
from .reader import read_config_file
from .schema import default_config
from .settings import Config
from .validator import ConfigValidator


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
    path = Path(path)
    try:
        data, key_lines = read_config_file(path)
    except ConfigError as err:
        LOGGER.warning('%s. Using default settings.', err)
        return default_config()

    config = ConfigValidator(path, key_lines).validate(data)
    LOGGER.info('loaded config from %s', path)
    return config
