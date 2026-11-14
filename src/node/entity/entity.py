from __future__ import annotations

from pygame import Vector2

from ..node import Node


class Entity(Node):
    def __init__(self, offset: Vector2) -> None:
        super().__init__()
        self.offset = offset

    def update(self, dt: float, t: float) -> bool:
        "Returns whether the entity is active and should be updated."
        if not super().update(dt, t):
            return False

        self.position = (
            self.parent.position.x + self.offset.x,
            self.parent.position.y + self.offset.y
        )

        return True
