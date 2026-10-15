"""Images, fonts, colors and the file paths they are loaded from.

Call ``ASSETS.load_all()`` and ``FONTS.load_all()`` once, after the
display has been created, before using any of their attributes.
"""

from .assets import ASSETS, Assets
from .colors import random_color
from .fonts import FONTS, Fonts
from .paths import ASSETS_DIR, FONT_DIR, FONT_PATH, GFX_DIR, ICON_PATH

__all__ = [
    'ASSETS',
    'ASSETS_DIR',
    'Assets',
    'FONTS',
    'FONT_DIR',
    'FONT_PATH',
    'Fonts',
    'GFX_DIR',
    'ICON_PATH',
    'random_color',
]
