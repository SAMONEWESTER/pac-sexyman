"""Grouping scores by the settings they were played with.

Scores only compare fairly when they were played with the same rules.
Every set of rules gets its own short id, and every id its own board,
so a player who edits ``config.json`` (more points per dot, tiny mazes)
never lands on the same board as everyone else.
"""

import hashlib
import json

from ..config import Config
from .settings import RULES_VERSION

RULESET_ID_LENGTH: int = 12
"""Hex characters in a ruleset id; ``firestore.rules`` checks this too."""


def ruleset_id(config: Config) -> str:
    """Return the id of the board a config's scores belong on.

    Only settings that change how many points a run can make are used.
    Names, the cheat flag and the file names do not count.

    Args:
        config: The validated game settings.

    Returns:
        A 12 character lowercase hex string.
    """
    rules = {
        'version': RULES_VERSION,
        'lives': config.lives,
        'points_per_dot': config.points_per_dot,
        'points_per_powerpellet': config.points_per_powerpellet,
        'points_per_ghost': config.points_per_ghost,
        'seed': config.seed,
        'time_multiplier': config.time_multiplier,
        'levels': [list(level.size) for level in config.levels],
    }
    text = json.dumps(rules, sort_keys=True, separators=(',', ':'))
    digest = hashlib.sha256(text.encode('utf-8')).hexdigest()
    return digest[:RULESET_ID_LENGTH]
