"""Command-line argument handling."""

from collections.abc import Sequence
from pathlib import Path

from ..errors import LOGGER, UsageError

USAGE: str = 'usage: python3 pac-man.py <config.json>'


def parse_args(argv: Sequence[str]) -> Path:
    """Return the config file path, the one and only argument.

    Args:
        argv: Command-line arguments, without the program name.

    Raises:
        UsageError: If there is not exactly one argument.
    """
    if len(argv) != 1:
        raise UsageError(
            f'expected exactly 1 argument (a config file), got {len(argv)}.'
            f'\n{USAGE}')

    path = Path(argv[0])
    if path.suffix.lower() != '.json':
        LOGGER.warning("'%s' does not end in .json, reading it anyway.", path)
    return path
