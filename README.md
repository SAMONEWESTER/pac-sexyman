# pac-sexyman
wow that yellow guy... How can he be such a cool color of yellow!?
him be cool

## Project structure

```
src/
|-- __main__.py        entry point: loads the config and starts the Game
|-- config/            config.json loading + fixed constants (TILE_SIZE, FPS)
|   |-- constants.py
|   `-- loader.py      load_config()
|-- resources/         everything loaded from the assets/ folder
|   |-- paths.py       file locations (ASSETS_DIR, ICON_PATH, ...)
|   |-- assets.py      ASSETS: images and sliced sprite sheets
|   |-- fonts.py       FONTS: game fonts
|   `-- colors.py      random_color()
|-- level/             what a level is made of
|   |-- maze.py        Maze: wraps the external mazegenerator package
|   `-- dots.py        generate_dots(): places pac-dots in a maze
|-- entities/          sprites that live inside a level
|   `-- pac_dot.py     PacDot
`-- game/              window + main loop
    |-- window.py      create_window()
    `-- game.py        Game: events, update, draw
```

Every folder is a package whose `__init__.py` exposes what other packages
need, so imports stay short:

```python
from src.level import Maze, generate_dots
from src.resources import ASSETS
```

Dependencies only point one way:
`game -> level -> entities -> resources -> config`.
