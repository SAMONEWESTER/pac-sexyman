"""The component that makes an entity edible for Pac-Man."""

from dataclasses import dataclass


@dataclass(frozen=True)
class Edible:
    """Marks an entity as edible and says what eating it is worth.

    Any entity can hold one in its ``edible`` slot: dots and power
    pellets always do, a ghost only while it is frightened.

    Attributes:
        points: Score Pac-Man gets for eating the entity.
    """

    points: int
