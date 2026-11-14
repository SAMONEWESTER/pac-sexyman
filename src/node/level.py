from __future__ import annotations

from typing import TYPE_CHECKING

import pygame
from pygame import Surface, Vector2
from pygame.sprite import Sprite, Group, GroupSingle, AbstractGroup

if TYPE_CHECKING:
    from ..game import Player

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
)

from .scene import Scene
from ..game.camera import Camera


class Level(Scene):
    def __init__(
            self,
            players: tuple[Player, ...],
            index: int
            ) -> None:
        super().__init__()
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
        self.power_pellets = Group(
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
        ):
            group.update(dt, elapsed)
        # self.player_stats_panels.update(*frame)
        # self.time_panel.update(
        #     self.time_limit - (self.elapsed_time - self.start_time))
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
        # self.player_stats_panels.draw(screen)
        # self.time_panel.draw(screen)

    def enter(self) -> None:
        pass

    def exit(self) -> None:
        pass
