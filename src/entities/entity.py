"""The abstract base class of everything that lives in a level."""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any

from pygame import Surface, Vector2
from pygame.sprite import AbstractGroup, Sprite

from .components import Edible


class Entity(Sprite, ABC):
    """Base class for every object in a level: Pac-Man, ghosts, dots, ...

    Being a pygame ``Sprite`` lets entities live in sprite groups, which
    update and draw them all at once.

    Every entity has an ``edible`` slot (composition). It holds an
    ``Edible`` while Pac-Man may eat the entity, and ``None`` otherwise.

    Args:
        image: What the entity looks like.
        center: Pixel position of the entity's center.
        *groups: Sprite groups to add the entity to.
    """

    def __init__(
            self,
            image: Surface,
            center: Vector2,
            *groups: AbstractGroup[Any],
            ) -> None:
        super().__init__(*groups)
        self.image = image
        self.rect = image.get_rect(center=center)
        self.edible: Edible | None = None

    @property
    def is_edible(self) -> bool:
        """Whether Pac-Man can eat this entity right now."""
        return self.edible is not None

    @abstractmethod
    def update(self, dt: float, elapsed: float) -> None:
        """Advance the entity by one frame. Every subclass must define it.

        Args:
            dt: Seconds since the previous frame.
            elapsed: Seconds since the game started.
        """
