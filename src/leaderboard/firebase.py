"""Talking to Firebase over its REST API.

Only the standard library is used for HTTP, so the PyInstaller build
needs nothing extra. ``certifi`` supplies the certificate list, because
a frozen build cannot always find the system one (macOS especially).

Every call here blocks and raises ``LeaderboardError`` on failure. Run
them from ``Leaderboard``'s background thread, never from the game loop.
"""

from __future__ import annotations

import json
import secrets
import ssl
import time
import urllib.error
import urllib.parse
import urllib.request
from collections.abc import Callable
from pathlib import Path
from typing import Any

import certifi

from ..errors import LOGGER, LeaderboardError
from .models import ScoreEntry
from .settings import REQUEST_TIMEOUT

SIGN_UP_URL: str = 'https://identitytoolkit.googleapis.com/v1/accounts:signUp'
"""Creates an anonymous Firebase account."""

REFRESH_URL: str = 'https://securetoken.googleapis.com/v1/token'
"""Trades a refresh token for a new id token."""

FIRESTORE_URL: str = 'https://firestore.googleapis.com/v1'
"""Root of the Firestore REST API."""

TOKEN_MARGIN: float = 60.0
"""Seconds before expiry at which an id token is renewed."""

SCORES: str = 'scores'
"""Name of the score collection inside each ruleset."""

_SSL_CONTEXT = ssl.create_default_context(cafile=certifi.where())

JsonObject = dict[str, Any]


class HttpError(LeaderboardError):
    """Firebase answered, but with an error status.

    Attributes:
        status: The HTTP status code, e.g. 401 or 403.
    """

    def __init__(self, status: int, message: str) -> None:
        super().__init__(f'Firebase refused the request ({status}: {message})')
        self.status = status


# HTTP.
# ------------------------------------------------------------------------------
def _send(
        url: str,
        body: JsonObject | None = None,
        *,
        form: dict[str, str] | None = None,
        token: str = '',
        ) -> Any:
    """POST JSON (or a form) and return the decoded JSON answer.

    Args:
        url: Where to send the request.
        body: JSON body to send.
        form: Form fields to send instead of a JSON body.
        token: Firebase id token for the ``Authorization`` header.

    Raises:
        HttpError: If Firebase answers with an error status.
        LeaderboardError: If Firebase cannot be reached or answers junk.
    """
    if form is not None:
        data = urllib.parse.urlencode(form).encode('utf-8')
        content_type = 'application/x-www-form-urlencoded'
    else:
        data = json.dumps(body or {}).encode('utf-8')
        content_type = 'application/json'

    request = urllib.request.Request(url, data=data, method='POST')
    request.add_header('Content-Type', content_type)
    if token:
        request.add_header('Authorization', f'Bearer {token}')

    try:
        with urllib.request.urlopen(
                request, timeout=REQUEST_TIMEOUT,
                context=_SSL_CONTEXT) as response:
            return json.loads(response.read().decode('utf-8'))
    except urllib.error.HTTPError as err:
        raise HttpError(err.code, _error_message(err)) from err
    except (urllib.error.URLError, TimeoutError, OSError) as err:
        raise LeaderboardError('cannot reach Firebase (offline?)') from err
    except ValueError as err:
        raise LeaderboardError('Firebase sent an unreadable answer') from err


def _send_for_object(
        url: str,
        body: JsonObject | None = None,
        *,
        form: dict[str, str] | None = None,
        ) -> JsonObject:
    """Like ``_send``, but the answer must be a JSON object.

    Raises:
        LeaderboardError: If the answer is anything else.
    """
    answer = _send(url, body, form=form)
    if not isinstance(answer, dict):
        raise LeaderboardError('Firebase sent an unexpected answer')
    return answer


def _error_message(err: urllib.error.HTTPError) -> str:
    """Pull Firebase's own error text out of an error response."""
    try:
        answer = json.loads(err.read().decode('utf-8'))
    except (OSError, ValueError):
        return str(err.reason)
    # runQuery wraps its error in a list, the other endpoints do not.
    if isinstance(answer, list) and answer:
        answer = answer[0]
    if isinstance(answer, dict) and isinstance(answer.get('error'), dict):
        return str(answer['error'].get('message', err.reason))
    return str(err.reason)


