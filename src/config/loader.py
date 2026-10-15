"""Reading the JSON-with-comments configuration file."""

import json
from pathlib import Path
from typing import Any


def load_config(path: str | Path) -> dict[str, Any]:
    """Load a JSON config file, ignoring lines that start with ``#``.

    Args:
        path: Location of the configuration file.

    Returns:
        The parsed configuration.
    """
    with open(path) as file:
        lines = (line for line in file if not line.strip().startswith('#'))
        config: dict[str, Any] = json.loads(''.join(lines))
    return config
