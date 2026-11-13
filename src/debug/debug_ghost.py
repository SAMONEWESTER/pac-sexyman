import pygame
from pygame import Color, Surface, Vector2

from src.game.camera import Camera
from ..entities import Ghost


class DebugGhost:
    def __init__(self, ghost: Ghost):
        self.ghost = ghost
        match ghost.NAME:
            case "blinky":
                self.color = Color(255, 64, 87)
            case "pinky":
                self.color = Color(255, 131, 200)
            case "inky":
                self.color = Color(50, 216, 242)
            case "clyde":
                self.color = Color(255, 155, 69)
            case "winky":
                self.color = Color(134, 101, 218)

    def draw(self, screen: Surface, camera: Camera) -> None:
        start = camera.point(self.ghost.rect.center)
        end = camera.point(Vector2(self.ghost.target) * 32 + Vector2(16, 16))

        pygame.draw.line(
            screen,
            (0, 0, 0),
            start,
            end,
            12
        )
        pygame.draw.circle(
            screen,
            (0, 0, 0),
            end,
            20,
            0
        )
        pygame.draw.line(
            screen,
            self.color,
            start,
            end,
            4
        )
        pygame.draw.circle(
            screen,
            self.color,
            end,
            16,
            0
        )
