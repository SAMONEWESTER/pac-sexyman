from __future__ import annotations

from abc import ABC
from collections.abc import Iterable, Iterator
from typing import TYPE_CHECKING

from pygame import Surface, Vector2

if TYPE_CHECKING:
    from .scene.scene import Scene
    from .entity.camera import Camera


class Node(ABC):
    """Node as part of a scene tree.
    Nodes can have children, and can be updated and drawn.
    """
    def __init__(self) -> None:
        self.parent: Node | None = None
        "Parent node in the scene tree; ``None`` if this is the root node."
        self.owner: Node | None = None
        "Final parent of components; ``None`` if this is not a component."
        self.children: list[Node] = []
        "Child nodes in the scene tree."
        self.active: bool = True
        "Whether the node is active and should be updated and drawn."
        self.position = Vector2(0, 0)
        "Absolute position of the node in the world."
        self.is_ready = False

    def add_child(self, child: Node, owner: Node | None = None) -> Node:
        """Adds a child node to this node.
        If the child already has a parent,
        it is removed from its previous parent.
        Returns the child node that was added."""
        if child.parent is not None:
            child.parent.remove_child(child)

        child.parent = self
        child.owner = owner or self
        self.children.append(child)
        if self.is_ready:
            child.is_ready = True
            child._on_enter_tree()
        return child

    def add_children(
            self,
            children: Iterable[Node],
            owner: Node | None = None
            ) -> list[Node]:
        """Adds multiple child nodes to this node.
        If a child already has a parent,
        it is removed from its previous parent.
        Returns the child nodes that were added as a list."""
        for child in children:
            self.add_child(child)
            child.owner = owner or self
        return list(children)

    def remove_child(self, child: Node) -> None:
        "Removes a child node from this node."
        child._on_exit_tree()
        self.children.remove(child)
        child.parent = None
        child.owner = None

    def kill(self) -> None:
        "Removes this entire node subtree, even if layers deep."
        if self.parent is None:
            return
        self.parent.remove_child(self)

    def update(self, dt: float) -> bool:
        "Returns whether the node is active and should be updated."
        if not self.active:
            return False
        for child in self.children:
            child.update(dt)
        return True

    def draw(self, surface: Surface, camera: Camera | None = None) -> bool:
        "Returns whether the node is active and should be drawn."
        if not self.active:
            return False
        for child in self.children:
            child.draw(surface, camera)
        return True

    def tree_to_string(self, depth: int = 0) -> str:
        result = f"{self}\n"
        for child in self:
            result += f"{"    " * depth} ╰─ {child.tree_to_string(depth + 1)}"
        return result

    def _on_enter_tree(self) -> None:
        for child in self.children:
            child._on_enter_tree()

    def _on_exit_tree(self) -> None:
        for child in self.children:
            child._on_exit_tree()

    @property
    def root(self) -> Scene:
        "Returns the root node of the scene tree."
        if self.parent is None:
            return self
        return self.parent.root

    def __len__(self) -> int:
        return len(self.children)

    def __getitem__(self, index: int) -> Node:
        return self.children[index]

    def __delitem__(self, index: int) -> None:
        del self.children[index]

    def __iter__(self) -> Iterator[Node]:
        return iter(self.children)

    def __contains__(self, item: Node) -> bool:
        return item in self.children

    def __str__(self):
        return f"{self.__class__.__name__}_{str(id(self))[-4:]}"
