"""Loading and slicing of all game graphics."""

from pygame import Rect, Surface
from pygame.image import load

from ..config import TILE_SIZE
from .paths import GFX_DIR

FRUIT_SIZE: int = 16
"""Width and height of one fruit in the fruit sheet, in pixels."""


class Assets:
    """Holds every image the game uses, loaded once at startup."""

    tileset0: tuple[Surface, ...]
    pac_dot: Surface
    power_pellet: Surface
    fruits: tuple[Surface, ...]

    def load_all(self) -> None:
        """Load all images. Requires an active display."""
        self.tileset0 = self._load_sliced('tileset/0')
        self.pac_dot = self._load_quick('obj/pac_dot')
        self.power_pellet = self._load_quick('obj/power_pellet')
        self.fruits = self._load_sliced('obj/fruits', FRUIT_SIZE)

    @staticmethod
    def _load_quick(path: str) -> Surface:
        """Load one PNG from the graphics folder, keeping transparency.

        Args:
            path: Image path inside ``assets/gfx``, without extension.
        """
        return load(GFX_DIR / f'{path}.png').convert_alpha()

    def _load_sliced(
            self, path: str, size: int = TILE_SIZE) -> tuple[Surface, ...]:
        """Load a sprite sheet and cut it into square pieces.

        Args:
            path: Image path inside ``assets/gfx``, without extension.
            size: Width and height of one piece, in pixels.

        Returns:
            The pieces, left to right and top to bottom.

        Raises:
            ValueError: If the image does not divide evenly by ``size``.
        """
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