# Sign-in.
# ------------------------------------------------------------------------------
class AnonymousSession:
    """An anonymous Firebase account that is remembered between runs.

    The refresh token is saved to a small file, so the same player keeps
    the same account instead of a new one being made on every start.

    Args:
        api_key: The Firebase web API key.
        session_path: File that stores the refresh token.
    """

    def __init__(self, api_key: str, session_path: Path) -> None:
        self.api_key = api_key
        self.session_path = session_path
        self.uid = ''
        self._id_token = ''
        self._refresh_token = ''
        self._expires_at = 0.0
        self._load()

    def token(self) -> str:
        """Return a valid id token, renewing or signing up when needed.

        Raises:
            LeaderboardError: If no token can be obtained.
        """
        if self._id_token and time.monotonic() < self._expires_at:
            return self._id_token
        if self._refresh_token:
            try:
                self._refresh()
                return self._id_token
            except HttpError as err:
                # 400 means the saved account is gone or revoked.
                if err.status != 400:
                    raise
                LOGGER.info('leaderboard: saved sign-in expired, new one')
        self._sign_up()
        return self._id_token

    def invalidate(self) -> None:
        """Forget the id token, so the next ``token()`` renews it."""
        self._expires_at = 0.0

    def _sign_up(self) -> None:
        answer = _send_for_object(
            f'{SIGN_UP_URL}?key={self.api_key}',
            {'returnSecureToken': True})
        self._store(
            answer.get('idToken'),
            answer.get('refreshToken'),
            answer.get('localId'),
            answer.get('expiresIn'))
        LOGGER.info('leaderboard: signed in anonymously as %s', self.uid)

    def _refresh(self) -> None:
        answer = _send_for_object(
            f'{REFRESH_URL}?key={self.api_key}',
            form={
                'grant_type': 'refresh_token',
                'refresh_token': self._refresh_token,
            })
        self._store(
            answer.get('id_token'),
            answer.get('refresh_token'),
            answer.get('user_id'),
            answer.get('expires_in'))

    def _store(
            self,
            id_token: object,
            refresh_token: object,
            uid: object,
            expires_in: object,
            ) -> None:
        if not (isinstance(id_token, str) and isinstance(refresh_token, str)
                and isinstance(uid, str)):
            raise LeaderboardError('Firebase sign-in answer is incomplete')
        try:
            lifetime = float(str(expires_in))
        except ValueError:
            lifetime = 3600.0
        self._id_token = id_token
        self._expires_at = time.monotonic() + lifetime - TOKEN_MARGIN
        if (refresh_token, uid) != (self._refresh_token, self.uid):
            self._refresh_token = refresh_token
            self.uid = uid
            self._save()

    def _load(self) -> None:
        try:
            saved = json.loads(self.session_path.read_text(encoding='utf-8'))
        except (OSError, ValueError):
            return
        if isinstance(saved, dict):
            self._refresh_token = str(saved.get('refresh_token', ''))
            self.uid = str(saved.get('uid', ''))

    def _save(self) -> None:
        try:
            self.session_path.parent.mkdir(parents=True, exist_ok=True)
            self.session_path.write_text(
                json.dumps({
                    'uid': self.uid,
                    'refresh_token': self._refresh_token,
                }),
                encoding='utf-8')
        except OSError as err:
            LOGGER.info(
                "leaderboard: cannot save sign-in to '%s' (%s)",
                self.session_path, err.strerror)


# Firestore.
# ------------------------------------------------------------------------------
class FirebaseClient:
    """Adds scores to and reads the top of a Firestore leaderboard.

    Scores live at ``rulesets/{ruleset}/scores/{id}``, one board per
    ruleset (see ``ruleset.py``).

    Args:
        api_key: The Firebase web API key.
        project_id: The Firebase project id.
        session_path: File that remembers the anonymous sign-in.
    """

    def __init__(
            self,
            api_key: str,
            project_id: str,
            session_path: Path,
            ) -> None:
        self.session = AnonymousSession(api_key, session_path)
        self.documents = (
            f'projects/{project_id}/databases/(default)/documents')

    def submit(self, ruleset: str, name: str, score: int, level: int) -> str:
        """Add one score to a board.

        Args:
            ruleset: Id of the board.
            name: Player name, already validated by the config.
            score: Points of the whole run.
            level: Highest level reached, counting from 1.

        Returns:
            The id of the new score document.

        Raises:
            LeaderboardError: If the score could not be stored.
        """
        entry_id = secrets.token_hex(10)
        path = f'{self.documents}/rulesets/{ruleset}/{SCORES}/{entry_id}'

        def commit(token: str) -> None:
            # The uid is only known once signed in, so build fields here.
            fields = {
                'name': {'stringValue': name},
                'score': {'integerValue': str(score)},
                'level': {'integerValue': str(level)},
                'uid': {'stringValue': self.session.uid},
            }
            _send(
                f'{FIRESTORE_URL}/{self.documents}:commit',
                {'writes': [{
                    'update': {'name': path, 'fields': fields},
                    # Only create, never overwrite.
                    'currentDocument': {'exists': False},
                    # The server's clock, so nobody can fake the date.
                    'updateTransforms': [{
                        'fieldPath': 'createdAt',
                        'setToServerValue': 'REQUEST_TIME',
                    }],
                }]},
                token=token)

        self._signed_in(commit)
        return entry_id

    def top(self, ruleset: str, size: int) -> list[ScoreEntry]:
        """Download the best scores of a board, best first.

        Args:
            ruleset: Id of the board.
            size: How many scores to fetch.

        Raises:
            LeaderboardError: If the board could not be read.
        """
        answer = _send(
            f'{FIRESTORE_URL}/{self.documents}/rulesets/{ruleset}:runQuery',
            {'structuredQuery': {
                'from': [{'collectionId': SCORES}],
                'orderBy': [{
                    'field': {'fieldPath': 'score'},
                    'direction': 'DESCENDING',
                }],
                'limit': size,
            }})
        if not isinstance(answer, list):
            raise LeaderboardError('Firebase sent an unexpected board')
        entries = (_parse_entry(row.get('document')) for row in answer
                   if isinstance(row, dict))
        return [entry for entry in entries if entry is not None]

    def _signed_in(self, call: Callable[[str], None]) -> None:
        """Run ``call(token)``, renewing the token once if it expired."""
        try:
            call(self.session.token())
        except HttpError as err:
            if err.status != 401:
                raise
            self.session.invalidate()
            call(self.session.token())


def _parse_entry(document: object) -> ScoreEntry | None:
    """Turn a Firestore document into a ``ScoreEntry``; ``None`` if junk."""
    if not isinstance(document, dict):
        return None
    fields = document.get('fields', {})
    try:
        return ScoreEntry(
            entry_id=str(document['name']).rsplit('/', 1)[-1],
            name=str(fields['name']['stringValue']),
            score=int(fields['score']['integerValue']),
            level=int(fields['level']['integerValue']),
        )
    except (KeyError, TypeError, ValueError):
        return None
