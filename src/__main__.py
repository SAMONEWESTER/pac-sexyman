"""Entry point for ``python -m src config.json``."""

import sys

from .launcher import main

if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
