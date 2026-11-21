from __future__ import annotations

from pygame import Vector2

from ..node import Node
from ...utils.get_time import get_time


class Entity(Node):
    """Object in the game world with an offset,
    allowing it to transform relative to the parent."""
    def __init__(self) -> None:
        super().__init__()
        self.offset: Vector2 = Vector2(0, 0)
        "Offset of the entity relative to its parent."
        self.start_time = get_time()
        "Time when the entity was created, in seconds since the game started."

    def update(self, dt: float) -> bool:
        "Returns whether the entity is active and should be updated."
        if not self.active:
            return False
        self.position.update(self.parent.position + self.offset)
        return super().update(dt)

    def on_collision(self, other: Entity) -> None:
        """Called when this entity collides with another entity.

        Parameters
        ----------
        other: Entity
            The other entity that this entity collided with.
        """
        pass
