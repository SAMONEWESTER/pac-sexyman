from __future__ import annotations

from abc import ABC
from typing import TYPE_CHECKING

from pygame import Surface, Vector2

if TYPE_CHECKING:
    from .entity.camera import Camera


class Node(ABC):
    def __init__(self) -> None:
        self.parent: Node | None = None
        "The parent node in the scene tree; ``None`` if this is the root node."
        self.children: list[Node] = []
        "The child nodes in the scene tree."
        self.active: bool = True
        "Whether the node is active and should be updated and drawn."
        self.position = Vector2(0, 0)
        "Absolute position of the node in the world."
        self.offset = Vector2(0, 0)
        "Offset of the node relative to its parent."

    def add_child(self, child: Node) -> None:
        child.parent = self
        self.children.append(child)

    def remove_child(self, child: Node) -> None:
        self.children.remove(child)
        child.parent = None

    def update(self, dt: float, t: float) -> bool:
        "Returns whether the node is active and should be updated."
        if not self.active:
            return False
        for child in self.children:
            child.update(dt, t)
        return True

    def draw(self, surface: Surface, camera: Camera | None = None) -> bool:
        "Returns whether the node is active and should be drawn."
        if not self.active:
            return False
        for child in self.children:
            child.draw(surface, camera)
        return True
