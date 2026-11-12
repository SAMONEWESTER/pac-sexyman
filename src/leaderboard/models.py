"""Plain data the leaderboard hands to the rest of the game."""

from dataclasses import dataclass
from enum import Enum, auto


class LeaderboardStatus(Enum):
    """What the leaderboard is doing right now, for the UI."""

    DISABLED = auto()
    """Switched off in the config, or Firebase is not set up yet."""

    LOADING = auto()
    """Waiting for the first answer from Firebase."""

    READY = auto()
    """The scores shown are fresh."""

    OFFLINE = auto()
    """The last request failed; the scores shown may be old or empty."""


@dataclass(frozen=True)
class ScoreEntry:
    """One line of the leaderboard.

    Attributes:
        entry_id: Firestore document id, used to highlight new entries.
        name: Player name, upper case.
        score: Points of the whole run, every level added up.
        level: Highest level reached in that run, counting from 1.
    """

    entry_id: str
    name: str
    score: int
    level: int
