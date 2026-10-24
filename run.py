"""Start the game: ``python3 pac-man.py config.json``."""

import runpy

runpy.run_module("src", run_name="__main__", alter_sys=True)
