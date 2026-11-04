"""Creating the game window."""

import pygame
from pygame import Surface
from pygame.image import load
from pygame.display import set_mode, set_caption, set_icon, get_desktop_sizes

from ..errors import DisplayError
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
    set_icon(load(asset_path('gfx/icon.png')))
    w, h = get_desktop_sizes()[0]
    try:
        screen = set_mode((w, h), pygame.SCALED | pygame.FULLSCREEN)
    except pygame.error as err:
        raise DisplayError(
            f'cannot open a {w}x{h} game window') from err
    set_caption('Pac-Man: Rearrangement')
    return screen
