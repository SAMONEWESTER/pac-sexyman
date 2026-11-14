from __future__ import annotations

from abc import abstractmethod

from ..node import Node


class Scene(Node):
    def __init__(self, start_time: float) -> None:
        super().__init__()
        self.start_time = start_time
        "Time when the scene was created, in seconds since the game started."
        self.dt = 0.0
        "Time since the last clock tick."
        self.t = 0.0
        "Time elapsed since beginning of the game."
        self.next_scene: Scene | None = None
        "The scene to switch to after this one ends; ``None`` while running."

    def update(self, dt: float, t: float) -> bool:
        """Update the scene and its children.

        Args:
            dt: Seconds since the previous frame.
            elapsed: Seconds since the game started.
        """
        if not super().update(dt, t):
            return False

        self.dt = dt
        self.t = t

        for child in self.children:
            child.update(dt, t)
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
