import json
from random import randint

import pygame
from pygame import image, Vector2
from pygame.sprite import GroupSingle

from .maze import Maze
from .assets import ASSETS


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

screen = pygame.display.set_mode((w, h), pygame.FULLSCREEN | pygame.SCALED)
pygame.display.set_caption('pac-man')
clock = pygame.time.Clock()


ASSETS.load_all()


def draw_dots(maze: Maze) -> None:
    # FAKE PAC-DOTS AND POWER PELLETS! JUST FOR SHOW, NOT ACTUAL OBJECTS!
    # Later, we can place them in the same positions as actual objects.
    for (x, y), cell in maze:
        if cell != 15:
            maze.image.blit(ASSETS.pac_dot, (x * 32 + 8, y * 32 + 8))
        if not (cell & 2):
            maze.image.blit(ASSETS.pac_dot, (x * 32 + 24, y * 32 + 8))
        if not (cell & 4):
            maze.image.blit(ASSETS.pac_dot, (x * 32 + 8, y * 32 + 24))
    maze.image.blit(
        ASSETS.power_pellet, (8, 8))
    maze.image.blit(
        ASSETS.power_pellet, ((maze.w - 1) * 32 + 8, 8))
    maze.image.blit(
        ASSETS.power_pellet, (8, (maze.h - 1) * 32 + 8))
    maze.image.blit(
        ASSETS.power_pellet, ((maze.w - 1) * 32 + 8, (maze.h - 1) * 32 + 8))


maze = GroupSingle(Maze(ASSETS.tileset0, randcolor(), maze_size))
draw_dots(maze.sprite)

cam = Vector2()


# Main game loop.
# -----------------------------------------------------------------------------
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
                draw_dots(maze.sprite)

    # Draw background.
    screen.fill(0)
    maze.draw(screen)

    # Update and draw sprite groups.

    # Draw UI.

    # Update screen and clock.
    pygame.display.flip()
    clock.tick(60)

pygame.quit()
