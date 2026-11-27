from __future__ import annotations
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from ...game import Game

from abc import abstractmethod

from pygame import Surface

from ...game.collision_manager import CollisionManager
from ...game.events import GameEvent
from ..node import Node
from ...utils.get_time import get_time


class Scene(Node):
    def __init__(self, game: Game) -> None:
        super().__init__()
        self.game = game
        "Game manager that owns this scene."

        self.start_time = get_time()
        "Time when the scene was created, in seconds since the game started."
        self.next_scene: Scene | None = None
        "The scene to switch to after this one ends; ``None`` while running."
        self.collision_manager = CollisionManager()
        "Collision manager for this scene."
        self.game_events: list[GameEvent] = []
        "Event queue for all game events."

    @abstractmethod
    def handle_key(self, key: int) -> None:
        """Handle a key press event.

        Args:
            key: The key code of the pressed key.
        """
        ...
