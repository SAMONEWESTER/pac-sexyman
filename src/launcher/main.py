"""The one place where every error ends up as a clean message."""

from collections.abc import Sequence

import pygame

from ..config import load_config
from ..errors import LOGGER, report_error, setup_logging
from ..game import Game
from .cli import parse_args

EXIT_OK: int = 0
EXIT_ERROR: int = 1
EXIT_INTERRUPTED: int = 130


def main(argv: Sequence[str]) -> int:
    """Run the game; never let a Python traceback reach the player.

    Args:
        argv: Command-line arguments, without the program name.

    Returns:
        The exit code: 0 on success, 1 on error, 130 on Ctrl+C.
    """
    setup_logging()
    try:
        config = load_config(parse_args(argv))
        Game(config).run()
    except KeyboardInterrupt:
        LOGGER.info('interrupted with Ctrl+C')
        return EXIT_INTERRUPTED
    except Exception as error:
        report_error(error)
        return EXIT_ERROR
    finally:
        pygame.quit()
    return EXIT_OK
