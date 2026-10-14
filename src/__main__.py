from random import randint
import json

from .maze import Maze

import pygame
from pygame import image, Color, Vector2
from pygame.sprite import Group, GroupSingle


pygame.init()


def randcolor() -> pygame.Color:
    return pygame.Color(randint(64, 255), randint(64, 255), randint(64, 255))


# Load the config with all comments discarded.
# ------------------------------------------------------------------------------
with open('config.json') as f:
    config = json.loads(
        ''.join(x for x in f.readlines() if not x.strip().startswith('#')))
print(config)


# Setup program.
# ------------------------------------------------------------------------------
maze_size = (config['level'][0]['width'], config['level'][0]['height'])
w, h = maze_size[0] * 32, maze_size[1] * 32
pygame.display.set_icon(image.load('assets/power_pellet.png'))

screen = pygame.display.set_mode((w, h), pygame.FULLSCREEN | pygame.SCALED)
pygame.display.set_caption('pac-man')
clock = pygame.time.Clock()

tiles = [image.load(f'assets/tiles/{x}.png').convert_alpha() for x in range(16)]
pacdot = image.load('assets/pac_dot.png').convert_alpha()
powerpellet = image.load('assets/power_pellet.png').convert_alpha()

maze = GroupSingle(Maze(tiles, randcolor(), maze_size))


def draw_dots(maze: Maze) -> None:
    # FAKE PAC-DOTS AND POWER PELLETS! JUST FOR SHOW, NOT ACTUAL OBJECTS!
    # Later, we can place them in the same positions as actual objects.
    for y, row in enumerate(maze.maze):
        for x, cell in enumerate(row):
            if cell != 15:
                maze.image.blit(pacdot, (x * 32 + 8, y * 32 + 8))
            if not (cell & 2):
                maze.image.blit(pacdot, (x * 32 + 24, y * 32 + 8))
            if not (cell & 4):
                maze.image.blit(pacdot, (x * 32 + 8, y * 32 + 24))
    maze.image.blit(powerpellet, (8, 8))
    maze.image.blit(powerpellet, ((maze.w - 1) * 32 + 8, 8))
    maze.image.blit(powerpellet, (8, (maze.h - 1) * 32 + 8))
    maze.image.blit(powerpellet, ((maze.w - 1) * 32 + 8, (maze.h - 1) * 32 + 8))


cam = Vector2()


# Main game loop.
# ------------------------------------------------------------------------------
running = True
while running:
    # Handle events.
    for event in pygame.event.get():
        keys = pygame.key.get_pressed()
        if event.type == pygame.QUIT or keys[pygame.K_ESCAPE]:
            running = False
        if event.type == pygame.MOUSEBUTTONDOWN:
            if pygame.mouse.get_pressed()[0]:
                maze.add(Maze(tiles, randcolor(), maze_size))

    # Draw background.
    screen.fill(0)
    maze.draw(screen)

    # Update and draw sprite groups.

    # Draw UI.

    # Update screen and clock.
    pygame.display.flip()
    clock.tick(60)

pygame.quit()