from ....resources import ASSETS

from pygame import Vector2

from ....game.events import EatFruitEvent
from ....config.config import CONFIG
from .item import Item
from ..sprite.world_sprite import WorldSprite
from ..float_animation import FloatStyle
from ..entity import Entity
from ..actor.pacman import PacMan


class Fruit(Item):
    """Fruit that can be eaten by Pacman.

    Parameters
    ----------
    offset: Vector2
        The position of the fruit relative to its parent.
    float_style: FloatStyle
        Idle animation to play.
    theme: int
        Theme to use for the fruit's appearance.
        Must be a valid index into ``ASSETS.fruits``.

    Raises
    ------
    IndexError
        If the given theme is not a valid index into ``ASSETS.fruits``.
    """
    def __init__(
            self,
            offset: Vector2,
            float_style: FloatStyle,
            theme: int
            ) -> None:
        super().__init__(offset, float_style)
        self.children[1].add_child(WorldSprite(ASSETS.fruits[theme]))

    def on_collision(self, other: Entity) -> None:
        if isinstance(other, PacMan):
            self.root.game_events.append(EatFruitEvent(
                player_index=other.player.index,))
            other.lag = 0.125
            self.kill()
