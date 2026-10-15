"""Logging to the terminal and to a log file."""

import logging
import sys
from pathlib import Path

LOG_PATH: Path = Path('pac-man.log')
"""Log file, rewritten on every run."""

LOGGER: logging.Logger = logging.getLogger('pacman')
"""The one logger the whole game writes to."""

_CONSOLE_FORMAT = '[%(levelname)s] %(message)s'
_FILE_FORMAT = '%(asctime)s [%(levelname)s] %(message)s'
_DATE_FORMAT = '%Y-%m-%d %H:%M:%S'


def setup_logging(log_path: Path = LOG_PATH) -> None:
    """Send warnings and errors to stderr, and everything to a log file.

    If the log file cannot be opened, the game keeps going with
    terminal output only.

    Args:
        log_path: Where to write the log file.
    """
    # Never let a failing log write print its own Python traceback.
    logging.raiseExceptions = False

    LOGGER.setLevel(logging.INFO)
    LOGGER.propagate = False
    LOGGER.handlers.clear()

    console = logging.StreamHandler(sys.stderr)
    console.setLevel(logging.WARNING)
    console.setFormatter(logging.Formatter(_CONSOLE_FORMAT))
    LOGGER.addHandler(console)

    try:
        log_file = logging.FileHandler(log_path, mode='w', encoding='utf-8')
    except OSError as err:
        LOGGER.warning(
            "cannot write log file '%s' (%s). Logging to the terminal only.",
            log_path, err.strerror)
        return
    log_file.setLevel(logging.INFO)
    log_file.setFormatter(logging.Formatter(_FILE_FORMAT, _DATE_FORMAT))
    LOGGER.addHandler(log_file)
