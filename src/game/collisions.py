"""Who touches whom: Pac-Man against dots, pellets and ghosts."""

from __future__ import annotations

from collections.abc import Callable
from typing import TypeVar

from pygame import Vector2
from pygame.sprite import Group, spritecollide

from ..config import tuning
from ..entities import Entity, Ghost, GhostState, PacMan

EntityT = TypeVar('EntityT', bound=Entity)


def within(radius: float) -> Callable[[Entity, Entity], bool]:
    """Make a collision test: are two entities' centers this close?

    Args:
        radius: Maximum distance between the centers, in pixels.
    """
    def test(a: Entity, b: Entity) -> bool:
        return Vector2(a.rect.center).distance_to(b.rect.center) < radius
    return test


def eat(pac_man: PacMan, group: Group[EntityT]) -> list[EntityT]:
    """Remove and return every edible entity Pac-Man is touching.

    Args:
        pac_man: The eater.
        group: Dots or power pellets.
    """
    touched = spritecollide(pac_man, group, False,
                            within(tuning.EAT_RADIUS))
    eaten = [entity for entity in touched if entity.is_edible]
    for entity in eaten:
        entity.kill()
    return eaten


def touched_ghosts(pac_man: PacMan, ghosts: Group[Ghost]) -> list[Ghost]:
    """Return the ghosts touching Pac-Man (eaten ghosts don't count).

    Args:
        pac_man: Pac-Man.
        ghosts: All ghosts.
    """
    touched = spritecollide(pac_man, ghosts, False,
                            within(tuning.GHOST_HIT_RADIUS))
    return [ghost for ghost in touched if ghost.state is not GhostState.EATEN]


def points(entity: Entity) -> int:
    """Score for eating an entity, 0 if it is not edible."""
    return entity.edible.points if entity.edible is not None else 0
