from pygame import Vector2

from ..entity import Entity
from ..collider import CollisionLayer, Collider
from ..float_animation import FloatAnimation, FloatStyle


class Item(Entity):
    """Item that can be eaten by Pacman.
    Starts with a collider and a float animation as children.

    Parameters
    ----------
    offset: Vector2
        The position of the item relative to its parent.
    float_style: FloatStyle
        Idle animation to play.
    """
    def __init__(self, offset: Vector2, float_style: FloatStyle) -> None:
        super().__init__()
        self.offset = offset

        col = Collider(Vector2(4, 4))
        col.owner = self
        col.layer = CollisionLayer.ITEM
        col.mask = CollisionLayer.PACMAN
        self.add_child(col)

        self.add_child(
            FloatAnimation(float_style, (offset.x + offset.y) / 100, 1.0))
