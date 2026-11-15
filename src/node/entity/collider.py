from pygame import Rect

from .entity import Entity


class Collider(Entity):
    def __init__(self, rect: Rect):
        super().__init__()
        self.rect = rect.copy()

    @property
    def global_rect(self) -> Rect:
        return self.rect.move(self.position)

    def collides_with(self, other: "Collider") -> bool:
        return self.global_rect.colliderect(other.global_rect)
