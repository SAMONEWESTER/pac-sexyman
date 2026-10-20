"""Everything the player can do with a key."""

from enum import Enum, auto

from ..grid import Direction


class Action(Enum):
    """A player action, independent of which key triggers it."""

    MOVE_UP = auto()
    MOVE_DOWN = auto()
    MOVE_LEFT = auto()
    MOVE_RIGHT = auto()
    MOVE_UP_P2 = auto()
    MOVE_DOWN_P2 = auto()
    MOVE_LEFT_P2 = auto()
    MOVE_RIGHT_P2 = auto()
    QUIT = auto()


MOVE_DIRECTIONS: dict[Action, Direction] = {
    Action.MOVE_UP: Direction.UP,
    Action.MOVE_DOWN: Direction.DOWN,
    Action.MOVE_LEFT: Direction.LEFT,
    Action.MOVE_RIGHT: Direction.RIGHT,
}
"""The direction each movement action steers Pac-Man in."""


MOVE_DIRECTIONS_P2: dict[Action, Direction] = {
    Action.MOVE_UP_P2: Direction.UP,
    Action.MOVE_DOWN_P2: Direction.DOWN,
    Action.MOVE_LEFT_P2: Direction.LEFT,
    Action.MOVE_RIGHT_P2: Direction.RIGHT,
}
"""The direction each movement action steers Pac-Man in."""
