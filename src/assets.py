from pygame import Surface, Rect
from pygame.image import load


class Assets:
    def load_all(self):
        self.tileset0 = self._load_sliced('tileset/0')
        self.pac_dot = self._load_quick('obj/pac_dot')
        self.power_pellet = self._load_quick('obj/power_pellet')
        self.fruits = self._load_sliced('obj/fruits', 16)

    @staticmethod
    def _load_quick(path: str) -> Surface:
        return load(f'assets/gfx/{path}.png').convert_alpha()

    def _load_sliced(self, path: str, size: int = 32) -> tuple[Surface, ...]:
        image = self._load_quick(path)
        rect = image.get_rect()
        if rect.w % size or rect.h % size:
            raise ValueError('Image is not cleanly divisible by given size.')

        result = []
        for y in range(rect.h // size):
            for x in range(rect.w // size):
                subrect = Rect(x * size, y * size, size, size)
                result.append(image.subsurface(subrect).copy())
        return tuple(result)


ASSETS = Assets()
