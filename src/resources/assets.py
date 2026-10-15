"""Loading and slicing of all game graphics."""

from pygame import Rect, Surface
from pygame import error as PygameError
from pygame.image import load

from ..config import TILE_SIZE
from ..errors import AssetError
from .paths import GFX_DIR

FRUIT_SIZE: int = 16
"""Width and height of one fruit in the fruit sheet, in pixels."""

TILE_VARIANTS: int = 16
"""Tiles a tileset needs: one for every combination of 4 walls."""


class Assets:
    """Holds every image the game uses, loaded once at startup."""

    tileset0: tuple[Surface, ...]
    pac_dot: Surface
    power_pellet: Surface
    fruits: tuple[Surface, ...]

    def load_all(self) -> None:
        """Load all images. Requires an active display.

        Raises:
            AssetError: If an image is missing or unusable.
        """
        self.tileset0 = self._load_sliced('tileset/0')
        if len(self.tileset0) < TILE_VARIANTS:
            raise AssetError(
                f"tileset 'tileset/0' has {len(self.tileset0)} tiles, "
                f'needs at least {TILE_VARIANTS}')
        self.pac_dot = self._load_quick('obj/pac_dot')
        self.power_pellet = self._load_quick('obj/power_pellet')
        self.fruits = self._load_sliced('obj/fruits', FRUIT_SIZE)

    @staticmethod
    def _load_quick(path: str) -> Surface:
        """Load one PNG from the graphics folder, keeping transparency.

        Args:
            path: Image path inside ``assets/gfx``, without extension.

        Raises:
            AssetError: If the file is missing or not a readable image.
        """
        file = GFX_DIR / f'{path}.png'
        try:
            return load(file).convert_alpha()
        except (PygameError, OSError) as err:
            raise AssetError(
                f"cannot load image '{file.as_posix()}'") from err

    def _load_sliced(
            self, path: str, size: int = TILE_SIZE) -> tuple[Surface, ...]:
        """Load a sprite sheet and cut it into square pieces.

        Args:
            path: Image path inside ``assets/gfx``, without extension.
            size: Width and height of one piece, in pixels.

        Returns:
            The pieces, left to right and top to bottom.

        Raises:
            AssetError: If the image cannot be loaded or does not divide
                evenly into ``size`` by ``size`` pieces.
        """
        image = self._load_quick(path)
        rect = image.get_rect()
        if rect.w % size or rect.h % size:
            raise AssetError(
                f"image '{path}' is {rect.w}x{rect.h} pixels, which does "
                f'not divide into {size}x{size} pieces')

        result = []
        for y in range(rect.h // size):
            for x in range(rect.w // size):
                subrect = Rect(x * size, y * size, size, size)
                result.append(image.subsurface(subrect).copy())
        return tuple(result)


ASSETS = Assets()
