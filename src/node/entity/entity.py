from __future__ import annotations

from pygame import Vector2

from ..node import Node
from ..utils import update_decorator


class Entity(Node):
    def __init__(self, offset: Vector2) -> None:
        super().__init__()
        self.offset = offset

    @update_decorator(Node.update)
    def update(self, dt: float, t: float) -> bool:
        "Returns whether the entity is active and should be updated."
        self.position = self.parent.position + self.offset
