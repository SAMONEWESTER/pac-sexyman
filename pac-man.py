"""Start the game: ``python3 pac-man.py config.json``."""

import sys

from src.launcher import main

if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
