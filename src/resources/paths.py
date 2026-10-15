"""Locations of every file the game loads, relative to the project root."""

from pathlib import Path

ASSETS_DIR: Path = Path('assets')
GFX_DIR: Path = ASSETS_DIR / 'gfx'
FONT_DIR: Path = ASSETS_DIR / 'font'

FONT_PATH: Path = FONT_DIR / 'lovely-pixels.otf'
ICON_PATH: Path = GFX_DIR / 'obj' / 'power_pellet.png'
