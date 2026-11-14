from __future__ import annotations

from pygame import Surface, Vector2

from .node import Node


class Entity(Node):
    def __init__(self) -> None:
        super().__init__()
        self.position = Vector2(0, 0)

    def update(self, dt: float, elapsed: float) -> None:
        super().update(dt, elapsed)

    def draw(self, surface: Surface) -> None:
        super().draw(surface)
