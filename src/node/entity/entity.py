from __future__ import annotations

from pygame import Vector2

from ..node import Node


class Entity(Node):
    def __init__(self, position: Vector2) -> None:
        super().__init__()
        self.position = position
