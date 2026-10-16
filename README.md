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


## Controls

| Action      | Keys          |
|-------------|---------------|
| Move        | Arrows / WASD |
| Quit        | Escape        |
| New maze    | Left click (debug) |

A pressed direction is remembered and taken at the first crossing where
it is possible, so turns can be pressed early. Pac-Man keeps moving until
a wall stops him and can reverse at any time.

Keys are bound to *actions* in `src/controls/`, so they can be rebound:

```python
controls.rebind(Action.MOVE_UP, [pygame.K_i])
```


## Gameplay tuning

Every speed, timer and distance lives in `src/config/tuning.py`
(Pac-Man speed, ghost speeds, frightened time, respawn time, hit radius,
each ghost's hunting parameters, ...).


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
|-- errors/            exceptions, logging and error reports
|-- config/            config file loading, constants and tuning
|   |-- constants.py   TILE_SIZE, FPS, ...
|   |-- tuning.py      gameplay balance: speeds, timers, ghost behaviour
|   `-- ...            settings, schema, reader, validator, loader
|-- controls/          actions and rebindable key bindings
|   |-- actions.py     Action, MOVE_DIRECTIONS
|   `-- bindings.py    Controls, DEFAULT_BINDINGS
|-- resources/         everything loaded from the assets/ folder
|   |-- assets.py      ASSETS: tiles, dots, Pac-Man and ghost sprites
|   |-- sprite_tools.py split_rows(), mirror(), rotate(), tint()
|   |-- fonts.py       FONTS
|   |-- colors.py      ghost tints, random_color()
|   `-- paths.py       file locations
|-- grid/              cells, pixel positions and directions
|-- level/             the maze and what is placed in it
|   |-- maze.py        Maze (+ walking distances for the ghosts)
|   |-- pickups.py     generate_dots(), generate_power_pellets()
|   `-- spawns.py      spawn_pac_man(), spawn_ghosts()
|-- entities/          everything that lives in a level (see below)
|   |-- entity.py      Entity (ABC)
|   |-- living/        Living (ABC), PacMan, ghosts/
|   |-- inanimate/     Inanimate, Dot, PowerUp (ABC), PowerPellet
|   `-- components/    Edible, IdleAnimation
`-- game/              window, main loop and rules
    |-- game.py        Game: events, update, draw
    |-- collisions.py  eat(), touched_ghosts()
    |-- session.py     Session: score, lives, level
    |-- hud.py         draw_hud()
    `-- window.py      create_window()
```

Every folder is a package whose `__init__.py` exposes what other packages
need, so imports stay short:

```python
from src.level import Maze, generate_dots
from src.errors import LOGGER, AssetError
```

Dependencies only point one way:
`launcher -> game -> level -> entities -> grid / resources / controls
-> config -> errors`.


## Entities

Inheritance describes what an entity **is**, composition what it **has**.

```
Entity (ABC)                 pygame Sprite, abstract update(dt, elapsed)
|-- Living (ABC)             tile-based movement; update = move, animate, place
|   |-- PacMan               player controlled, buffered turns
|   `-- Ghost (ABC)          states CHASE / FRIGHTENED / EATEN
|       |-- Blinky           hunts Pac-Man's cell
|       |-- Pinky            aims 4 cells ahead of Pac-Man
|       |-- Inky             mirrors Blinky around 2 cells ahead
|       `-- Clyde            hunts from afar, shy up close
`-- Inanimate                fixed spot, optional idle animation
    |-- Dot
    `-- PowerUp (ABC)        abstract activate(target)
        `-- PowerPellet      frightens the ghosts
```

Components:

* `Edible(points)`: every entity has an `edible` slot. Dots and power
  pellets always hold one; a ghost holds one only while frightened. This
  is why "edible" is a component and not a class in the tree: a ghost is
  `Living`, yet it can become edible.
* `IdleAnimation(style)`: the float / swing / bounce motion of dots and
  pellets.

Ghosts choose their way at every crossing by *walking* distance to their
target (a breadth-first search through the maze), never turning back
unless at a dead end. Their eyes always look at Pac-Man.


## Sprites

Character sheets are 4 columns of 32x32 frames:

* `obj/pacman.png`: row 1 front (moving down), row 2 back (up), row 3
  side (right; mirrored for left, and tilted forward while moving).
* `obj/blinky.png`: row 1 body wobble, row 2 eyes (drawn on the body).
* `obj/pinky.png`, `obj/inky.png`, `obj/clyde.png`: picked up
  automatically once added. Until then, Blinky is recolored.
