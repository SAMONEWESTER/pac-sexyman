"""Abstract base class of the four ghosts."""

from __future__ import annotations

from abc import ABC, abstractmethod
from enum import Enum, auto
from typing import TYPE_CHECKING, Any, ClassVar

from pygame import Surface
from pygame.sprite import AbstractGroup

from ....config import HALF_TILE, tuning
from ....grid import Cell, Direction
from ....resources import ASSETS
from ...components import Edible
from ..living import MOVE_DIRECTIONS, Living
from ..pac_man import PacMan

if TYPE_CHECKING:
    from ....level import Maze

EYE_FRAMES: dict[Direction, tuple[int, bool]] = {
    Direction.NONE: (0, False),
    Direction.DOWN: (1, False),
    Direction.UP: (2, False),
    Direction.RIGHT: (3, False),
    Direction.LEFT: (3, True),
}
"""Eye frame per look direction as ``(column in sheet, mirrored)``.

``NONE`` is used when Pac-Man is right on top of the ghost.
"""


class GhostState(Enum):
    """What a ghost is doing."""

    CHASE = auto()
    """Hunting Pac-Man: touching him costs a life."""
    FRIGHTENED = auto()
    """Blue and edible, fleeing from Pac-Man."""
    EATEN = auto()
    """Only the eyes are left, waiting in the corner to come back."""


def distance_squared(a: Cell, b: Cell) -> int:
    """Squared straight-line distance between two cells."""
    return (a[0] - b[0]) ** 2 + (a[1] - b[1]) ** 2


class Ghost(Living, ABC):
    """A ghost. Subclasses only decide where to hunt (``chase_target``).

    At every crossing the ghost takes the open direction (never straight
    back, unless it is a dead end) with the shortest *walk* to its target.
    While frightened it picks the walk farthest from Pac-Man instead.
    Its eyes always look at Pac-Man.

    Walking distance (not straight-line, as in the original arcade game)
    is used because random mazes have long detours where a straight-line
    ghost can circle forever without reaching its target.

    Class attributes every subclass sets:
        NAME: Sprite name, ``ASSETS.ghosts[NAME]``.
        TUNING: Speeds, from ``config/tuning.py``.

    Args:
        maze: The maze the ghost moves in.
        cell: The corner the ghost starts and respawns in.
        pac_man: Who to hunt (and look at).
        points: Score for eating the ghost while it is frightened.
        *groups: Sprite groups to add the ghost to.
    """

    NAME: ClassVar[str]
    TUNING: ClassVar[tuning.GhostTuning]

    def __init__(
            self,
            maze: Maze,
            cell: Cell,
            pac_men: list[PacMan],
            points: int,
            *groups: AbstractGroup[Any],
            ) -> None:
        self.sprites = ASSETS.ghosts[self.NAME]
        super().__init__(self.sprites.bodies[0], maze, cell,
                         self.TUNING.speed, *groups)
        self.pac_men = pac_men
        self.points = points
        self.state = GhostState.CHASE
        self.timer = 0.0
        self._frames: dict[tuple[bool, int, int, bool], Surface] = {}

    @abstractmethod
    def chase_target(self) -> Cell:
        """The cell this ghost hunts for. Each ghost has its own idea."""

    # State changes.
    # -------------------------------------------------------------------------
    @property
    def is_dangerous(self) -> bool:
        """Whether touching this ghost costs Pac-Man a life."""
        return self.state is GhostState.CHASE

    def frighten(self, seconds: float) -> None:
        """Turn blue, become edible, slow down and turn around.

        Args:
            seconds: How long the ghost stays frightened.
        """
        if self.state is GhostState.EATEN:
            return
        self.state = GhostState.FRIGHTENED
        self.timer = seconds
        self.edible = Edible(self.points)
        self.speed = self.TUNING.frightened_speed
        self.reverse()

    def calm(self) -> None:
        """Back to normal: hunting, dangerous, full speed."""
        self.state = GhostState.CHASE
        self.timer = 0.0
        self.edible = None
        self.speed = self.TUNING.speed

    def get_eaten(self) -> None:
        """Pac-Man ate the ghost: only the eyes wait in the corner."""
        self.state = GhostState.EATEN
        self.timer = tuning.GHOST_RESPAWN_SECONDS
        self.edible = None
        self.respawn()

    # Living template steps.
    # -------------------------------------------------------------------------
    def update(self, dt: float, elapsed: float) -> None:
        """Run the state timers, then move, animate and place.

        Args:
            dt: Seconds since the previous frame.
            elapsed: Seconds since the game started.
        """
        if self.state is not GhostState.CHASE:
            self.timer -= dt
            if self.timer <= 0:
                self.calm()
        super().update(dt, elapsed)

    def move(self, dt: float) -> None:
        """Move, except while eaten (waiting in the corner)."""
        if self.state is not GhostState.EATEN:
            super().move(dt)

    def choose_direction(self) -> Direction:
        """Pick the best open direction at a crossing, see the class doc."""
        # Sort the pac-men.
        self.pac_men.sort(
            key=lambda x: self.maze.distances_from(self.cell)[x.cell])

        options = [
            d for d in MOVE_DIRECTIONS
            if self.can_move(d) and d is not self.direction.opposite]
        if not options:  # Dead end: the only way out is back.
            options = [d for d in MOVE_DIRECTIONS if self.can_move(d)]
        if not options:
            return Direction.NONE

        def next_cell(d: Direction) -> Cell:
            return self.cell[0] + d.dx, self.cell[1] + d.dy

        if self.state is GhostState.FRIGHTENED:
            from_pac_man = self.maze.distances_from(self.pac_men[0].cell)
            return max(
                options, key=lambda d: from_pac_man.get(next_cell(d), 0))
        # Targets may lie outside the maze or inside the 42: snap them.
        target = self.maze.nearest_open_cell(self.chase_target())
        to_target = self.maze.distances_from(target)
        unreachable = self.maze.w * self.maze.h
        return min(
            options, key=lambda d: to_target.get(next_cell(d), unreachable))

    def animate(self, dt: float, elapsed: float) -> None:
        """Wobble the body and point the eyes at Pac-Man.

        Args:
            dt: Seconds since the previous frame (unused).
            elapsed: Seconds since the game started.
        """
        eye_column, mirrored = EYE_FRAMES[self._look_direction()]
        eye_frames = (self.sprites.eyes_mirrored if mirrored
                      else self.sprites.eyes)
        if self.state is GhostState.EATEN:
            self.image = eye_frames[eye_column]
            return

        frightened = self.state is GhostState.FRIGHTENED
        body = int(elapsed * tuning.GHOST_BODY_FPS) % len(self.sprites.bodies)
        key = (frightened, body, eye_column, mirrored)
        if key not in self._frames:
            bodies = (ASSETS.ghost_frightened_bodies if frightened
                      else self.sprites.bodies)
            frame = bodies[body].copy()
            frame.blit(eye_frames[eye_column], (0, 0))
            self._frames[key] = frame
        self.image = self._frames[key]

    def _look_direction(self) -> Direction:
        """The main direction from this ghost towards Pac-Man."""
        offset = self.pac_men[0].pos - self.pos
        if offset.length() < HALF_TILE:
            return Direction.NONE
        if abs(offset.x) > abs(offset.y):
            return Direction.RIGHT if offset.x > 0 else Direction.LEFT
        return Direction.DOWN if offset.y > 0 else Direction.UP
