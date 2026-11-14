from __future__ import annotations

from typing import TYPE_CHECKING, Any

import pygame
from pygame import Surface, Vector2
from pygame.display import get_surface
from pygame.event import Event
from pygame.sprite import Sprite, Group, GroupSingle, AbstractGroup

if TYPE_CHECKING:
    from ..game import Player


from ..errors import LOGGER
from ..controls import (
    P1_DIRECTIONS,
    P2_DIRECTIONS,
    P3_DIRECTIONS,
    P4_DIRECTIONS,
    Action,
    Controls
)
from ..grid import cell_center
from ..resources import ASSETS
from ..config import CONFIG
from ..level import Maze, spawn_ghosts, spawn_dots
from ..entities.components import IdleStyle
from ..entities import (
    Dot,
    PowerPellet,
    PacMan,
    Ghost,
    Fruit,
    WorldMessage,
    PlayerStatsPanel,
    TimePanel,
)
from .scene import Scene
from ..game.camera import Camera
from ..leaderboard import (
    GAME_OVER_SECONDS,
    GAME_OVER_SKIP_DELAY,
    Leaderboard,
)

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
            index: int
            ) -> None:
        super().__init__()
        self.controls = Controls()
        self.level = index

        self.styles: list[IdleStyle] = list(IdleStyle)

        theme = (self.level // 3) % len(ASSETS.tilesets)
        style = self.styles[self.level % 3]
        maze_size = \
            CONFIG.levels[self.level % len(CONFIG.levels)].size
        maze_area = maze_size[0] * maze_size[1]
        self.time_limit = \
            maze_area * (maze_area * 0.002 + CONFIG.time_multiplier)
        maze = Maze(maze_size, theme, None if self.level else CONFIG.seed)
        self.maze: GroupSingle[Maze] = GroupSingle(maze)

        # Objects in the maze.
        self.dots = spawn_dots(maze, style, CONFIG.points_per_dot)
        self.starting_dot_count = len(self.dots)
        self.power_pellets: Group[PowerPellet] = Group(
            PowerPellet(
                cell_center(corner),
                style,
                CONFIG.points_per_powerpellet,
                maze.theme
            )
            for corner in maze.corners
        )
        self.fruits: Group[Fruit] = Group()
        self.pacmen: Group[PacMan] = Group()

        self.players = players
        self.pacman_by_player: dict[int, PacMan] = {}
        for i in range(4):
            if not self.players[i].is_over:
                self.__spawn_pacman(i)

        self.ghosts = spawn_ghosts(
            maze,
            self.pacmen,
            CONFIG.points_per_ghost,
            CONFIG.levels[self.level % len(CONFIG.levels)].ghosts,
        )
        self.world_messages: Group[WorldMessage] = Group()
        # self.ai_visualizers.clear()
        # for ghost in self.ghosts:
        #     self.ai_visualizers.append(AIVisualizer(ghost))

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
                90,
                (
                    get_surface().get_width() - 224,
                    get_surface().get_height() - 96
                )
            )
        )

        self.camera = Camera(
            (
                CONFIG.levels[self.level].size[0] * 32,
                CONFIG.levels[self.level].size[1] * 32
            ),
            90
        )

    def __spawn_pacman(self, player_id: int) -> None:
        pac_man = PacMan(
            self.maze.sprite,
            player_id,
            # self.elapsed_time if not self.invincibility else float("inf"),
            0.0
        )
        # if self.speedup:
        #     pac_man.speed_multiplier = 1.5
        self.pacman_by_player[player_id] = pac_man
        self.pacmen.add(pac_man)

    def __draw_world_group(
            self,
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
            self,
            group: AbstractGroup[Sprite],
            screen: Surface,
            ) -> None:
        for sprite in group:
            width, height = sprite.image.get_size()
            image = pygame.transform.scale(
                sprite.image, (width * 3, height * 3))
            rect = image.get_rect(topleft=sprite.rect.topleft)
            screen.blit(image, rect)

    def update(self, dt: float, elapsed: float) -> None:
        """Advance every entity by one frame, then apply the rules."""
        # if self.game_over_at is not None:
        #     self.__update_game_over(self.game_over_at)
        #     return

        # if self.elapsed_time - self.start_time > self.time_limit:
        #     self._lose(sounds.TIME_UP)
        #     return

        for group in (
                self.maze,
                self.dots,
                self.power_pellets,
                self.fruits,
                self.pacmen,
                self.ghosts,
                self.world_messages,
                self.player_stats_panels
        ):
            group.update(dt, elapsed)
        self.time_panel.update(
            self.time_limit - (elapsed - 0.0))
        # self.__apply_rules()

    def draw(self, screen: Surface) -> None:
        """Draw the maze and every entity in it."""
        for group in (
                self.maze,
                self.dots,
                self.power_pellets,
                self.fruits,
                self.pacmen,
                self.ghosts,
                self.world_messages,
        ):
            self.__draw_world_group(group, screen, self.camera)

        # if self.ai_debug:
        #     for debug_ghost in self.ai_visualizers:
        #         debug_ghost.draw(self.screen, self.camera)

        # Draw UI.
        self.__draw_scaled(self.player_stats_panels, screen)
        self.__draw_scaled(self.time_panel, screen)

        # if self.game_over_at is not None:
        #     panel = self.leaderboard_panel
        #     self.screen.blit(panel.image, panel.rect)

    def handle_key(self, event: Event) -> None:
        def __handle_cheats(self, key: Any) -> None:
            if key == pygame.K_1:
                pacmen = self.pacmen.sprites()
                if self.invincibility:
                    LOGGER.info("CHEAT: invincibility OFF")
                    for pacman in pacmen:
                        self.__message(pacman.pos, 'Not invincible!')
                        pacman.last_respawn = float("-inf")
                else:
                    LOGGER.info("CHEAT: invincibility ON")
                    for pacman in pacmen:
                        self.__message(pacman.pos, 'Invincible!')
                        pacman.last_respawn = float("inf")
                self.invincibility = not self.invincibility
            elif key == pygame.K_2:
                LOGGER.info("CHEAT: skipped level %d", self.level)
                self.__next_level()
            elif key == pygame.K_3:
                ghosts = self.ghosts.sprites()
                if ghosts[0].speed_multiplier == 1.0:
                    LOGGER.info("CHEAT: frozen ghosts ON")
                    for ghost in ghosts:
                        self.__message(ghost.pos, 'Frozen!')
                        ghost.speed_multiplier = 0.0
                else:
                    LOGGER.info("CHEAT: frozen ghosts OFF")
                    for ghost in ghosts:
                        self.__message(ghost.pos, 'Unfrozen!')
                        ghost.speed_multiplier = 1.0
            elif key == pygame.K_4:
                pacmen = self.pacmen.sprites()
                LOGGER.info("CHEAT: extra lives added")
                for pacman in pacmen:
                    self.__message(pacman.pos, 'Extra life!')
                    self.players[pacman.player].add_life()
            elif key == pygame.K_5:
                pacmen = self.pacmen.sprites()
                if self.speedup:
                    LOGGER.info("CHEAT: increased player speed OFF")
                    for pacman in pacmen:
                        self.__message(pacman.pos, 'Normal speed!')
                        pacman.speed_multiplier = 1.0
                else:
                    LOGGER.info("CHEAT: increased player speed ON")
                    for pacman in pacmen:
                        self.__message(pacman.pos, 'Increased speed!')
                        pacman.speed_multiplier = 1.5
                self.speedup = not self.speedup
            elif key == pygame.K_6:
                LOGGER.info("CHEAT: toggled debug mode")
                self.__message(
                    Vector2(self.maze.sprite.w * 16, self.maze.sprite.h * 16),
                    'Debug mode toggled'
                )
                self.ai_debug = not self.ai_debug

        def __handle_game_over_key(
                self,
                action: Action | None,
                game_over_at: float,
                ) -> None:
            """Quit, or let whoever presses confirm start the next game."""
            if action is Action.QUIT:
                self.running = False
            elif action in CONFIRM_ACTIONS \
                    and self.elapsed - game_over_at >= GAME_OVER_SKIP_DELAY:
                self.__restart(CONFIRM_ACTIONS.index(action))

        action = self.controls.action_for(event.key)

        # if self.game_over_at is not None:
        #     self.__handle_game_over_key(action, self.game_over_at)
        #     return

        if action in P1_DIRECTIONS:
            pac_man = self.pacman_by_player.get(0)
            if pac_man:
                pac_man.steer(P1_DIRECTIONS[action])
        elif action in P2_DIRECTIONS:
            pac_man = self.pacman_by_player.get(1)
            if pac_man:
                pac_man.steer(P2_DIRECTIONS[action])
        elif action in P3_DIRECTIONS:
            pac_man = self.pacman_by_player.get(2)
            if pac_man:
                pac_man.steer(P3_DIRECTIONS[action])
        elif action in P4_DIRECTIONS:
            pac_man = self.pacman_by_player.get(3)
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

        # if CONFIG.cheatmode:
        #     __handle_cheats(event.key)

    def enter(self) -> None:
        pass

    def exit(self) -> None:
        pass
