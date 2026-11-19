from collections import defaultdict

from ..node.entity.collider import Collider


class CollisionManager:
    def __init__(self) -> None:
        self.colliders: set[Collider] = set()

    def register(self, collider: Collider) -> None:
        self.colliders.add(collider)

    def unregister(self, collider: Collider) -> None:
        self.colliders.discard(collider)

    def update(self):
        grid: defaultdict[tuple[int, int], list[Collider]] = defaultdict(list)

        # Assign colliders to grid cells
        for collider in self.colliders:
            if not collider.active:
                continue

            rect = collider.rect

            left = rect.left // 32
            right = (rect.right - 1) // 32
            top = rect.top // 32
            bottom = (rect.bottom - 1) // 32

            for x in range(left, right + 1):
                for y in range(top, bottom + 1):
                    grid[(x, y)].append(collider)

        # Only check objects sharing a cell
        collisions = set()

        for cell_colliders in grid.values():
            for i in range(len(cell_colliders)):
                a = cell_colliders[i]
                for b in cell_colliders[i + 1:]:
                    if a.owner is b.owner:
                        continue

                    if not (a.mask & b.layer and b.mask & a.layer):
                        continue

                    pair = (a, b) if id(a) < id(b) else (b, a)

                    if pair in collisions:
                        continue

                    if a.rect.colliderect(b.rect):
                        collisions.add(pair)

        for a, b in collisions:
            print(f"Collision detected between {a.owner} and {b.owner}")
            a.owner.on_collision(b.owner)
            b.owner.on_collision(a.owner)
