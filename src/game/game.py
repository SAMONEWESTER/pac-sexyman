"""The main game loop."""

from __future__ import annotations

import pygame
from pygame import Vector2
from pygame.event import Event
from pygame.sprite import Group, GroupSingle

from ..config import FPS, Config
from ..controls import MOVE_DIRECTIONS, Action, Controls
from ..entities import Dot, Ghost, IdleStyle, PacMan, PowerPellet
from ..errors import LOGGER
from ..level import (
    Maze,
    generate_dots,
    generate_power_pellets,
    spawn_ghosts,
    spawn_pac_man,
)
from ..resources import ASSETS, FONTS, random_color
from .collisions import eat, points, touched_ghosts
from .hud import draw_hud
from .session import Session
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

    def __init__(self, config: Config, controls: Controls | None = None
                 ) -> None:
        pygame.init()
        self.config = config
        self.controls = controls or Controls()
        self.maze_size = config.levels[0].size
        self.screen = create_window(self.maze_size)
        self.clock = pygame.time.Clock()

        ASSETS.load_all()
        FONTS.load_all()

        self.session = Session(lives=config.lives)
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
    def _new_level(self) -> None:
        """Replace the maze and everything in it with fresh ones."""
        maze = Maze(ASSETS.tileset0, random_color(), self.maze_size)
        style = self.styles[0]
        self.maze.add(maze)
        self.dots = generate_dots(
            maze, style, self.config.points_per_pacgum)
        self.power_pellets = generate_power_pellets(
            maze, style, self.config.points_per_super_pacgum)
        pac_man = spawn_pac_man(maze)
        self.pac_man.add(pac_man)
        self.ghosts = spawn_ghosts(
            maze, pac_man, self.config.points_per_ghost)

    def _next_style(self) -> None:
        """Rotate to the next dot animation style."""
        self.styles.append(self.styles.pop(0))

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
                    self._next_style()
                    self._new_level()

    def _handle_key(self, event: Event) -> None:
        """Turn a key press into an action, through the key bindings."""
        action = self.controls.action_for(event.key)
        if action is Action.QUIT:
            self.running = False
        elif action in MOVE_DIRECTIONS:
            self.pac_man.sprite.steer(MOVE_DIRECTIONS[action])

    # Frame update.
    # -------------------------------------------------------------------------
    def _update(self) -> None:
        """Advance every entity by one frame, then apply the rules."""
        frame = (self.dt, self.elapsed_time)
        self.dots.update(*frame)
        self.power_pellets.update(*frame)
        self.pac_man.update(*frame)
        self.ghosts.update(*frame)
        self._apply_rules()

    def _apply_rules(self) -> None:
        """Eating, scoring, losing lives and clearing the level."""
        pac_man = self.pac_man.sprite
        for dot in eat(pac_man, self.dots):
            self.session.score += points(dot)
        for pellet in eat(pac_man, self.power_pellets):
            self.session.score += points(pellet)
            pellet.activate(self)

        for ghost in touched_ghosts(pac_man, self.ghosts):
            if ghost.is_edible:
                self.session.score += points(ghost)
                ghost.get_eaten()
            elif ghost.is_dangerous:
                self._lose_life()
                return

        if not self.dots:
            LOGGER.info('level %d cleared, score %d',
                        self.session.level, self.session.score)
            self.session.level += 1
            self._new_level()

    def _lose_life(self) -> None:
        """Lose a life; everyone back to start, or game over at 0 lives."""
        self.session.lives -= 1
        if self.session.is_over:
            LOGGER.info('game over, score %d', self.session.score)
            self.session = Session(lives=self.config.lives)
            self._new_level()
            return
        self.pac_man.sprite.respawn()
        for ghost in self.ghosts:
            ghost.calm()
            ghost.respawn()

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
        self.pac_man.draw(self.screen)
        self.ghosts.draw(self.screen)

        # Draw UI.
        draw_hud(self.screen, self.session)

        pygame.display.flip()
