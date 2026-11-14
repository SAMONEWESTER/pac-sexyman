"""The main game loop."""

from __future__ import annotations

from random import choice

import pygame
from pygame import Surface, Vector2
from pygame.event import Event
from pygame.sprite import AbstractGroup, Group, GroupSingle, WeakDirtySprite

from ..node import Scene, Level

from ..audio import AUDIO, SoundEffect, music_for_level, sounds
from ..config import FPS, CONFIG
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
    Fruit,
    LeaderboardPanel,
    WorldMessage,
    PlayerStatsPanel,
    TimePanel
)
from ..errors import LOGGER
from ..leaderboard import (
    GAME_OVER_SECONDS,
    GAME_OVER_SKIP_DELAY,
    Leaderboard,
)
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
from ..debug import AIVisualizer

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
            controls: Controls | None = None,
            ) -> None:
        pygame.init()

        # Game state.
        self.controls = controls or Controls()
        "Key bindings; the defaults if omitted."
        self.screen = create_window(CONFIG.resolution)
        "Main game window."
        self.running = False
        "Whether the main loop is running."

        # Load all media files.
        ASSETS.load_all()
        FONTS.load_all()
        AUDIO.load_all()

        # Global time.
        self.clock = pygame.time.Clock()
        "Timekeeper. The main loop ticks it every frame."
        self.dt = 0.0
        "Time since the last clock tick."
        self.elapsed_time = 0.0
        "Time elapsed since beginning of the game."

        # Player state.
        self.players = tuple(Player() for _ in range(4))
        self.players[0].start(CONFIG.lives)

        self.scene: Scene | None = Level(self.players, 0)
        "Current scene and parent of all entities."

        self.time_multiplier = CONFIG.time_multiplier
        if CONFIG.cheatmode:
            print(
                "Cheats activated, enter number keys:\n"
                "- 1: Invincibility\n"
                "- 2: Skip current level\n"
                "- 3: Frozen ghosts\n"
                "- 4: Add extra lives\n"
                "- 5: Increased player speed\n"
                "- 6: Toggle debug mode"
            )

        # Cheats and debug visualization.
        self.invincibility = False
        self.speedup = False
        self.ai_debug = False
        self.ai_visualizers: list[AIVisualizer] = []

        self.leaderboard = Leaderboard(CONFIG)
        self.leaderboard_panel = LeaderboardPanel(
            self.leaderboard, self.screen.get_size())
        self.game_over_at: float | None = None
        "Time the game over screen opened; ``None`` while playing."

        self.bg_color = ASSETS.tilesets[0][15].get_at((0, 0))
        self.ghost_combo = 1
        "Point multiplier for eating multiple ghosts in a row."

        self.start_time = 0.0
        "Time when the level began."

        self.__next_level(0)

    def run(self) -> None:
        """Run the main loop until the player quits."""
        self.running = True
        while self.running:
            self.dt = min(self.clock.tick(FPS) / 1000, MAX_DT)
            self.elapsed_time += self.dt

            self.__handle_events()
            self.scene.update(self.dt, self.elapsed_time)
            self.screen.fill(self.bg_color)
            self.scene.draw(self.screen)

            pygame.display.flip()
        self.leaderboard.close()

    def frighten_ghosts(self, seconds: float) -> None:
        """Make every ghost edible for a while (``PowerUpTarget``).

        Args:
            seconds: How long the ghosts stay edible.
        """
        for ghost in self.ghosts:
            ghost.frighten(seconds)

    # Level setup.
    # --------------------------------------------------------------------------

    def __next_level(self, index: int | None = None) -> None:
        """Create a new maze populated with objects.

        Args:
            index: Optionally select a specific level to go to.
        """
        if index is not None:
            self.level = index
        else:
            self.level += 1

        self.bg_color = (0, 0, 0)
        # self.__new_camera()
        self.start_time = self.elapsed_time
        AUDIO.play_music(music_for_level(self.level))

    def __player_start(self, index: int) -> None:
        LOGGER.info('player %d joined the game', index)
        AUDIO.play(sounds.PLAYER_JOINED)
        self.players[index].start(CONFIG.lives)
        self.__spawn_pacman(index)

    # Input.
    # --------------------------------------------------------------------------
    def __handle_events(self) -> None:
        """Process window, keyboard and mouse events."""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.KEYDOWN:
                self.scene.handle_key(event)

    # Frame update.
    # --------------------------------------------------------------------------
    def __update(self) -> None:
        """Advance every entity by one frame, then apply the rules."""
        if self.game_over_at is not None:
            self.__update_game_over(self.game_over_at)
            return

        frame = (self.dt, self.elapsed_time)
        if self.elapsed_time - self.start_time > self.time_limit:
            self._lose(sounds.TIME_UP)
            return

        self.__apply_rules()

    def __apply_rules(self) -> None:
        """Eating, scoring, losing lives and clearing the level."""
        for i, pac_man in enumerate(self.pacmen.sprites()):
            dots = eat(pac_man, self.dots)
            if dots:
                AUDIO.play(sounds.DOT_EATEN)
            for dot in dots:
                self._award(pac_man.player, points(dot))
                if len(self.dots) == self.starting_dot_count // 2:
                    self.__spawn_fruit()
                pac_man.lag = 0.1
            for pellet in eat(pac_man, self.power_pellets):
                LOGGER.info('power pellet eaten by player %d', pac_man.player)
                AUDIO.play(sounds.POWER_PELLET_EATEN)
                self._award(pac_man.player, points(pellet))
                pellet.activate(self)
                self.ghost_combo = 1
                pac_man.lag = 0.1
            for fruit in eat(pac_man, self.fruits):
                LOGGER.info('fruit eaten by player %d', pac_man.player)
                AUDIO.play(sounds.POWER_PELLET_EATEN)
                scored_points = points(fruit) * (self.level + 1)
                self._award(pac_man.player, scored_points)
                self.__message(pac_man.pos, scored_points)
                pac_man.lag = 0.1

            for ghost in touched_ghosts(pac_man, self.ghosts):
                if ghost.is_edible:
                    LOGGER.info('ghost eaten by player %d', pac_man.player)
                    AUDIO.play(sounds.GHOST_EATEN)
                    scored_points = points(ghost) * self.ghost_combo
                    self._award(pac_man.player, scored_points)
                    self.__message(pac_man.pos, scored_points)
                    ghost.get_eaten()
                    self.ghost_combo *= 2
                    pac_man.lag = 0.1
                elif ghost.is_dangerous \
                        and not pac_man.is_invincible(self.elapsed_time):
                    LOGGER.info('player %d caught by ghost', pac_man.player)
                    self.players[pac_man.player].lives -= 1
                    if not self.players[pac_man.player].is_over:
                        AUDIO.play(sounds.PLAYER_DIED)
                        pac_man.respawn(self.elapsed_time)
                    else:
                        LOGGER.info(
                            'player %d ran out of lives with %d points',
                            pac_man.player, self.players[pac_man.player].score)
                        self.__submit_run(pac_man.player)
                        pac_man.kill()
                        if not self.pacmen:
                            self._lose()
                        else:
                            AUDIO.play(sounds.PLAYER_OUT)
                    ghost.lag = 0.25
                    return

        if not self.dots:
            score = sum(x.score for x in self.players)
            LOGGER.info('level %d cleared with %d points', self.level, score)
            AUDIO.play(sounds.LEVEL_CLEARED)
            self.__next_level()

    def _award(self, player: int, scored_points: int) -> None:
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
        for index, player in enumerate(self.players):
            if not player.is_over:
                self.__submit_run(index)
                player.end()
        self.leaderboard.refresh()
        self.game_over_at = self.elapsed_time

    # Leaderboard and game over screen.
    # --------------------------------------------------------------------------
    def __submit_run(self, index: int) -> None:
        """Send a finished run to the leaderboard (in the background).

        The score already holds every level of the run added up.

        Args:
            index: The player whose run just ended.
        """
        player = self.players[index]
        name = CONFIG.player_name(index)
        if self.leaderboard.submit(name, player.score, self.level + 1):
            LOGGER.info('player %d queued for the leaderboard as %s',
                        index, name)

    def __update_game_over(self, game_over_at: float) -> None:
        """Count down the game over screen, then start a new game."""
        waited = self.elapsed_time - game_over_at
        # The cards keep the final scores and blink their join prompts.
        self.player_stats_panels.update(self.dt, self.elapsed_time)
        self.leaderboard_panel.update(
            GAME_OVER_SECONDS - waited, waited >= GAME_OVER_SKIP_DELAY)
        if waited >= GAME_OVER_SECONDS:
            self.__restart()

    # def __restart(self, index: int = 0) -> None:
    #     """Close the game over screen and start again from level 1.

    #     Args:
    #         index: The player who starts the new game.
    #     """
    #     self.game_over_at = None
    #     self.players[index].start(CONFIG.lives)
    #     self.__next_level(0)

    # def __spawn_fruit(self) -> None:
    #     position = choice(tuple(self.maze.sprite.corridors))
    #     LOGGER.info("spawning fruit at (%d, %d)", *position)
    #     self.fruits.add(Fruit(
    #             cell_center(position),
    #             CONFIG.points_per_powerpellet * 4,
    #             self.level
    #         )
    #     )

    # def __message(self, position: Vector2, message: str) -> None:
    #     self.world_messages.add(WorldMessage(
    #         position,
    #         message,
    #         self.elapsed_time
    #     ))
