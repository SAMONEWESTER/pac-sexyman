"""Abstract base class for items that trigger an effect when eaten."""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Protocol

from .inanimate import Inanimate


class PowerUpTarget(Protocol):
    """What a power-up can affect. The game implements these methods."""

    def frighten_ghosts(self, seconds: float) -> None:
        """Make every ghost edible for a while."""


class PowerUp(Inanimate, ABC):
    """An item that does something special when Pac-Man eats it.

    Subclasses decide what that is by implementing ``activate``.
    """

    @abstractmethod
    def activate(self, target: PowerUpTarget) -> None:
        """Apply the power-up's effect. Every subclass must define it.

        Args:
            target: The game objects the effect can change.
        """
