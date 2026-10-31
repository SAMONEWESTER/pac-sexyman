"""Player input: actions and the (rebindable) keys that trigger them.

Game code asks about *actions* ("is MOVE_UP pressed?"), never about
specific keys, so keys can be rebound without touching game code.
"""

from .actions import P1_DIRECTIONS, P2_DIRECTIONS, Action
from .bindings import DEFAULT_BINDINGS, Controls

__all__ = [
    'Action',
    'Controls',
    'DEFAULT_BINDINGS',
    'P1_DIRECTIONS',
    'P2_DIRECTIONS',
]
