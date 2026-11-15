from __future__ import annotations

from functools import wraps
from typing import Callable, TYPE_CHECKING

from pygame import Surface

from .node import Node

if TYPE_CHECKING:
    from .entity.camera import Camera


def update_decorator(
        base_update: Callable[[Node, float, float], bool],
        ):
    def decorator(
            func: Callable[[Node, float, float], None],
            ) -> Callable[[Node, float, float], bool]:
        @wraps(func)
        def wrapper(self: Node, dt: float, t: float) -> bool:
            if not base_update(self, dt, t):
                return False

            func(self, dt, t)

            for child in self.children:
                child.update(dt, t)
            return True

        return wrapper
    return decorator


def draw_decorator(
        base_draw: Callable[[Node, Surface, Camera | None], bool],
        ):
    def decorator(
            func: Callable[[Node, Surface, Camera | None], None],
            ) -> Callable[[Node, Surface, Camera | None], bool]:
        @wraps(func)
        def wrapper(
                self: Node,
                surface: Surface,
                camera: Camera | None = None,
                ) -> bool:
            if not base_draw(self, surface, camera) or camera is None:
                return False

            func(self, surface, camera)

            for child in self.children:
                child.draw(surface, camera)
            return True

        return wrapper
    return decorator
