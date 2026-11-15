from __future__ import annotations

from abc import abstractmethod

from ..node import Node
from ..utils import get_time


class Scene(Node):
    def __init__(self) -> None:
        super().__init__()
        self.dt = 0.0
        "Time since the last clock tick."
        self.start_time = get_time()
        "Time when the scene was created, in seconds since the game started."
        self.next_scene: Scene | None = None
        "The scene to switch to after this one ends; ``None`` while running."

    def update(self, dt: float) -> bool:
        """Update the scene and its children.

        Args:
            dt: Seconds since the previous frame.
            elapsed: Seconds since the game started.
        """
        if not super().update(dt):
            return False
        self.dt = dt
        return True

    @abstractmethod
    def handle_key(self, key: int) -> None:
        """Handle a key press event.

        Args:
            key: The key code of the pressed key.
        """
        ...

    @abstractmethod
    def enter(self) -> None:
        """Called when the scene is entered,
        after it is added to the scene tree."""
        ...

    @abstractmethod
    def exit(self) -> None:
        """Called when the scene is exited,
        before it is removed from the scene tree."""
        ...
