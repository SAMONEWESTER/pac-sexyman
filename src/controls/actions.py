"""Everything the player can do with a key."""

from enum import Enum, auto

from ..grid import Direction


class Action(Enum):
    """A player action, independent of which key triggers it."""

    P1_UP = auto()
    P1_DOWN = auto()
    P1_LEFT = auto()
    P1_RIGHT = auto()
    P1_CONFIRM = auto()
    P2_UP = auto()
    P2_DOWN = auto()
    P2_LEFT = auto()
    P2_RIGHT = auto()
    P2_CONFIRM = auto()
    QUIT = auto()


P1_DIRECTIONS: dict[Action, Direction] = {
    Action.P1_UP: Direction.UP,
    Action.P1_DOWN: Direction.DOWN,
    Action.P1_LEFT: Direction.LEFT,
    Action.P1_RIGHT: Direction.RIGHT,
}
"""The direction each movement action steers Pac-Man in."""


P2_DIRECTIONS: dict[Action, Direction] = {
    Action.P2_UP: Direction.UP,
    Action.P2_DOWN: Direction.DOWN,
    Action.P2_LEFT: Direction.LEFT,
    Action.P2_RIGHT: Direction.RIGHT,
}
"""The direction each movement action steers Ms. Pac-Man in."""
