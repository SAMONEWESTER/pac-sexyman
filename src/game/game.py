"""The main game loop."""

from __future__ import annotations

import pygame

from ..node import Scene, Level

from ..audio import AUDIO
from ..config import FPS, CONFIG
from ..controls import Controls
# from ..errors import LOGGER
# from ..leaderboard import (
#     GAME_OVER_SECONDS,
#     GAME_OVER_SKIP_DELAY,
#     Leaderboard,
# )
from ..resources import ASSETS, FONTS
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

        # Player state.
        self.players = tuple(Player() for _ in range(4))
        self.players[0].start(CONFIG.lives)

        self.scene = Level(self.players, 0)
        "Current scene and parent of all entities."
        self.scene.is_ready = True
        self.scene._on_enter_tree()

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

    def run(self) -> None:
        """Run the main loop until the player quits."""
        self.running = True
        while self.running:
            self.dt = min(self.clock.tick(FPS) / 1000, MAX_DT)

            self.__handle_events()
            self.scene.update(self.dt)
            if self.scene.next_scene:
                self.scene = self.scene.next_scene
                continue
            self.screen.fill((0, 0, 0))
            self.scene.draw(self.screen)

            pygame.display.flip()
        # self.leaderboard.close()

    # Input.
    # --------------------------------------------------------------------------
    def __handle_events(self) -> None:
        """Process window, keyboard and mouse events."""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.running = False
                else:
                    self.scene.handle_key(event)

    # Leaderboard and game over screen.
    # --------------------------------------------------------------------------
    # def __submit_run(self, index: int) -> None:
    #     """Send a finished run to the leaderboard (in the background).

    #     The score already holds every level of the run added up.

    #     Args:
    #         index: The player whose run just ended.
    #     """
    #     player = self.players[index]
    #     name = CONFIG.player_name(index)
    #     if self.leaderboard.submit(name, player.score, self.level + 1):
    #         LOGGER.info('player %d queued for the leaderboard as %s',
    #                     index, name)

    # def __update_game_over(self, game_over_at: float) -> None:
    #     """Count down the game over screen, then start a new game."""
    #     waited = self.t - game_over_at
    #     # The cards keep the final scores and blink their join prompts.
    #     self.player_stats_panels.update(self.dt, self.t)
    #     self.leaderboard_panel.update(
    #         GAME_OVER_SECONDS - waited, waited >= GAME_OVER_SKIP_DELAY)
    #     if waited >= GAME_OVER_SECONDS:
    #         self.__restart()
