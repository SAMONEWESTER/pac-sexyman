"""Creating the game window."""

import pygame
from pygame import Surface

from ..config import TILE_SIZE, WINDOW_TITLE
from ..errors import LOGGER, DisplayError
from ..resources import ICON_PATH


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
        screen = pygame.display.set_mode((width, height), pygame.FULLSCREEN | pygame.SCALED)
    except pygame.error as err:
        raise DisplayError(
            f'cannot open a {width}x{height} game window') from err
    pygame.display.set_caption(WINDOW_TITLE)
    return screen


def _set_icon() -> None:
    """Set the window icon. A missing icon is only a warning."""
    try:
        pygame.display.set_icon(pygame.image.load(ICON_PATH))
    except (pygame.error, OSError) as err:
        LOGGER.warning("cannot load window icon '%s' (%s). "
                       'Continuing without it.', ICON_PATH.as_posix(),
                       str(err).rstrip('.'))
