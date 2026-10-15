"""Creating the game window."""

import pygame
from pygame import Surface

from ..config import TILE_SIZE, WINDOW_TITLE
from ..resources import ICON_PATH


def create_window(grid_size: tuple[int, int]) -> Surface:
    """Open a window that fits a maze of the given size.

    Args:
        grid_size: Width and height of the maze, in cells.

    Returns:
        The display surface to draw on.
    """
    width, height = grid_size[0] * TILE_SIZE, grid_size[1] * TILE_SIZE
    pygame.display.set_icon(pygame.image.load(ICON_PATH))
    screen = pygame.display.set_mode((width, height), pygame.SCALED)
    pygame.display.set_caption(WINDOW_TITLE)
    return screen
