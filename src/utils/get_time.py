import pygame


def get_time() -> float:
    "Returns the time elapsed since the game started, in seconds."
    return pygame.time.get_ticks() / 1000.0
