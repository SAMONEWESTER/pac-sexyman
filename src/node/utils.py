# from functools import wraps
# from typing import Callable, ParamSpec, TypeVar

# from pygame import Surface
# from pygame.sprite import Sprite

# from .entity.camera import Camera

# P = ParamSpec("P")
# R = TypeVar("R")


# def draw_decorator(
#     base_draw: Callable[[Sprite, Surface, Camera | None], bool],
# ) -> Callable[
#     [Callable[P, R]],
#     Callable[P, bool],
# ]:
#     def decorator(func: Callable[P, R]) -> Callable[P, bool]:
#         @wraps(func)
#         def wrapper(*args: P.args, **kwargs: P.kwargs) -> bool:
#             self, surface, camera = args

#             if not base_draw(self, surface, camera) or camera is None:
#                 return False

#             func(*args, **kwargs)

#             for child in self.children:
#                 child.draw(surface, camera)

#             return True

#         return wrapper
#     return decorator
