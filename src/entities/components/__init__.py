"""Small parts an entity can hold, for behaviour that crosses the tree.

An entity *is* a Living or an Inanimate (inheritance), but it *has*
an Edible or an IdleAnimation (composition).
"""

from .edible import Edible
from .idle_animation import IdleAnimation, IdleStyle

__all__ = ['Edible', 'IdleAnimation', 'IdleStyle']
