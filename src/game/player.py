"""Score, lives and level of the current play-through."""


class Player:
    """Holds player data."""

    def __init__(self):
        self.lives = -1
        self.score = 0

    def start(self, lives: int) -> None:
        self.lives = lives
        self.score = 0

    @property
    def is_over(self) -> bool:
        """Whether all lives are lost."""
        return self.lives < 0
