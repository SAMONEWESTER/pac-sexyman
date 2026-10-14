import json
from random import randint

import pygame
from pygame import image, Vector2
from pygame.sprite import Group, GroupSingle

from .maze import Maze
from .assets import ASSETS
from .pac_dot import PacDot


pygame.init()


def randcolor() -> pygame.Color:
    return pygame.Color(randint(64, 255), randint(64, 255), randint(64, 255))


# Load the config with all comments discarded.
# -----------------------------------------------------------------------------
with open('config.json') as f:
    config = json.loads(
        ''.join(x for x in f.readlines() if not x.strip().startswith('#')))


# Setup program.
# -----------------------------------------------------------------------------
maze_size = (config['level'][0]['width'], config['level'][0]['height'])
w, h = maze_size[0] * 32, maze_size[1] * 32
pygame.display.set_icon(image.load('assets/gfx/obj/power_pellet.png'))

screen = pygame.display.set_mode((w, h), pygame.SCALED)
pygame.display.set_caption('pac-man')
clock = pygame.time.Clock()


ASSETS.load_all()


def generate_dots(maze: Maze) -> Group:
    result = Group()
    for (x, y), cell in maze:
        if cell != 15:
            result.add(PacDot((x * 32 + 16, y * 32 + 16)))
        if not (cell & 2):
            result.add(PacDot((x * 32 + 32, y * 32 + 16)))
        if not (cell & 4):
            result.add(PacDot((x * 32 + 16, y * 32 + 32)))
    return result
    # maze.image.blit(
    #     ASSETS.power_pellet, (8, 8))
    # maze.image.blit(
    #     ASSETS.power_pellet, ((maze.w - 1) * 32 + 8, 8))
    # maze.image.blit(
    #     ASSETS.power_pellet, (8, (maze.h - 1) * 32 + 8))
    # maze.image.blit(
    #     ASSETS.power_pellet, ((maze.w - 1) * 32 + 8, (maze.h - 1) * 32 + 8))


maze = GroupSingle(Maze(ASSETS.tileset0, randcolor(), maze_size))
# draw_dots(maze.sprite)
pacdots = generate_dots(maze.sprite)

cam = Vector2()


# Main game loop.
# -----------------------------------------------------------------------------
elapsed_time = 0.0
running = True
while running:
    # Handle events.
    for event in pygame.event.get():
        keys = pygame.key.get_pressed()
        if event.type == pygame.QUIT or keys[pygame.K_ESCAPE]:
            running = False
        if event.type == pygame.MOUSEBUTTONDOWN:
            if pygame.mouse.get_pressed()[0]:
                maze.add(Maze(ASSETS.tileset0, randcolor(), maze_size))
                pacdots = generate_dots(maze.sprite)

    # Draw background.
    screen.fill(0)
    maze.draw(screen)

    # Update and draw sprite groups.
    pacdots.update(elapsed_time)
    pacdots.draw(screen)

    # Draw UI.

    # Update screen and clock.
    pygame.display.flip()
    elapsed_time += clock.tick(60) / 1000

pygame.quit()
