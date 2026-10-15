"""Fixed values shared across the whole game.

Values that a player may want to change belong in the config file instead.
"""

TILE_SIZE: int = 32
"""Width and height of one maze cell, in pixels."""

HALF_TILE: int = TILE_SIZE // 2
"""Offset from a cell's corner to its center, in pixels."""

FPS: int = 144
"""Frame rate the game loop is capped at."""

WINDOW_TITLE: str = 'pac-male'
"""Text shown in the window title bar."""
