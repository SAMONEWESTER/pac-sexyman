"""Loading of the game fonts."""

from pygame import error as PygameError
from pygame.font import Font

from ..errors import AssetError
from .paths import FONT_PATH
from .assets import asset_path


class Fonts:
    """Holds every font the game uses, loaded once at startup."""

    regular: Font
    big: Font

    def load_all(self) -> None:
        """Load all fonts. Requires ``pygame.init()`` to have run.

        Raises:
            AssetError: If the font file is missing or unusable.
        """
        try:
            self.regular = Font(asset_path('font/lovely-pixels.otf'), size=24)
            self.big = Font(asset_path('font/lovely-pixels.otf'), size=48)
        except (PygameError, OSError) as err:
            raise AssetError(
                f"cannot load font '{FONT_PATH.as_posix()}'") from err


FONTS = Fonts()
