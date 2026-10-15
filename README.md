# pac-sexyman
wow that yellow guy... How can he be such a cool color of yellow!?
him be cool

## Running

```
make install
make run                      # uses config.json
make run CONFIG=other.json    # any other config file
python3 pac-man.py config.json
```


## Configuration

The config file is JSON. Lines starting with `#` are comments.
Problems never stop the game: a missing or invalid value falls back to
its default, a value out of range is clamped to the nearest limit, and
unknown keys are ignored. Every problem is printed as a warning with the
file and line, e.g.:

```
[WARNING] config.json:9: 'lives' must be between 1 and 9, got -2. Using 1.
```

If the whole file is unusable (missing, unreadable or broken JSON), the
game warns once and starts with all defaults.

| Key                       | Default             | Allowed            |
|---------------------------|---------------------|--------------------|
| `highscore_filename`      | `"highscore.txt"`   | non-empty text     |
| `level`                   | 15x10, 30x15        | non-empty list     |
| `level[].width`           | 15                  | 14 to 50           |
| `level[].height`          | 10                  | 10 to 30           |
| `lives`                   | 3                   | 1 to 9             |
| `pacgum`                  | 42                  | 0 to 1000          |
| `points_per_pacgum`       | 10                  | 0 to 100000        |
| `points_per_super_pacgum` | 50                  | 0 to 100000        |
| `points_per_ghost`        | 200                 | 0 to 100000        |
| `seed`                    | 42                  | 0 to 2147483647    |
| `level_max_time`          | 90 (seconds)        | 10 to 3600         |

14x10 is the smallest maze that still fits the 42 pattern. All rules
live in `src/config/schema.py`.


## Error handling

* Every error the game raises on purpose is a subclass of
  `PacManError` (`src/errors/exceptions.py`): `UsageError`,
  `ConfigError`, `AssetError`, `DisplayError`, `MazeError`.
* `main()` in `src/launcher/main.py` is the only place that catches
  errors for the whole program. Python tracebacks never reach the
  player; instead a short report shows the cause and where in `src/`
  it happened:

  ```
  [ERROR] AssetError: cannot load image 'assets/gfx/obj/pac_dot.png'
    caused by FileNotFoundError: No file 'assets/gfx/obj/pac_dot.png' found ...
    at src/resources/assets.py:55 in _load_quick
    at src/resources/assets.py:37 in load_all
    at src/game/game.py:30 in __init__
    at src/launcher/main.py:29 in main
  ```

* Errors that are not a `PacManError` are reported the same way, marked
  as a bug.
* Warnings and errors go to the terminal; everything (including info
  messages such as ignored config keys) also goes to `pac-man.log`,
  which is rewritten on every run.
* Exit codes: `0` normal, `1` error, `130` Ctrl+C.


## Project structure

```
pac-man.py             launcher: python3 pac-man.py config.json
src/
|-- __main__.py        same launcher for: python -m src config.json
|-- launcher/          command line + the top-level error catcher
|   |-- cli.py         parse_args(): exactly one config file argument
|   `-- main.py        main(): runs the game, turns errors into messages
|-- errors/            exceptions, logging and error reports
|   |-- exceptions.py  PacManError and its subclasses
|   |-- logger.py      LOGGER, setup_logging()
|   `-- reporting.py   format_error(), report_error()
|-- config/            config file loading + fixed constants
|   |-- constants.py   TILE_SIZE, FPS, ...
|   |-- settings.py    Config, LevelConfig: the validated settings
|   |-- schema.py      defaults and allowed ranges of every key
|   |-- reader.py      reads the file, strips comments, parses JSON
|   |-- validator.py   repairs bad values, warns with file:line
|   `-- loader.py      load_config(): ties the three above together
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
from src.errors import LOGGER, AssetError
```

Dependencies only point one way:
`launcher -> game -> level -> entities -> resources -> config -> errors`.
