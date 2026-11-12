"""The leaderboard the game talks to: never blocks, never raises.

Network calls run one after another on a background thread. The game
only queues work (``submit``, ``refresh``) and reads the last known
results (``entries``, ``status``), so a slow or missing connection can
never freeze a frame or stop the game.
"""

from __future__ import annotations

import queue
import threading
from collections.abc import Callable
from pathlib import Path

from ..config import Config
from ..errors import LOGGER, LeaderboardError
from .firebase import FirebaseClient
from .models import LeaderboardStatus, ScoreEntry
from .ruleset import ruleset_id
from .settings import (
    FIREBASE_API_KEY,
    FIREBASE_PROJECT_ID,
    SESSION_FILE_NAME,
    TOP_SIZE,
)

Job = Callable[[], None]


class Leaderboard:
    """The global high score board for the current ruleset.

    Args:
        config: The validated game settings.
    """

    def __init__(self, config: Config) -> None:
        self.ruleset = ruleset_id(config)
        self.ranked = not config.cheatmode
        """Whether scores of this session may be submitted."""

        self._entries: tuple[ScoreEntry, ...] = ()
        self._own_ids: set[str] = set()
        self._status = LeaderboardStatus.DISABLED
        self._lock = threading.Lock()
        self._jobs: queue.Queue[Job | None] = queue.Queue()
        self._client: FirebaseClient | None = None
        self._thread: threading.Thread | None = None

        if not config.online_leaderboard:
            LOGGER.info('leaderboard: switched off in the config')
            return
        if not (FIREBASE_API_KEY and FIREBASE_PROJECT_ID):
            LOGGER.info('leaderboard: Firebase not set up, playing offline')
            return
        if not self.ranked:
            LOGGER.warning('Cheats are on: scores will not be submitted.')

        LOGGER.info('leaderboard: ruleset %s', self.ruleset)
        self._client = FirebaseClient(
            FIREBASE_API_KEY,
            FIREBASE_PROJECT_ID,
            Path.home() / '.pac-man' / SESSION_FILE_NAME)
        self._status = LeaderboardStatus.LOADING
        self._thread = threading.Thread(
            target=self._work, name='leaderboard', daemon=True)
        self._thread.start()
        self.refresh()

    # Read by the game (main thread).
    # --------------------------------------------------------------------------
    @property
    def entries(self) -> tuple[ScoreEntry, ...]:
        """The last downloaded top scores, best first."""
        with self._lock:
            return self._entries

    @property
    def status(self) -> LeaderboardStatus:
        """What the leaderboard is doing, for the UI."""
        with self._lock:
            return self._status

    def is_own(self, entry: ScoreEntry) -> bool:
        """Whether an entry was submitted during this session."""
        with self._lock:
            return entry.entry_id in self._own_ids

    # Called by the game (main thread).
    # --------------------------------------------------------------------------
    def submit(self, name: str, score: int, level: int) -> bool:
        """Queue a finished run for the board.

        Args:
            name: Player name.
            score: Points of the whole run, every level added up.
            level: Highest level reached, counting from 1.

        Returns:
            Whether the score was queued; ``False`` when offline by
            choice, with cheats on, or for an empty score.
        """
        client = self._client
        if client is None or not self.ranked or score <= 0:
            return False

        def job() -> None:
            entry_id = client.submit(self.ruleset, name, score, level)
            LOGGER.info(
                'leaderboard: submitted %s with %d points (level %d)',
                name, score, level)
            with self._lock:
                self._own_ids.add(entry_id)

        self._jobs.put(job)
        return True

    def refresh(self) -> None:
        """Queue a download of the top scores.

        Queued after ``submit`` calls, it shows the new scores.
        """
        client = self._client
        if client is None:
            return

        def job() -> None:
            entries = tuple(client.top(self.ruleset, TOP_SIZE))
            with self._lock:
                self._entries = entries
                self._status = LeaderboardStatus.READY

        self._jobs.put(job)

    def close(self, timeout: float = 3.0) -> None:
        """Let queued work finish, waiting at most ``timeout`` seconds.

        Gives a score submitted just before quitting a chance to arrive.
        """
        if self._thread is None:
            return
        self._jobs.put(None)
        self._thread.join(timeout)

    # Background thread.
    # --------------------------------------------------------------------------
    def _work(self) -> None:
        """Run queued jobs one by one until ``close`` is called."""
        while True:
            job = self._jobs.get()
            if job is None:
                return
            try:
                job()
            except LeaderboardError as err:
                self._fail(str(err))
            except Exception as err:  # A bug here must not end the thread.
                self._fail(f'unexpected {type(err).__name__}: {err}')

    def _fail(self, reason: str) -> None:
        LOGGER.warning('Leaderboard: %s', reason)
        with self._lock:
            self._status = LeaderboardStatus.OFFLINE
