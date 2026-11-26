from __future__ import annotations

from random import choice
from typing import TYPE_CHECKING, Any

import pygame
from pygame import Surface, Vector2
from pygame.display import get_surface
from pygame.event import Event
from pygame.sprite import Sprite, Group, GroupSingle, AbstractGroup

from ...debug.ai_visualizer import AIVisualizer
from ...entities.ui.leaderboard_panel import LeaderboardPanel

from ..node import Node
from ..entity.collider import Collider
from ..entity.camera import Camera
from ..entity.sprite.world_sprite import WorldSprite
from ..entity.sprite.canvas_sprite import CanvasSprite
from ..entity.item.powerpellet import PowerPellet
from ..entity.item.fruit import Fruit
from ..entity.float_animation import FloatStyle
from ..entity.actor.pacman import PacMan

from ...game.collisions import eat, points, touched_ghosts
from ...game.collision_manager import CollisionManager
if TYPE_CHECKING:
    from ...game import Player


from ...audio import AUDIO, SoundEffect, music_for_level, sounds
from ...errors import LOGGER
from ...controls import (
    P1_DIRECTIONS,
    P2_DIRECTIONS,
    P3_DIRECTIONS,
    P4_DIRECTIONS,
    Action,
    Controls
)
from ...grid import cell_center
from ...resources import ASSETS, text_to_image
from ...config import CONFIG
from ...level import Maze, spawn_ghosts, spawn_dots
from ...entities import (
    PacMan as Pac_Man,
    WorldMessage,
    PlayerStatsPanel,
    TimePanel,
)
from .scene import Scene
from ...leaderboard import (
    # GAME_OVER_SECONDS,
    GAME_OVER_SKIP_DELAY,
    Leaderboard,
)
from ...utils.get_time import get_time

CONFIRM_ACTIONS: tuple[Action, ...] = (
    Action.P1_CONFIRM,
    Action.P2_CONFIRM,
    Action.P3_CONFIRM,
    Action.P4_CONFIRM,
)
"""Join keys, in player order; they also skip the game over screen."""


