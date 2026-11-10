"""Score, lives and level of the current play-through."""


class Player:
    """Holds player data."""

    def __init__(self) -> None:
        self.lives = -1
        self.score = -1
        self.continues = -1

    def start(self, lives: int) -> None:
        self.lives = lives
        self.score = 0
        self.continues += 1

    @property
    def is_over(self) -> bool:
        """Whether all lives are lost."""
        return self.lives < 0

    def add_points(self, points: int) -> bool:
        """Add to the score, with an extra life every 10,000 points.

        Returns:
            Whether an extra life was earned.
        """
        earned_life = self.score // 10_000 < (self.score + points) // 10_000
        if earned_life:
            self.add_life()
        self.score += points
        return earned_life

    def add_life(self) -> None:
        self.lives += 1
