from random import randint
import json

from mazegenerator import MazeGenerator

import pygame
from pygame import image, Surface, Rect, Vector2


pygame.init()

# Load the config with all comments discarded.
# ------------------------------------------------------------------------------
with open('config.json') as f:
    config = json.loads(
        ''.join(x for x in f.readlines() if not x.strip().startswith('#')))
print(config)


# Setup program.
# ------------------------------------------------------------------------------
maze_size = (25, 15)

maze = MazeGenerator(tuple(maze_size))
w, h = maze_size[0] * 32, maze_size[1] * 32
pygame.display.set_icon(image.load('assets/power_pellet.png'))

screen = pygame.display.set_mode((w, h), pygame.FULLSCREEN | pygame.SCALED)
pygame.display.set_caption('pac-man')
clock = pygame.time.Clock()

tiles = [image.load(f'assets/tiles/{x}.png').convert_alpha() for x in range(16)]
pacdot = image.load(f'assets/pac_dot.png').convert_alpha()
powerpellet = image.load(f'assets/power_pellet.png').convert_alpha()


def draw_maze(maze: MazeGenerator) -> tuple[Surface, Rect]:
    bg = Surface((maze._width * 32, maze._height * 32))
    bg_rect = bg.get_rect()

    for y, row in enumerate(maze.maze):
        for x, cell in enumerate(row):
            bg.blit(tiles[cell], (x * 32, y * 32))
    bg.fill(
        pygame.Color(randint(32, 255), randint(32, 255), randint(32, 255)),
        special_flags=pygame.BLEND_MULT)
    # FAKE PAC-DOTS AND POWER PELLETS! JUST FOR SHOW, NOT ACTUAL OBJECTS!
    # Later, we can place them in the same positions as actual objects.
    for y, row in enumerate(maze.maze):
        for x, cell in enumerate(row):
            if cell != 15:
                bg.blit(pacdot, (x * 32 + 8, y * 32 + 8))
            if not (cell & 2):
                bg.blit(pacdot, (x * 32 + 24, y * 32 + 8))
            if not (cell & 4):
                bg.blit(pacdot, (x * 32 + 8, y * 32 + 24))
    bg.blit(powerpellet, (8, 8))
    bg.blit(powerpellet, ((maze_size[0] - 1) * 32 + 8, 8))
    bg.blit(powerpellet, (8, (maze_size[1] - 1) * 32 + 8))
    bg.blit(powerpellet, ((maze_size[0] - 1) * 32 + 8, (maze_size[1] - 1) * 32 + 8))
    return (bg, bg_rect)


bg, bg_rect = draw_maze(maze)
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
                bg, bg_rect = draw_maze(maze := MazeGenerator(maze_size))

    # Draw background.
    screen.fill(0)
    screen.blit(bg, bg_rect.move(cam))

    # Update and draw sprite groups.

    # Draw UI.

    # Update screen and clock.
    pygame.display.flip()
    clock.tick(60)

pygame.quit()