class Level(Scene):
    def __init__(
            self,
            players: tuple[Player, ...],
            level: int,
            ) -> None:
        super().__init__()
        self.controls = Controls()
        self.level = level
        level_looped = level % len(CONFIG.levels)
        self.collision_manager = CollisionManager()

        # Cheats and debug visualization.
        self.invincibility = False
        self.speedup = False
        self.ai_debug = False
        self.ai_visualizers: list[AIVisualizer] = []

        style = FloatStyle.from_index(level)
        theme = (level // 3) % len(ASSETS.tilesets)

        maze_size = \
            CONFIG.levels[level_looped].size
        maze_area = maze_size[0] * maze_size[1]
        self.time_limit = \
            maze_area * (maze_area * 0.002 + CONFIG.time_multiplier)
        maze = Maze(maze_size, theme, None if level else CONFIG.seed)
        self.maze = maze
        maze_sprite = WorldSprite(maze.image)
        maze_sprite.offset.update((maze.w * 16, maze.h * 16))
        self.add_child(maze_sprite)

        # Dots.
        # ----------------------------------------------------------------------
        dots = spawn_dots(maze, style)
        self.starting_dot_count = len(dots)
        self.add_children(dots)

        # Power Pellets.
        # ----------------------------------------------------------------------
        self.add_children(
            PowerPellet(maze.cell_center(corner), style, theme)
            for corner in maze.corners
        )

        # Pacmen.
        # ----------------------------------------------------------------------
        self.pacmen = [PacMan(maze.center, maze, i) for i in range(4)]
        self.add_children(self.pacmen)

        # Ghosts.
        # ----------------------------------------------------------------------
        self.ghosts = spawn_ghosts(
            maze,
            self.pacmen,
            CONFIG.levels[level_looped].ghosts,
        )
        self.add_children(self.ghosts)

        # ----------------------------------------------------------------------
        self.players = players
        for i, pacman in enumerate(self.pacmen):
            pacman.active = not players[i].is_over

        # HUD panels are drawn at the bottom of the screen, outside the maze.
        self.player_stats_panels: Group[PlayerStatsPanel] = Group(
            PlayerStatsPanel(
                self.players[i],
                i,
                (144 + 264 * i, get_surface().get_height() - 118)
            ) for i in range(4)
        )
        self.time_panel: GroupSingle[TimePanel] = GroupSingle(
            TimePanel(
                (
                    get_surface().get_width() - 224,
                    get_surface().get_height() - 96
                )
            )
        )
        self.camera = Camera(
            (
                CONFIG.levels[level_looped].size[0] * 32,
                CONFIG.levels[level_looped].size[1] * 32
            ),
            90
        )

        self.leaderboard = Leaderboard(CONFIG)
        self.leaderboard_panel = LeaderboardPanel(
            self.leaderboard, get_surface().get_size())
        self.game_over_at: float | None = None
        "Time the game over screen opened; ``None`` while running."

        self.ghost_combo = 1
        "Point multiplier for eating multiple ghosts in a row."

        AUDIO.play_music(music_for_level(self.level))

    # def __apply_rules(self) -> None:
    #     """Eating, scoring, losing lives and clearing the level."""
    #     for i, pacman in enumerate(self.pacmen.sprites()):
            # dots = eat(pac_man, self.dots)
            # if dots:
            #     AUDIO.play(sounds.DOT_EATEN)
            # for dot in dots:
            #     self._award(pac_man.player, points(dot))
            #     if len(self.dots) == self.starting_dot_count // 2:
            #         self.__spawn_fruit()
            #     pac_man.lag = 0.1
            # for pellet in eat(pac_man, self.power_pellets):
            #     LOGGER.info('power pellet eaten by player %d', pacman.player)
            #     AUDIO.play(sounds.POWER_PELLET_EATEN)
            #     self._award(pac_man.player, points(pellet))
            #     pellet.activate(self)
            #     self.ghost_combo = 1
            #     pac_man.lag = 0.1
            # for fruit in eat(pacman, self.fruits):
            #     LOGGER.info('fruit eaten by player %d', pacman.player)
            #     AUDIO.play(sounds.POWER_PELLET_EATEN)
            #     scored_points = points(fruit) * (self.level + 1)
            #     self._award(pacman.player, scored_points)
            #     self.__message(pacman.pos, scored_points)
            #     pacman.lag = 0.1

            # for ghost in touched_ghosts(pacman, self.ghosts):
            #     if ghost.is_edible:
            #         LOGGER.info('ghost eaten by player %d', pacman.player)
            #         AUDIO.play(sounds.GHOST_EATEN)
            #         scored_points = points(ghost) * self.ghost_combo
            #         self._award(pacman.player, scored_points)
            #         self.__message(pacman.pos, scored_points)
            #         ghost.get_eaten()
            #         self.ghost_combo *= 2
            #         pacman.lag = 0.1
            #     elif ghost.is_dangerous \
            #             and not pacman.is_invincible(get_time()):
            #         LOGGER.info('player %d caught by ghost', pacman.player)
            #         self.players[pacman.player].lives -= 1
            #         if not self.players[pacman.player].is_over:
            #             AUDIO.play(sounds.PLAYER_DIED)
            #             pacman.respawn(get_time())
            #         else:
            #             LOGGER.info(
            #                 'player %d ran out of lives with %d points',
            #                 pacman.player, self.players[pacman.player].score)
            #             # self.__submit_run(pac_man.player)
            #             pacman.kill()
            #             if not self.pacmen:
            #                 self._lose()
            #             else:
            #                 AUDIO.play(sounds.PLAYER_OUT)
            #         ghost.lag = 0.25
            #         return

        # if not self.dots:
        #     score = sum(x.score for x in self.players)
        #     LOGGER.info('level %d cleared with %d points', self.level, score)
        #     AUDIO.play(sounds.LEVEL_CLEARED)
        #     self.next_scene = Level(self.players, self.level + 1)

    def award(self, player: int, scored_points: int) -> None:
        """Give a player points, with a jingle when a life is earned."""
        if self.players[player].add_points(scored_points):
            AUDIO.play(sounds.EXTRA_LIFE)

    def _lose(self, sound: SoundEffect = sounds.GAME_OVER) -> None:
        """Lose the game and open the game over screen.

        Players still alive (the time ran out) end their run here, so
        their score reaches the leaderboard too.

        Args:
            sound: What to play; the time running out has its own sound.
        """
        score = sum(max(x.score, 0) for x in self.players)
        LOGGER.info('game over on level %d with %d points', self.level, score)
        AUDIO.play(sound)
        self.__player_start(0)
        self.__next_level(0)
        # for index, player in enumerate(self.players):
        #     if not player.is_over:
        #         self.__submit_run(index)
        #         player.end()
        # self.leaderboard.refresh()
        # self.game_over_at = get_time()

    def __player_start(self, player_id: int) -> None:
        LOGGER.info('player %d joined the game', player_id)
        AUDIO.play(sounds.PLAYER_JOINED)
        self.players[player_id].start(CONFIG.lives)
        pacman = self.pacmen[player_id]
        pacman.active = True
        pacman.start_time = get_time()

    def frighten_ghosts(self, seconds: float) -> None:
        """Make every ghost edible for a while (``PowerUpTarget``).

        Args:
            seconds: How long the ghosts stay edible.
        """
        for ghost in self.ghosts:
            ghost.frighten(seconds)

    def update(self, dt: float) -> bool:
        """Advance every entity by one frame, then apply the rules."""
        if not self.active:
            return False

        if get_time() - self.start_time > self.time_limit:
            self._lose(sounds.TIME_UP)
            return

        result = super().update(dt)
        self.collision_manager.update()
        return result

    def draw(self, screen: Surface, camera: Camera | None = None) -> bool:
        """Draw the maze and every entity in it."""
        if not self.active:
            return False
        return super().draw(screen, self.camera)

    def handle_key(self, event: Event) -> None:
        def __handle_cheats(key: Any) -> None:
            if key == pygame.K_1:
                if self.invincibility:
                    LOGGER.info("CHEAT: invincibility OFF")
                    for pacman in self.pacmen:
                        self.__message(pacman.offset, 'Not invincible!')
                        pacman.start_time = float("-inf")
                else:
                    LOGGER.info("CHEAT: invincibility ON")
                    for pacman in self.pacmen:
                        self.__message(pacman.offset, 'Invincible!')
                        pacman.start_time = float("inf")
                self.invincibility = not self.invincibility
            elif key == pygame.K_2:
                LOGGER.info("CHEAT: skipped level %d", self.level)
                self.__next_level()
            elif key == pygame.K_3:
                if self.ghosts[0].cheat_speed_multiplier == 1.0:
                    LOGGER.info("CHEAT: frozen ghosts ON")
                    for ghost in self.ghosts:
                        self.__message(ghost.offset, 'Frozen!')
                        ghost.cheat_speed_multiplier = 0.0
                else:
                    LOGGER.info("CHEAT: frozen ghosts OFF")
                    for ghost in self.ghosts:
                        self.__message(ghost.offset, 'Unfrozen!')
                        ghost.cheat_speed_multiplier = 1.0
            elif key == pygame.K_4:
                LOGGER.info("CHEAT: extra lives added")
                for pacman in self.pacmen:
                    self.__message(pacman.offset, 'Extra life!')
                    self.players[pacman.player].add_life()
            elif key == pygame.K_5:
                if self.speedup:
                    LOGGER.info("CHEAT: increased player speed OFF")
                    for pacman in self.pacmen:
                        self.__message(pacman.offset, 'Normal speed!')
                        pacman.cheat_speed_multiplier = 1.0
                else:
                    LOGGER.info("CHEAT: increased player speed ON")
                    for pacman in self.pacmen:
                        self.__message(pacman.offset, 'Increased speed!')
                        pacman.cheat_speed_multiplier = 1.5
                self.speedup = not self.speedup
            elif key == pygame.K_6:
                LOGGER.info("CHEAT: toggled debug mode")
                self.__message(
                    Vector2(self.maze.w * 16, self.maze.sprite.h * 16),
                    'Debug mode toggled'
                )
                self.ai_debug = not self.ai_debug

        def __handle_game_over_key(
                action: Action | None,
                game_over_at: float,
                ) -> None:
            """Quit, or let whoever presses confirm start the next game."""
            if action is Action.QUIT:
                pygame.event.post(Event(pygame.QUIT))
            elif action in CONFIRM_ACTIONS \
                    and get_time() - game_over_at >= GAME_OVER_SKIP_DELAY:
                self.__next_level(0)

        action = self.controls.action_for(event.key)

        if self.game_over_at is not None:
            __handle_game_over_key(action, self.game_over_at)
            return

        if action in P1_DIRECTIONS:
            if self.pacmen[0].active:
                self.pacmen[0].steer(P1_DIRECTIONS[action])
        elif action in P2_DIRECTIONS:
            if self.pacmen[1].active:
                self.pacmen[1].steer(P2_DIRECTIONS[action])
        elif action in P3_DIRECTIONS:
            if self.pacmen[2].active:
                self.pacmen[2].steer(P3_DIRECTIONS[action])
        elif action in P4_DIRECTIONS:
            if self.pacmen[3].active:
                self.pacmen[3].steer(P4_DIRECTIONS[action])

        elif action is Action.P1_CONFIRM and self.players[0].is_over:
            self.__player_start(0)
        elif action is Action.P2_CONFIRM and self.players[1].is_over:
            self.__player_start(1)
        elif action is Action.P3_CONFIRM and self.players[2].is_over:
            self.__player_start(2)
        elif action is Action.P4_CONFIRM and self.players[3].is_over:
            self.__player_start(3)

        if CONFIG.cheatmode:
            __handle_cheats(event.key)

    def __next_level(self, level: int | None = None) -> None:
        "Start the next level."
        if level is None:
            level = self.level + 1
        self.next_scene = Level(self.players, level)

    # def __spawn_fruit(self) -> None:
    #     position = choice(tuple(self.maze.sprite.corridors))
    #     LOGGER.info("spawning fruit at (%d, %d)", *position)
    #     self.fruits.add(Fruit(
    #             cell_center(position),
    #             CONFIG.points_per_powerpellet * 4,
    #             self.level
    #         )
    #     )
