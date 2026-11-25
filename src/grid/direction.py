"""The four directions an entity can move in, plus standing still."""

from enum import Enum


class Direction(Enum):
    """A grid direction with its step and its wall bit in a maze cell.

    Maze cells store walls as bits: 1 north, 2 east, 4 south, 8 west.

    Attributes:
        dx: Step in cells along x.
        dy: Step in cells along y.
        wall: The wall bit blocking this direction, 0 for ``NONE``.
    """

    NONE = (0, 0, 0)
    N = (0, -1, 1)
    E = (1, 0, 2)
    S = (0, 1, 4)
    W = (-1, 0, 8)

    def __init__(self, dx: int, dy: int, wall: int) -> None:
        self.dx = dx
        self.dy = dy
        self.wall = wall

    @property
    def opposite(self) -> 'Direction':
        """The direction pointing the other way."""
        return _OPPOSITES[self]


MOVEMENT_DIRECTIONS: tuple[Direction, ...] = (
    Direction.N,
    Direction.E,
    Direction.S,
    Direction.W
)

_OPPOSITES: dict[Direction, Direction] = {
    Direction.NONE: Direction.NONE,
    Direction.N: Direction.S,
    Direction.S: Direction.N,
    Direction.W: Direction.E,
    Direction.E: Direction.W,
}
