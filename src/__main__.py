"""Entry point of the game, used by ``python -m src``."""

from .config import CONFIG_PATH, load_config
from .game import Game


def main() -> None:
    """Load the configuration and start the game."""
    config = load_config(CONFIG_PATH)
    Game(config).run()


if __name__ == '__main__':
    main()
