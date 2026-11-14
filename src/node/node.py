from __future__ import annotations

from abc import ABC

from pygame import Surface


class Node(ABC):
    def __init__(self) -> None:
        self.parent: Node | None = None
        self.children: list[Node] = []
        self.active: bool = True

    def add_child(self, child: Node) -> None:
        child.parent = self
        self.children.append(child)

    def remove_child(self, child: Node) -> None:
        self.children.remove(child)
        child.parent = None

    def update(self, dt: float, elapsed: float) -> bool:
        "Returns whether the node is active and should be updated."
        if not self.active:
            return False
        for child in self.children:
            child.update(dt, elapsed)
        return True

    def draw(self, surface: Surface) -> bool:
        "Returns whether the node is active and should be drawn."
        if not self.active:
            return False
        for child in self.children:
            child.draw(surface)
        return True
