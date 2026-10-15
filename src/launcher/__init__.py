"""Starting the game from the command line."""

from .cli import USAGE, parse_args
from .main import main

__all__ = ['USAGE', 'main', 'parse_args']
