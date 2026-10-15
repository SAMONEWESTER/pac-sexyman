"""Loading of the game fonts."""

from pygame.font import Font

from .paths import FONT_PATH


class Fonts:
    """Holds every font the game uses, loaded once at startup."""

    regular: Font
    big: Font

    def load_all(self) -> None:
        """Load all fonts. Requires ``pygame.init()`` to have run."""
        self.regular = Font(FONT_PATH, size=24)
        self.big = Font(FONT_PATH, size=48)


FONTS = Fonts()
