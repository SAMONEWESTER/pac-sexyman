from enum import IntFlag, auto

from pygame import Rect, Vector2, SRCALPHA, Surface

from .entity import Entity
from .sprite.world_sprite import WorldSprite


class CollisionLayer(IntFlag):
    """Collision layers for entities,
    used to determine which entities can collide with each other.
    """
    NONE = 0
    PACMAN = auto()
    GHOST = auto()
    ITEM = auto()

    # Entity          Layer     Mask
    # ------------------------------------
    # Pacman          PACMAN    GHOST,ITEM
    # Ghost           GHOST     PACMAN
    # Dot             ITEM      PACMAN
    # Power pellet    ITEM      PACMAN


class Collider(Entity):
    """Collider for an entity, used to detect collisions with other entities.

    Parameters
    ----------
    size: Vector2
        Size of the collider, in pixels.
    """
    def __init__(self, size: Vector2) -> None:
        super().__init__()
        self.size = size
        "Size of the collider, in pixels."
        self.layer = CollisionLayer.NONE
        "Which layer this collider belongs to."
        self.mask = CollisionLayer.NONE
        "Which layers this collider collides with."

        debug_img = Surface((size.x, size.y), flags=SRCALPHA)
        debug_img.fill((255, 255, 0, 128))
        self.add_child(WorldSprite(debug_img))

    @property
    def rect(self) -> Rect:
        "The rectangle of the collider, in world coordinates."
        return Rect(self.position, self.size)

    def _on_enter_tree(self):
        print('3')
        print(f'\033[2mIn _on_enter_tree, my parent is {self.parent}\033[0m')
        print(f'\033[2mIn _on_enter_tree, my parent\'s parent is {self.parent.parent}\033[0m')
        print(f'\033[2mIn _on_enter_tree, my root is {self.root}\033[0m')
        self.root.collision_manager.register(self)
        print('4')
        for child in self.children:
            child._on_enter_tree()

    def _on_exit_tree(self):
        self.root.collision_manager.unregister(self)
        for child in self.children:
            child._on_exit_tree()
