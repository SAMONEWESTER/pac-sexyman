from ....resources import ASSETS

from pygame import Vector2

from ....config.config import CONFIG
from .item import Item
from ..sprite.world_sprite import WorldSprite
from ..float_animation import FloatStyle
from ..entity import Entity
from ..actor.pacman import PacMan


class Dot(Item):
    """Dot that can be eaten by Pacman.

    Parameters
    ----------
    offset: Vector2
        The position of the dot relative to its parent.
    float_style: FloatStyle
        Idle animation to play.
    theme: int
        Theme to use for the dot's appearance.
        Must be a valid index into ``ASSETS.pac_dots``.

    Raises
    ------
    IndexError
        If the given theme is not a valid index into ``ASSETS.pac_dots``.
    """
    def __init__(
            self,
            offset: Vector2,
            float_style: FloatStyle,
            theme: int
            ) -> None:
        super().__init__(offset, float_style)
        self.children[1].add_child(WorldSprite(ASSETS.pac_dots[theme]))

    def on_collision(self, other: Entity) -> None:
        if isinstance(other, PacMan):
            other.award(CONFIG.points_per_dot)
            other.lag = 0.125
            self.kill()
