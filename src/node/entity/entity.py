from __future__ import annotations

from pygame import Vector2

from ..node import Node
from ..utils import get_time


class Entity(Node):
    def __init__(
            self,
            offset: Vector2,
            ) -> None:
        super().__init__()
        self.offset = offset
        "Offset of the entity relative to its parent."
        self.start_time = get_time()
        "Time when the entity was created, in seconds since the game started."

    def update(self, dt: float) -> bool:
        "Returns whether the entity is active and should be updated."
        if not super().update(dt):
            return False
        self.position = self.parent.position + self.offset
        return True
