"""Reading the JSON-with-comments config file from disk."""

import json
import re
from pathlib import Path
from typing import Any

from ..errors import ConfigError

KeyLines = dict[str, list[int]]
"""For every key name, the file line numbers it appears on, in order."""

_KEY_PATTERN = re.compile(r'"((?:[^"\\]|\\.)*)"\s*:')


def read_config_file(path: Path) -> tuple[Any, KeyLines]:
    """Read a config file, ignoring lines that start with ``#``.

    Comment lines are blanked instead of removed, so line numbers in
    error messages match the real file.

    Args:
        path: Location of the config file.

    Returns:
        The parsed JSON data and the line numbers of every key.

    Raises:
        ConfigError: If the file cannot be read or is not valid JSON.
    """
    lines = [
        '\n' if line.lstrip().startswith('#') else line
        for line in _read_lines(path)
    ]
    try:
        data = json.loads(''.join(lines))
    except json.JSONDecodeError as err:
        raise ConfigError(
            f'{path}:{err.lineno}: invalid JSON, {err.msg} '
            f'(column {err.colno})') from err
    except RecursionError as err:
        raise ConfigError(f'{path}: JSON is nested too deeply') from err
    return data, _find_key_lines(lines)


def _read_lines(path: Path) -> list[str]:
    """Return all lines of a text file, or raise a ``ConfigError``."""
    try:
        with open(path, encoding='utf-8') as file:
            return file.readlines()
    except FileNotFoundError as err:
        raise ConfigError(f"config file '{path}' not found") from err
    except IsADirectoryError as err:
        raise ConfigError(f"'{path}' is a folder, not a file") from err
    except UnicodeDecodeError as err:
        raise ConfigError(f"'{path}' is not a UTF-8 text file") from err
    except OSError as err:
        raise ConfigError(
            f"cannot read config file '{path}' ({err.strerror})") from err


def _find_key_lines(lines: list[str]) -> KeyLines:
    """Find on which line every ``"key":`` appears (1-based)."""
    result: KeyLines = {}
    for number, line in enumerate(lines, start=1):
        for match in _KEY_PATTERN.finditer(line):
            result.setdefault(match.group(1), []).append(number)
    return result
