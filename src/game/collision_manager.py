from ..node.entity.collider import Collider


class CollisionManager:
    def __init__(self) -> None:
        self.colliders: set[Collider] = set()

    def register(self, collider: Collider) -> None:
        self.colliders.add(collider)

    def unregister(self, collider: Collider) -> None:
        self.colliders.discard(collider)

    def update(self) -> None:
        colliders = tuple(self.colliders)
        collisions: list[tuple[Collider, Collider]] = []
        for i, a in enumerate(colliders):
            if not a.active:
                continue
            for b in colliders[i + 1:]:
                if not b.active or a.owner is b.owner:
                    continue
                if not (a.mask & b.layer and b.mask & a.layer):
                    continue

                if a.rect.colliderect(b.rect):
                    collisions.append((a, b))

        for a, b in collisions:
            print(f"Collision detected between {a.owner} and {b.owner}")
            a.owner.on_collision(b.owner)
            b.owner.on_collision(a.owner)
