"""The main game loop."""

from __future__ import annotations

import pygame
from pygame import Vector2
from pygame.event import Event
from pygame.sprite import Group, GroupSingle

from ..config import FPS, Config
from ..controls import P1_DIRECTIONS, P2_DIRECTIONS, Action, Controls
from ..entities import Dot, Ghost, IdleStyle, PacMan, PowerPellet, PointMessage
from ..errors import LOGGER
from ..level import (
    Maze,
    generate_dots,
    generate_power_pellets,
    spawn_ghosts,
)
from ..resources import ASSETS, FONTS
from .collisions import eat, points, touched_ghosts
from .hud import blit_player_stats, blit_time
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
        self.time_limit = config.level_max_time
        self.screen = create_window((self.maze_size[0], self.maze_size[1] + 1))
        self.clock = pygame.time.Clock()

        ASSETS.load_all()
        FONTS.load_all()

        self.styles: list[IdleStyle] = list(IdleStyle)
        self.maze: GroupSingle[Maze] = GroupSingle()

        self.dots: Group[Dot] = Group()
        self.power_pellets: Group[PowerPellet] = Group()
        self.pac_men: Group[PacMan] = Group()
        self.ghosts: Group[Ghost] = Group()
        self.point_messages: Group[PointMessage] = Group()

        self.players = tuple(Player() for _ in range(4))
        self.players[0].start(config.lives)
        self.pac_man_by_player: dict[int, PacMan] = {}

        self.ghost_combo = 1
        "Point multiplier for eating multiple ghosts in a row."
        self.cam = Vector2()
        "Camera position."
        self.start_time = 0.0
        "Time when the level began."

        self.dt = 0.0
        "Time since the last clock tick."
        self.elapsed_time = 0.0
        "Time elapsed since beginning of the game."
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
    def _spawn_pacman(self, player_id: int) -> None:
        pac_man = PacMan(self.maze.sprite, player_id, self.elapsed_time)
        self.pac_man_by_player[player_id] = pac_man
        self.pac_men.add(pac_man)

    def _next_level(self, index: int | None = None) -> None:
        """Create a new maze populated with objects.

        Args:
            index: Optionally select a specific level to go to.
        """
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
        self.starting_dot_count = len(self.dots)
        self.power_pellets = generate_power_pellets(
            maze, style, self.config.points_per_super_pacgum)

        self.pac_men.empty()
        for i in range(4):
            if not self.players[i].is_over:
                self._spawn_pacman(i)

        self.ghosts = spawn_ghosts(
            maze, self.pac_men, self.config.points_per_ghost)

        self.start_time = self.elapsed_time

    def _player_start(self, index: int) -> None:
        LOGGER.info('player %d joined the game', index)
        self.players[index].start(self.config.lives)
        self._spawn_pacman(index)

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
                if pygame.mouse.get_pressed()[1]:
                    self.point_messages.add(PointMessage(
                        self.pac_men.sprites()[0].pos,
                        42,
                        self.elapsed_time))

    def _handle_key(self, event: Event) -> None:
        action = self.controls.action_for(event.key)

        if action in P1_DIRECTIONS:
            pac_man = self.pac_man_by_player.get(0)
            if pac_man:
                pac_man.steer(P1_DIRECTIONS[action])
        elif action in P2_DIRECTIONS:
            pac_man = self.pac_man_by_player.get(1)
            if pac_man:
                pac_man.steer(P2_DIRECTIONS[action])

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
        if self.elapsed_time - self.start_time > self.time_limit:
            self._lose()

        self.dots.update(*frame)
        self.power_pellets.update(*frame)
        self.pac_men.update(*frame)
        self.ghosts.update(*frame)
        self.point_messages.update(*frame)
        self._apply_rules()

    def _apply_rules(self) -> None:
        """Eating, scoring, losing lives and clearing the level."""
        for i, pac_man in enumerate(self.pac_men.sprites()):
            for dot in eat(pac_man, self.dots):
                self.players[pac_man.player].add_points(points(dot))
                self.start_time += 0.125
                pac_man.lag = 0.1
            for pellet in eat(pac_man, self.power_pellets):
                LOGGER.info('power pellet eaten by player %d', pac_man.player)
                self.players[pac_man.player].add_points(points(pellet))
                pellet.activate(self)
                self.ghost_combo = 1
                pac_man.lag = 0.1

            for ghost in touched_ghosts(pac_man, self.ghosts):
                if ghost.is_edible:
                    LOGGER.info('ghost eaten by player %d', pac_man.player)
                    scored_points = points(ghost) * self.ghost_combo
                    self.players[pac_man.player].add_points(
                        points(ghost) * self.ghost_combo)
                    self.point_messages.add(PointMessage(
                        pac_man.pos, scored_points, self.elapsed_time))
                    ghost.get_eaten()
                    self.ghost_combo *= 2
                    pac_man.lag = 0.1
                elif ghost.is_dangerous \
                        and not pac_man.is_invincible(self.elapsed_time):
                    LOGGER.info('player %d caught by ghost', pac_man.player)
                    self.players[pac_man.player].lives -= 1
                    if not self.players[pac_man.player].is_over:
                        pac_man.respawn(self.elapsed_time)
                    else:
                        LOGGER.info(
                            'player %d ran out of lives with %d points',
                            pac_man.player, self.players[pac_man.player].score)
                        pac_man.kill()
                        if not self.pac_men:
                            self._lose()
                    ghost.lag = 0.25
                    return

        if not self.dots:
            score = sum(x.score for x in self.players)
            LOGGER.info('level %d cleared with %d points', self.level, score)
            self._next_level()

    def _lose(self) -> None:
        """Lose the game."""
        score = sum(x.score for x in self.players)
        LOGGER.info('game over on level %d with %d points', self.level, score)
        self.players[0].start(self.config.lives)
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
        self.point_messages.draw(self.screen)

        # Draw UI.
        blit_player_stats(
            self.screen,
            self.players[0],
            0,
            self.elapsed_time,
            (8, self.maze_size[1] * 32))
        blit_player_stats(
            self.screen,
            self.players[1],
            1,
            self.elapsed_time,
            (96, self.maze_size[1] * 32))
        blit_time(
            self.screen,
            int(self.time_limit - (self.elapsed_time - self.start_time)),
            (self.screen.get_width() - 64, self.maze_size[1] * 32 + 8))

        pygame.display.flip()
