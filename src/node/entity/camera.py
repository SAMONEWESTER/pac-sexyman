from pygame import Vector2
from pygame.display import get_surface

from .entity import Entity


class Camera(Entity):
    def __init__(
            self,
            offset: Vector2,
            maze_size: tuple[int, int],
            bottom_padding: int = 0,
            ) -> None:
        super().__init__(offset)
        maze_w, maze_h = maze_size
        screen_w, screen_h = get_surface().get_size()

        self.scale = min(screen_w / maze_w,
                         (screen_h - bottom_padding) / maze_h)
        self.offset_x = (screen_w - maze_w * self.scale) / 2
        self.offset_y = \
            (screen_h - maze_h * self.scale) / 2 - bottom_padding / 2

    def point(self, pos: tuple[float, float]) -> tuple[int, int]:
        return (round(self.offset_x + pos[0] * self.scale),
                round(self.offset_y + pos[1] * self.scale))

    def size(self, size: tuple[int, int]) -> tuple[int, int]:
        return (max(1, round(size[0] * self.scale)),
                max(1, round(size[1] * self.scale)))
