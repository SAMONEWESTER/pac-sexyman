"""Entry point for ``python -m src config.json``."""

from sys import argv, exit

import pygame

from .config import load_config
from .errors import LOGGER, report_error, setup_logging
from .game import Game

EXIT_INTERRUPTED: int = 130


setup_logging()

if len(argv) > 1:
    path = argv[1]
    if not path.lower().endswith('.json'):
        LOGGER.warning("'%s' does not end in .json, reading it anyway.", path)
else:
    path = ""
try:
    config = load_config(path)
    Game(config).run()
except KeyboardInterrupt:
    LOGGER.info('interrupted with Ctrl+C')
    exit(EXIT_INTERRUPTED)
except Exception as error:
    report_error(error)
    exit(1)
finally:
    pygame.quit()
