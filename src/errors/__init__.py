"""Custom exceptions, logging and error reports.

Every error the game raises on purpose is a ``PacManError``. Warnings
and errors go to the terminal and to ``pac-man.log`` through ``LOGGER``.
"""

from .exceptions import (
    AssetError,
    ConfigError,
    DisplayError,
    MazeError,
    PacManError,
    UsageError,
)
from .logger import LOG_PATH, LOGGER, setup_logging
from .reporting import format_error, report_error

__all__ = [
    'AssetError',
    'ConfigError',
    'DisplayError',
    'LOGGER',
    'LOG_PATH',
    'MazeError',
    'PacManError',
    'UsageError',
    'format_error',
    'report_error',
    'setup_logging',
]
