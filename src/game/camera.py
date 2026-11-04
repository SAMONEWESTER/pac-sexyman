from pygame import Surface


class Camera:
    def __init__(
            self,
            screen: Surface,
            maze_size: tuple[int, int],
            bottom_padding: int = 0
            ) -> None:
        maze_w, maze_h = maze_size
        screen_w, screen_h = screen.get_size()

        self.scale = min(
            screen_w / maze_w,
            (screen_h - bottom_padding) / maze_h)
        self.offset_x = (screen_w - maze_w * self.scale) / 2
        self.offset_y = (screen_h - maze_h * self.scale) / 2 \
            - bottom_padding / 2

    def point(self, pos: tuple[float, float]) -> tuple[int, int]:
        return (round(self.offset_x + pos[0] * self.scale),
                round(self.offset_y + pos[1] * self.scale))

    def size(self, size: tuple[int, int]) -> tuple[int, int]:
        return (max(1, round(size[0] * self.scale)),
                max(1, round(size[1] * self.scale)))
