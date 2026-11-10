"""The main game loop."""

from __future__ import annotations

import pygame
from pygame import Surface
from pygame.event import Event
from pygame.sprite import AbstractGroup, Group, GroupSingle, Sprite

from ..config import FPS, Config
from ..controls import (
    P1_DIRECTIONS,
    P2_DIRECTIONS,
    P3_DIRECTIONS,
    P4_DIRECTIONS,
    Action,
    Controls
)
from ..entities import (
    Dot,
    Ghost,
    IdleStyle,
    PacMan,
    PowerPellet,
    PointMessage,
    PlayerStatsPanel,
    TimePanel
)
from ..errors import LOGGER
from ..level import (
    Maze,
    spawn_dots,
    spawn_ghosts,
)
from ..resources import ASSETS, FONTS
from ..grid import cell_center
from .collisions import eat, points, touched_ghosts
from .player import Player
from .window import create_window
from .camera import Camera

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
        self.time_multiplier = config.time_multiplier
        if config.cheatmode:
            print(
                "Cheats activated, enter number keys:\n"
                "- 1: Invincibility\n"
                "- 2: Skip current level\n"
                "- 3: Frozen ghosts\n"
                "- 4: Add extra lives\n"
                "- 5: Increased player speed"
            )

        self.controls = controls or Controls()

        maze_size = config.levels[0].size
        self.screen = create_window((maze_size[0], maze_size[1] + 1))
        self.camera = Camera(
            self.screen,
            (maze_size[0] * 32, maze_size[1] * 32),
            90
        )

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

        # HUD panels are drawn at the bottom of the screen, outside the maze.
        self.player_stats_panels: Group[PlayerStatsPanel] = Group(
            PlayerStatsPanel(
                self.players[i],
                i,
                (144 + 264 * i, self.screen.get_height() - 118)
            ) for i in range(4)
        )
        self.time_panel: GroupSingle[TimePanel] = GroupSingle(
            TimePanel(
                90,
                (self.screen.get_width() - 224, self.screen.get_height() - 96)
            )
        )

        self.bg_color = ASSETS.tilesets[0][15].get_at((0, 0))
        self.ghost_combo = 1
        "Point multiplier for eating multiple ghosts in a row."

        self.clock = pygame.time.Clock()
        self.start_time = 0.0
        "Time when the level began."
        self.dt = 0.0
        "Time since the last clock tick."
        self.elapsed_time = 0.0
        "Time elapsed since beginning of the game."

        self.running = False
        self.__next_level(0)

    def run(self) -> None:
        """Run the main loop until the player quits."""
        self.running = True
        while self.running:
            self.__handle_events()
            self.__update()
            self.__draw()
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
    # --------------------------------------------------------------------------
    def __spawn_pacman(self, player_id: int) -> None:
        pac_man = PacMan(self.maze.sprite, player_id, self.elapsed_time)
        self.pac_man_by_player[player_id] = pac_man
        self.pac_men.add(pac_man)

    def __next_level(self, index: int | None = None) -> None:
        """Create a new maze populated with objects.

        Args:
            index: Optionally select a specific level to go to.
        """
        if index is not None:
            self.level = index
        else:
            self.level += 1
        theme = (self.level // 3) % len(ASSETS.tilesets)
        style = self.styles[self.level % 3]
        maze_size = \
            self.config.levels[self.level % len(self.config.levels)].size
        self.time_limit = maze_size[0] * maze_size[1] * self.time_multiplier
        maze = Maze(maze_size, theme, 0 if self.level else self.config.seed)
        self.maze.add(maze)

        self.dots = spawn_dots(maze, style, self.config.points_per_dot)
        self.starting_dot_count = len(self.dots)

        self.power_pellets = Group(
            PowerPellet(
                cell_center(corner),
                style,
                self.config.points_per_powerpellet,
                maze.theme
            )
            for corner in maze.corners
        )

        self.pac_men.empty()
        for i in range(4):
            if not self.players[i].is_over:
                self.__spawn_pacman(i)

        self.ghosts = spawn_ghosts(
            maze,
            self.pac_men,
            self.config.points_per_ghost,
            ('blinky', 'pinky', 'inky', 'clyde'),
        )

        self.bg_color = ASSETS.tilesets[theme][15].get_at((0, 0))
        self.camera = Camera(
            self.screen, (maze_size[0] * 32, maze_size[1] * 32), 90)
        self.start_time = self.elapsed_time

    def __player_start(self, index: int) -> None:
        LOGGER.info('player %d joined the game', index)
        self.players[index].start(self.config.lives)
        self.__spawn_pacman(index)

    # Input.
    # --------------------------------------------------------------------------
    def __handle_events(self) -> None:
        """Process window, keyboard and mouse events."""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.KEYDOWN:
                self.__handle_key(event)
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if pygame.mouse.get_pressed()[1]:
                    self.point_messages.add(PointMessage(
                        self.pac_men.sprites()[0].pos,
                        42,
                        self.elapsed_time))

    def __handle_key(self, event: Event) -> None:
        action = self.controls.action_for(event.key)

        if action in P1_DIRECTIONS:
            pac_man = self.pac_man_by_player.get(0)
            if pac_man:
                pac_man.steer(P1_DIRECTIONS[action])
        elif action in P2_DIRECTIONS:
            pac_man = self.pac_man_by_player.get(1)
            if pac_man:
                pac_man.steer(P2_DIRECTIONS[action])
        elif action in P3_DIRECTIONS:
            pac_man = self.pac_man_by_player.get(2)
            if pac_man:
                pac_man.steer(P3_DIRECTIONS[action])
        elif action in P4_DIRECTIONS:
            pac_man = self.pac_man_by_player.get(3)
            if pac_man:
                pac_man.steer(P4_DIRECTIONS[action])

        elif action is Action.P1_CONFIRM and self.players[0].is_over:
            self.__player_start(0)
        elif action is Action.P2_CONFIRM and self.players[1].is_over:
            self.__player_start(1)
        elif action is Action.P3_CONFIRM and self.players[2].is_over:
            self.__player_start(2)
        elif action is Action.P4_CONFIRM and self.players[3].is_over:
            self.__player_start(3)

        elif action is Action.QUIT:
            self.running = False

        if self.config.cheatmode:
            self.__handle_cheats(event.key)

    # Frame update.
    # --------------------------------------------------------------------------
    def __update(self) -> None:
        """Advance every entity by one frame, then apply the rules."""
        frame = (self.dt, self.elapsed_time)
        if self.elapsed_time - self.start_time > self.time_limit:
            self.__lose()

        self.dots.update(*frame)
        self.power_pellets.update(*frame)
        self.pac_men.update(*frame)
        self.ghosts.update(*frame)
        self.point_messages.update(*frame)
        self.player_stats_panels.update(*frame)
        self.time_panel.update(
            self.time_limit - (self.elapsed_time - self.start_time))
        self.__apply_rules()

    def __apply_rules(self) -> None:
        """Eating, scoring, losing lives and clearing the level."""
        for i, pac_man in enumerate(self.pac_men.sprites()):
            for dot in eat(pac_man, self.dots):
                self.players[pac_man.player].add_points(points(dot))
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
                            self.__lose()
                    ghost.lag = 0.25
                    return

        if not self.dots:
            score = sum(x.score for x in self.players)
            LOGGER.info('level %d cleared with %d points', self.level, score)
            self.__next_level()

    def __lose(self) -> None:
        """Lose the game."""
        score = sum(x.score for x in self.players)
        LOGGER.info('game over on level %d with %d points', self.level, score)
        self.players[0].start(self.config.lives)
        self.__next_level(0)

    # Cheats.
    # --------------------------------------------------------------------------
    def __handle_cheats(self, key) -> None:
        if key == pygame.K_1:
            pacmen = self.pac_men.sprites()
            if pacmen[0].last_respawn != float("inf"):
                LOGGER.info("CHEAT: invincibility ON")
                for pacman in pacmen:
                    pacman.last_respawn = float("inf")
            else:
                LOGGER.info("CHEAT: invincibility OFF")
                for pacman in pacmen:
                    pacman.last_respawn = float("-inf")
        elif key == pygame.K_2:
            LOGGER.info("CHEAT: skipped level %d", self.level)
            self.__next_level()
        elif key == pygame.K_3:
            ghosts = self.ghosts.sprites()
            if ghosts[0].speed_multiplier == 1.0:
                LOGGER.info("CHEAT: frozen ghosts ON")
                for ghost in ghosts:
                    ghost.speed_multiplier = 0.0
            else:
                LOGGER.info("CHEAT: frozen ghosts OFF")
                for ghost in ghosts:
                    ghost.speed_multiplier = 1.0
        elif key == pygame.K_4:
            pacmen = self.pac_men.sprites()
            LOGGER.info("CHEAT: extra lives added")
            for pacman in pacmen:
                self.players[pacman.player].add_life()
        elif key == pygame.K_5:
            pacmen = self.pac_men.sprites()
            if pacmen[0].speed_multiplier == 1.0:
                LOGGER.info("CHEAT: increased player speed ON")
                for pacman in pacmen:
                    pacman.speed_multiplier = 1.5
            else:
                LOGGER.info("CHEAT: increased player speed OFF")
                for pacman in pacmen:
                    pacman.speed_multiplier = 1.0

    # Drawing.
    # --------------------------------------------------------------------------
    def __draw(self) -> None:
        """Draw the background, sprites and UI, then show the frame."""
        def __draw_world_group(
                group: AbstractGroup[Sprite],
                screen: Surface,
                camera: Camera,
                ) -> None:
            for sprite in group:
                image = pygame.transform.scale(
                    sprite.image,
                    camera.size(sprite.image.get_size()))
                rect = image.get_rect(
                    center=camera.point(sprite.rect.center))
                screen.blit(image, rect)

        def __draw_scaled(
                group: AbstractGroup[Sprite],
                screen: Surface,
                ) -> None:
            for sprite in group:
                width, height = sprite.image.get_size()
                image = pygame.transform.scale(
                    sprite.image, (width * 3, height * 3))
                rect = image.get_rect(topleft=sprite.rect.topleft)
                screen.blit(image, rect)

        self.screen.fill(self.bg_color)

        for group in (
                self.maze,
                self.dots,
                self.power_pellets,
                self.pac_men,
                self.ghosts,
                self.point_messages):
            __draw_world_group(group, self.screen, self.camera)

        # Draw UI.
        __draw_scaled(self.player_stats_panels, self.screen)
        __draw_scaled(self.time_panel, self.screen)

        pygame.display.flip()
