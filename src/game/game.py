"""The main game loop."""

from __future__ import annotations

import pygame
from pygame import Vector2
from pygame.event import Event
from pygame.sprite import Group, GroupSingle

from ..config import FPS, Config
from ..controls import P1_DIRECTIONS, P2_DIRECTIONS, Action, Controls
from ..entities import Dot, Ghost, IdleStyle, PacMan, PowerPellet
from ..errors import LOGGER
from ..level import (
    Maze,
    generate_dots,
    generate_power_pellets,
    spawn_ghosts,
)
from ..resources import ASSETS, FONTS
from .collisions import eat, points, touched_ghosts
from .hud import draw_hud
from .session import Session
from .player import Player
from .window import create_window

MAX_DT: float = 0.05
"""Longest frame step in seconds, so a hiccup never skips through walls."""


class Game:
    """Owns the window, the current level and the main loop.

    Also the ``PowerUpTarget`` that power-ups act on.

    Args:
        config: The validated game settings.
        controls: Key bindings; the defaults if omitted.
    """

    def __init__(
            self,
            config: Config,
            controls: Controls | None = None,
            ) -> None:
        pygame.init()
        self.config = config
        self.controls = controls or Controls()
        self.maze_size = config.levels[0].size
        self.screen = create_window(self.maze_size)
        self.clock = pygame.time.Clock()

        ASSETS.load_all()
        FONTS.load_all()

        self.players = (Player(), Player())
        self.players[0].start(config.lives)
        self.players[1].start(config.lives)

        self.session = Session(lives=config.lives)
        self.styles: list[IdleStyle] = list(IdleStyle)
        self.maze: GroupSingle[Maze] = GroupSingle()
        self.dots: Group[Dot] = Group()
        self.power_pellets: Group[PowerPellet] = Group()
        self.ghosts: Group[Ghost] = Group()
        self.pac_men: Group[PacMan] = Group()
        self.cam = Vector2()

        self.dt = 0.0
        self.elapsed_time = 0.0
        self.running = False
        self._next_level(0)

    def run(self) -> None:
        """Run the main loop until the player quits."""
        self.running = True
        while self.running:
            self._handle_events()
            self._update()
            self._draw()
            self.dt = min(self.clock.tick(FPS) / 1000, MAX_DT)
            self.elapsed_time += self.dt

    def frighten_ghosts(self, seconds: float) -> None:
        """Make every ghost edible for a while (``PowerUpTarget``).

        Args:
            seconds: How long the ghosts stay edible.
        """
        for ghost in self.ghosts:
            ghost.frighten(seconds)

    # Level setup.
    # -------------------------------------------------------------------------
    def _next_level(self, index: int | None = None) -> None:
        """Replace the maze and everything in it with fresh ones."""
        if index is not None:
            self.level = index
        else:
            self.level += 1
        theme = self.level % len(ASSETS.tilesets)
        style = self.styles[self.level % 3]
        maze = Maze(self.maze_size, theme)
        self.maze.add(maze)
        self.dots = generate_dots(
            maze, style, self.config.points_per_pacgum)
        self.power_pellets = generate_power_pellets(
            maze, style, self.config.points_per_super_pacgum)
        self.pac_men.empty()
        if not self.players[0].is_over:
            self.pac_men.add(PacMan(maze, 0, self.elapsed_time))
        if not self.players[1].is_over:
            self.pac_men.add(PacMan(maze, 1, self.elapsed_time))
        self.ghosts = spawn_ghosts(
            maze, self.pac_men, self.config.points_per_ghost)

    def _player_start(self, index: int) -> None:
        self.players[index].start(self.config.lives)
        self.pac_men.add(PacMan(self.maze.sprite, index, self.elapsed_time))

    # Input.
    # -------------------------------------------------------------------------
    def _handle_events(self) -> None:
        """Process window, keyboard and mouse events."""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.KEYDOWN:
                self._handle_key(event)
            elif event.type == pygame.MOUSEBUTTONDOWN:
                # Debug: left click generates a new maze.
                if pygame.mouse.get_pressed()[0]:
                    self._next_level()

    def _handle_key(self, event: Event) -> None:
        """Turn a key press into an action, through the key bindings."""
        action = self.controls.action_for(event.key)
        if action in P1_DIRECTIONS:
            self.pac_men.sprites()[0].steer(P1_DIRECTIONS[action])
        elif len(self.pac_men.sprites()) > 1 and action in P2_DIRECTIONS:
            self.pac_men.sprites()[1].steer(P2_DIRECTIONS[action])
        elif action is Action.P1_CONFIRM and self.players[0].is_over:
            self._player_start(0)
        elif action is Action.P2_CONFIRM and self.players[1].is_over:
            self._player_start(1)
        elif action is Action.QUIT:
            self.running = False

    # Frame update.
    # -------------------------------------------------------------------------
    def _update(self) -> None:
        """Advance every entity by one frame, then apply the rules."""
        frame = (self.dt, self.elapsed_time)
        self.dots.update(*frame)
        self.power_pellets.update(*frame)
        self.pac_men.update(*frame)
        self.ghosts.update(*frame)
        self._apply_rules()

    def _apply_rules(self) -> None:
        """Eating, scoring, losing lives and clearing the level."""
        for i, pac_man in enumerate(self.pac_men.sprites()):
            for dot in eat(pac_man, self.dots):
                self.session.score += points(dot)
                pac_man.lag = 0.1
            for pellet in eat(pac_man, self.power_pellets):
                self.session.score += points(pellet)
                pellet.activate(self)
                pac_man.lag = 0.1

            for ghost in touched_ghosts(pac_man, self.ghosts):
                if ghost.is_edible:
                    self.session.score += points(ghost)
                    ghost.get_eaten()
                    pac_man.lag = 0.1
                elif ghost.is_dangerous \
                        and not pac_man.is_invincible(self.elapsed_time):
                    self.players[i].lives -= 1
                    if not self.players[i].is_over:
                        pac_man.respawn(self.elapsed_time)
                    else:
                        pac_man.kill()
                        if not self.pac_men:
                            self._lose()
                    ghost.lag = 0.25
                    return

        if not self.dots:
            LOGGER.info('level %d cleared, score %d',
                        self.level, self.session.score)
            self._next_level()

    def _lose(self) -> None:
        """Lose the game."""
        LOGGER.info('game over, score %d', self.session.score)
        self.players[0].start(self.config.lives)
        self.players[1].start(self.config.lives)
        self.session = Session(lives=self.config.lives)
        self._next_level(0)

    # Drawing.
    # -------------------------------------------------------------------------
    def _draw(self) -> None:
        """Draw the background, sprites and UI, then show the frame."""
        # Draw background.
        self.screen.fill(0)
        self.maze.draw(self.screen)

        # Draw sprite groups, back to front.
        self.dots.draw(self.screen)
        self.power_pellets.draw(self.screen)
        self.pac_men.draw(self.screen)
        self.ghosts.draw(self.screen)

        # Draw UI.
        draw_hud(self.screen, self.session)

        pygame.display.flip()
