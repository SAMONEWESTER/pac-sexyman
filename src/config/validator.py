"""Checking raw config data and repairing anything that is wrong."""

import json
from collections.abc import Set
from pathlib import Path
from typing import Any

from ..errors import LOGGER
from .reader import KeyLines
from .schema import (
    DEFAULT_HIGHSCORE_FILENAME,
    DEFAULT_LEVELS,
    INT_RULES,
    KNOWN_KEYS,
    LEVEL_RULES,
    IntRule,
    default_config,
)
from .settings import Config, LevelConfig


class ConfigValidator:
    """Turns parsed JSON into a ``Config``, warning about every problem.

    Missing or wrongly typed values fall back to their default, values
    out of range are clamped, unknown keys are ignored. Every warning
    names the file and, when possible, the line.

    Args:
        path: The config file, used in warning messages.
        key_lines: Line numbers of every key, from ``read_config_file``.
    """

    def __init__(self, path: Path, key_lines: KeyLines) -> None:
        self.path = path
        self.key_lines = key_lines

    def validate(self, data: Any) -> Config:
        """Check all settings and return a complete, safe ``Config``.

        Args:
            data: The parsed JSON content of the config file.
        """
        if not isinstance(data, dict):
            self._warn(None, 'the config must be a JSON object {...}, got '
                             f'{_show(data)}. Using default settings.')
            return default_config()
        self._note_unknown_keys(data, KNOWN_KEYS, 'top level')

        return Config(
            highscore_filename=self._highscore_filename(data),
            levels=self._levels(data),
            lives=self._int(data, 'lives'),
            pacgum=self._int(data, 'pacgum'),
            points_per_pacgum=self._int(data, 'points_per_pacgum'),
            points_per_super_pacgum=self._int(
                data, 'points_per_super_pacgum'),
            points_per_ghost=self._int(data, 'points_per_ghost'),
            seed=self._int(data, 'seed'),
            level_max_time=self._int(data, 'level_max_time'),
        )

    # Single values.
    # -------------------------------------------------------------------------
    def _int(self, data: dict[str, Any], key: str) -> int:
        """Validate a top-level whole-number setting."""
        return self._check_int(
            data, key, INT_RULES[key], label=f"'{key}'",
            where=self._where(key))

    def _check_int(
            self,
            data: dict[str, Any],
            key: str,
            rule: IntRule,
            label: str,
            where: str | None,
            ) -> int:
        """Return ``data[key]`` as a whole number within ``rule``.

        Args:
            data: The JSON object holding the key.
            key: Name of the setting.
            rule: Default and allowed range.
            label: How to name the setting in messages.
            where: File location for messages, ``None`` for no line.
        """
        if key not in data:
            self._warn(where, f'{label} is missing. Using {rule.default}.')
            return rule.default

        value = data[key]
        # bool is a subclass of int in Python, so rule it out explicitly.
        if isinstance(value, bool) or not isinstance(value, int):
            self._warn(where, f'{label} must be a whole number, got '
                              f'{_show(value)}. Using {rule.default}.')
            return rule.default

        clamped = min(max(value, rule.minimum), rule.maximum)
        if clamped != value:
            self._warn(where, f'{label} must be between {rule.minimum} '
                              f'and {rule.maximum}, got {value}. '
                              f'Using {clamped}.')
        return clamped

    def _highscore_filename(self, data: dict[str, Any]) -> str:
        """Validate ``highscore_filename``: a non-empty string."""
        key, default = 'highscore_filename', DEFAULT_HIGHSCORE_FILENAME
        if key not in data:
            self._warn(None, f"'{key}' is missing. Using '{default}'.")
            return default

        value = data[key]
        if not isinstance(value, str) or not value.strip():
            self._warn(self._where(key),
                       f"'{key}' must be a non-empty text, got "
                       f"{_show(value)}. Using '{default}'.")
            return default
        return value.strip()

    # Levels.
    # -------------------------------------------------------------------------
    def _levels(self, data: dict[str, Any]) -> tuple[LevelConfig, ...]:
        """Validate the ``level`` list and every level in it."""
        if 'level' not in data:
            self._warn(None, "'level' is missing. Using the default levels.")
            return DEFAULT_LEVELS

        entries = data['level']
        where = self._where('level')
        if not isinstance(entries, list) or not entries:
            self._warn(where, "'level' must be a non-empty list like "
                              '[{"width": 15, "height": 10}], got '
                              f'{_show(entries)}. Using the default levels.')
            return DEFAULT_LEVELS

        level_line = self._line_of('level')
        seen = {key: 0 for key in LEVEL_RULES}
        result = []
        for number, entry in enumerate(entries, start=1):
            if not isinstance(entry, dict):
                self._warn(where, f'level {number} must be an object like '
                                  '{"width": 15, "height": 10}, got '
                                  f'{_show(entry)}. Using the default size.')
                result.append(_default_level())
                continue
            self._note_unknown_keys(entry, LEVEL_RULES.keys(),
                                    f'level {number}')
            sizes = {}
            for key, rule in LEVEL_RULES.items():
                sizes[key] = self._check_int(
                    entry, key, rule, label=f"'{key}' of level {number}",
                    where=self._where(key, seen[key], after=level_line))
                seen[key] += key in entry
            result.append(LevelConfig(sizes['width'], sizes['height']))
        return tuple(result)

    # Messages.
    # -------------------------------------------------------------------------
    def _note_unknown_keys(
            self, data: dict[str, Any], known: Set[str], place: str,
            ) -> None:
        """Log unknown keys to the log file only; they are ignored."""
        for key in data.keys() - known:
            LOGGER.info('%s: ignoring unknown key %r in %s',
                        self._where(key) or self.path, key, place)

    def _line_of(self, key: str) -> int:
        """Line of the first occurrence of ``key``, or 0 if not found."""
        lines = self.key_lines.get(key, [])
        return lines[0] if lines else 0

    def _where(self, key: str, occurrence: int = 0, after: int = 0) -> str:
        """Return ``file:line`` for a key, or just the file if unknown.

        Args:
            key: The key to look up.
            occurrence: Which appearance of the key, counting from 0.
            after: Only count appearances below this line.
        """
        lines = [n for n in self.key_lines.get(key, []) if n > after]
        if occurrence < len(lines):
            return f'{self.path}:{lines[occurrence]}'
        return str(self.path)

    def _warn(self, where: str | None, message: str) -> None:
        """Log a config warning prefixed with its location."""
        LOGGER.warning('%s: %s', where or self.path, message)


def _default_level() -> LevelConfig:
    """A level with the default width and height."""
    return LevelConfig(LEVEL_RULES['width'].default,
                       LEVEL_RULES['height'].default)


def _show(value: Any, limit: int = 40) -> str:
    """Show a value the way it looks in JSON, shortened if long."""
    text = json.dumps(value)
    return text if len(text) <= limit else text[:limit - 3] + '...'
