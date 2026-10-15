"""Turning exceptions into short, readable error reports."""

import traceback
from pathlib import Path

from .exceptions import PacManError
from .logger import LOGGER

PROJECT_ROOT: Path = Path(__file__).resolve().parents[2]
SRC_DIR: Path = PROJECT_ROOT / 'src'


def format_error(error: BaseException) -> str:
    """Build a short report: message, cause and where in ``src/`` it came from.

    Example::

        AssetError: cannot load image 'assets/gfx/obj/pac_dot.png'
          caused by FileNotFoundError: No file 'assets/...' found
          at src/resources/assets.py:55 in _load_quick
          at src/resources/assets.py:37 in load_all

    Args:
        error: The exception to describe.

    Returns:
        The report, most recent location first.
    """
    lines = [f'{type(error).__name__}: {error}']
    cause = error.__cause__
    if cause is not None:
        lines.append(f'  caused by {type(cause).__name__}: {cause}')

    show_trace = error.show_trace if isinstance(error, PacManError) else True
    if show_trace:
        lines.extend(_code_locations(error))
    return '\n'.join(lines)


def report_error(error: BaseException) -> None:
    """Log an error report. Errors that are not ours are flagged as bugs.

    Args:
        error: The exception to report.
    """
    if isinstance(error, PacManError):
        LOGGER.error(format_error(error))
    else:
        LOGGER.error('Unexpected error, this is a bug:\n%s',
                     format_error(error))


def _code_locations(error: BaseException) -> list[str]:
    """List the traceback steps that are inside ``src/``, newest first."""
    result = []
    for frame in reversed(traceback.extract_tb(error.__traceback__)):
        path = Path(frame.filename).resolve()
        if path.is_relative_to(SRC_DIR):
            location = path.relative_to(PROJECT_ROOT).as_posix()
            result.append(f'  at {location}:{frame.lineno} in {frame.name}')
    return result
