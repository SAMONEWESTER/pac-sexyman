"""Which keys trigger which action, changeable at runtime."""

from collections.abc import Iterable, Mapping

import pygame

from .actions import Action

DEFAULT_BINDINGS: Mapping[Action, tuple[int, ...]] = {
    Action.MOVE_UP: (pygame.K_UP, pygame.K_w),
    Action.MOVE_DOWN: (pygame.K_DOWN, pygame.K_s),
    Action.MOVE_LEFT: (pygame.K_LEFT, pygame.K_a),
    Action.MOVE_RIGHT: (pygame.K_RIGHT, pygame.K_d),
    Action.QUIT: (pygame.K_ESCAPE,),
}
"""Arrow keys and WASD to move, Escape to quit."""


class Controls:
    """Maps actions to keys. Every action can have several keys.

    Example::

        controls = Controls()
        controls.rebind(Action.MOVE_UP, [pygame.K_i])
        controls.action_for(pygame.K_i)   # -> Action.MOVE_UP

    Args:
        bindings: Starting keys per action, ``DEFAULT_BINDINGS`` if omitted.
    """

    def __init__(
            self,
            bindings: Mapping[Action, Iterable[int]] = DEFAULT_BINDINGS,
            ) -> None:
        self._keys: dict[Action, tuple[int, ...]] = {
            action: tuple(keys) for action, keys in bindings.items()}

    def keys_for(self, action: Action) -> tuple[int, ...]:
        """Return the keys bound to an action (empty if none)."""
        return self._keys.get(action, ())

    def action_for(self, key: int) -> Action | None:
        """Return the action a key triggers, or ``None`` if unbound."""
        for action, keys in self._keys.items():
            if key in keys:
                return action
        return None

    def rebind(self, action: Action, keys: Iterable[int]) -> None:
        """Replace the keys of an action.

        A key can only trigger one action, so the new keys are removed
        from every other action first.

        Args:
            action: The action to change.
            keys: The new keys (``pygame.K_...`` constants).
        """
        new_keys = tuple(keys)
        for other, old_keys in self._keys.items():
            self._keys[other] = tuple(k for k in old_keys if k not in new_keys)
        self._keys[action] = new_keys

    def reset(self) -> None:
        """Go back to the default keys."""
        self._keys = {
            action: tuple(keys) for action, keys in DEFAULT_BINDINGS.items()}
