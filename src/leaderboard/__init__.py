"""The online global leaderboard, stored in Firebase Firestore.

Usage from the game::

    board = Leaderboard(config)
    board.submit('SAM', 12340, 5)   # queued, sent in the background
    board.refresh()                 # queued, downloads the top scores
    board.entries                   # last known top scores, best first

Set up Firebase first: see ``settings.py`` and ``firestore.rules``.
"""

from .models import LeaderboardStatus, ScoreEntry
from .ruleset import ruleset_id
from .service import Leaderboard
from .settings import GAME_OVER_SECONDS, GAME_OVER_SKIP_DELAY

__all__ = [
    'GAME_OVER_SECONDS',
    'GAME_OVER_SKIP_DELAY',
    'Leaderboard',
    'LeaderboardStatus',
    'ScoreEntry',
    'ruleset_id',
]
