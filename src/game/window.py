"""Creating the game window."""

import pygame
from pygame import Surface
from pygame.image import load
from pygame.display import set_mode, set_caption, set_icon

from ..config import TILE_SIZE, WINDOW_TITLE
from ..errors import LOGGER, DisplayError
from ..resources import asset_path


def create_window(grid_size: tuple[int, int]) -> Surface:
    """Open a window that fits a maze of the given size.

    Args:
        grid_size: Width and height of the maze, in cells.

    Returns:
        The display surface to draw on.

    Raises:
        DisplayError: If the window cannot be opened.
    """
    width, height = grid_size[0] * TILE_SIZE, grid_size[1] * TILE_SIZE
    _set_icon()
    try:
        screen = set_mode(
            (width, height), pygame.SCALED)
    except pygame.error as err:
        raise DisplayError(
            f'cannot open a {width}x{height} game window') from err
    set_caption(WINDOW_TITLE)
    return screen


def _set_icon() -> None:
    """Set the window icon. A missing icon is only a warning."""
    try:
        set_icon(load(asset_path('gfx/icon.png')))
    except (pygame.error, OSError) as err:
        LOGGER.warning(
            "cannot load window icon 'assets/gfx/icon.png'. "
            "Continuing without it.",
            str(err).rstrip('.'))
