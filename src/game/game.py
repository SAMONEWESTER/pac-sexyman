"""The main game loop."""

from __future__ import annotations

import pygame
from pygame import Vector2
from pygame.sprite import Group, GroupSingle

from ..config import FPS, Config
from ..entities import Dot, Ghost, IdleStyle, PacMan, PowerPellet
from ..level import (
    Maze,
    generate_dots,
    generate_power_pellets,
    spawn_ghosts,
    spawn_pac_man,
)
from ..resources import ASSETS, FONTS, random_color
from .window import create_window


class Game:
    """Owns the window, the current level and the main loop.

    Also the ``PowerUpTarget`` that power-ups act on.

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

        self.styles: list[IdleStyle] = list(IdleStyle)
        self.maze: GroupSingle[Maze] = GroupSingle()
        self.dots: Group[Dot] = Group()
        self.power_pellets: Group[PowerPellet] = Group()
        self.ghosts: Group[Ghost] = Group()
        self.pac_man: GroupSingle[PacMan] = GroupSingle()
        self.cam = Vector2()

        self.dt = 0.0
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
            self.dt = self.clock.tick(FPS) / 1000
            self.elapsed_time += self.dt

    def frighten_ghosts(self, seconds: float) -> None:
        """Make every ghost edible for a while (``PowerUpTarget``).

        Args:
            seconds: How long the ghosts stay edible.
        """
        for ghost in self.ghosts:
            ghost.frighten(seconds)

    def _new_level(self) -> None:
        """Replace the maze and everything in it with fresh ones."""
        maze = Maze(ASSETS.tileset0, random_color(), self.maze_size)
        style = self.styles[0]
        self.maze.add(maze)
        self.dots = generate_dots(
            maze, style, self.config.points_per_pacgum)
        self.power_pellets = generate_power_pellets(
            maze, style, self.config.points_per_super_pacgum)
        self.ghosts = spawn_ghosts(maze, self.config.points_per_ghost)
        self.pac_man.add(spawn_pac_man(maze))

    def _next_style(self) -> None:
        """Rotate to the next dot animation style."""
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
        """Advance every entity by one frame."""
        frame = (self.dt, self.elapsed_time)
        self.dots.update(*frame)
        self.power_pellets.update(*frame)
        self.ghosts.update(*frame)
        self.pac_man.update(*frame)

    def _draw(self) -> None:
        """Draw the background, sprites and UI, then show the frame."""
        # Draw background.
        self.screen.fill(0)
        self.maze.draw(self.screen)

        # Draw sprite groups, back to front.
        self.dots.draw(self.screen)
        self.power_pellets.draw(self.screen)
        self.ghosts.draw(self.screen)
        self.pac_man.draw(self.screen)

        # Draw UI.

        pygame.display.flip()
