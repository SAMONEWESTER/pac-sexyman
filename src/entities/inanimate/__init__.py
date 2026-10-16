"""Entities that stay where they are placed: dots and power-ups."""

from .dot import Dot
from .inanimate import Inanimate
from .power_pellet import PowerPellet
from .power_up import PowerUp, PowerUpTarget

__all__ = ['Dot', 'Inanimate', 'PowerPellet', 'PowerUp', 'PowerUpTarget']
