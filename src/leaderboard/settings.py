"""Fixed settings of the online leaderboard.

Fill in the two Firebase values below with the ones from your own
Firebase project (Project settings > General > Your apps > Web app).
Both are public by design: what protects the data are the Firestore
security rules in ``firestore.rules``, not these values.

While either value is empty the leaderboard is switched off and the game
plays offline as before.
"""

FIREBASE_API_KEY: str = 'AIzaSyAiSuMdfCx-n6GNIv-g7kv1RnCYGLCPb3Y'
"""The ``apiKey`` of your Firebase web app config."""

FIREBASE_PROJECT_ID: str = 'pac-male'
"""The ``projectId`` of your Firebase web app config."""

RULES_VERSION: int = 1
"""Raise this by one when a gameplay change makes old scores unfair.

It is part of the ruleset id, so a new version starts a fresh board
while the old scores stay stored under the old id.
"""

TOP_SIZE: int = 10
"""How many scores the game downloads and shows."""

REQUEST_TIMEOUT: float = 8.0
"""Seconds to wait for Firebase before giving up on a request."""

GAME_OVER_SECONDS: float = 10.0
"""How long the game over screen with the leaderboard stays up."""

GAME_OVER_SKIP_DELAY: float = 1.0
"""Seconds before a confirm key may skip the game over screen.

Stops a player who is still mashing keys from skipping it by accident.
"""

SESSION_FILE_NAME: str = 'leaderboard-session.json'
"""File in ``~/.pac-man/`` that remembers the anonymous sign-in."""
