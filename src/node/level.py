import pygame
from pygame import Surface
from pygame.sprite import Sprite, AbstractGroup

from .scene import Scene
from ..game.camera import Camera


class Level(Scene):
    def __init__(self, ) -> None:
        super().__init__()

    def __draw_world_group(
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
            group: AbstractGroup[Sprite],
            screen: Surface,
            ) -> None:
        for sprite in group:
            width, height = sprite.image.get_size()
            image = pygame.transform.scale(
                sprite.image, (width * 3, height * 3))
            rect = image.get_rect(topleft=sprite.rect.topleft)
            screen.blit(image, rect)

    def enter(self) -> None:
        pass

    def exit(self) -> None:
        pass
