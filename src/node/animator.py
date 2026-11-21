from .node import Node
from ..resources import Frames


class Animator(Node):
    def __init__(self) -> None:
        super().__init__()
        self.animations: dict[str, Frames] = {}
