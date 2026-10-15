"""The main game loop."""

from __future__ import annotations

import pygame
from pygame import Vector2
from pygame.sprite import Group, GroupSingle

from ..config import FPS, Config
from ..entities import DOT_STYLES, PacDot
from ..level import Maze, generate_dots
from ..resources import ASSETS, FONTS, random_color
from .window import create_window


class Game:
    """Owns the window, the current level and the main loop.

    Args:
        config: The validated game settings.
    """

    def __init__(self, config: Config) -> None:
        pygame.init()
        self.config = config
        self.maze_size = config.levels[0].size
        self.screen = create_window(self.maze_size)
        self.clock = pygame.time.Clock()

        ASSETS.load_all()
        FONTS.load_all()

        self.styles: list[str] = list(DOT_STYLES)
        self.maze: GroupSingle[Maze] = GroupSingle()
        self.pacdots: Group[PacDot] = Group()
        self.cam = Vector2()

        self.elapsed_time = 0.0
        self.running = False
        self._new_level()

    def run(self) -> None:
        """Run the main loop until the player quits."""
        self.running = True
        while self.running:
            self._handle_events()
            self._update()
            self._draw()
            self.elapsed_time += self.clock.tick(FPS) / 1000

    def _new_level(self) -> None:
        """Replace the maze and its dots with freshly generated ones."""
        self.maze.add(Maze(ASSETS.tileset0, random_color(), self.maze_size))
        self.pacdots = generate_dots(self.maze.sprite, self.styles[0])

    def _next_style(self) -> None:
        """Rotate to the next pac-dot animation style."""
        self.styles.append(self.styles.pop(0))

    def _handle_events(self) -> None:
        """Process window, keyboard and mouse events."""
        for event in pygame.event.get():
            keys = pygame.key.get_pressed()
            if event.type == pygame.QUIT or keys[pygame.K_ESCAPE]:
                self.running = False
            if event.type == pygame.MOUSEBUTTONDOWN:
                if pygame.mouse.get_pressed()[0]:
                    self._next_style()
                    self._new_level()

    def _update(self) -> None:
        """Advance all animations by one frame."""
        self.pacdots.update(self.elapsed_time)

    def _draw(self) -> None:
        """Draw the background, sprites and UI, then show the frame."""
        # Draw background.
        self.screen.fill(0)
        self.maze.draw(self.screen)

        # Draw sprite groups.
        self.pacdots.draw(self.screen)

        # Draw UI.

        pygame.display.flip()
