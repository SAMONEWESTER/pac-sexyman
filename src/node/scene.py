from __future__ import annotations

from abc import abstractmethod

from .node import Node


class Scene(Node):
    def __init__(self) -> None:
        super().__init__()

    @abstractmethod
    def enter(self) -> None:
        ...

    @abstractmethod
    def exit(self) -> None:
        ...
