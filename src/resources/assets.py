"""Loading and slicing of all game graphics."""

import sys
from pathlib import Path
from dataclasses import dataclass

from pygame import Rect, Surface
from pygame import error as PygameError
from pygame.image import load
from pygame.transform import flip

from ..config import TILE_SIZE
from ..errors import AssetError
from ..grid import Direction
from .sprite_tools import Frames, mirror, split_rows

FRUIT_SIZE: int = 16
"""Width and height of one fruit in the fruit sheet, in pixels."""

PICKUP_SIZE: int = 16
"""Width and height of the dot and power pellet images, in pixels."""

TILE_VARIANTS: int = 16
"""Tiles a tileset needs: one for every combination of 4 walls."""

SHEET_COLUMNS: int = 4
"""Animation frames per row in the character sprite sheets."""

# Rows of pacman.png.
PAC_MAN_FRONT_ROW: int = 0
PAC_MAN_BACK_ROW: int = 1
PAC_MAN_SIDE_ROW: int = 2

# Rows of blinky.png (and of any other ghost sheet).
GHOST_BODY_ROW: int = 0
GHOST_EYES_ROW: int = 1


@dataclass(frozen=True)
class GhostSprites:
    """All frames of one ghost.

    Attributes:
        bodies: Body wobble animation.
        eyes: Eye frames, drawn on top of the body.
        eyes_mirrored: The same eye frames, flipped horizontally.
    """

    bodies: Frames
    eyes: Frames
    eyes_mirrored: Frames


def asset_path(relative_path: Path) -> str:
    if getattr(sys, "frozen", False):
        base_path = Path(sys._MEIPASS)
    else:
        base_path = Path(__file__).resolve().parents[2]

    return str(base_path / 'assets' / relative_path)


class Assets:
    """Holds every image the game uses, loaded once at startup."""

    def load_all(self) -> None:
        """Load all images. Requires an active display.

        Raises:
            AssetError: If an image is missing or unusable.
        """
        self.tilesets = [self._load_sliced('tileset/0')]
        self.tilesets.append(self._load_sliced('tileset/1'))
        for i, tileset in enumerate(self.tilesets):
            if len(tileset) < TILE_VARIANTS:
                raise AssetError(
                    f"tileset {i} has {len(tileset)} tiles, "
                    f'needs at least {TILE_VARIANTS}')
        self.pac_dots = self._load_sliced('obj/pac_dot', 8)
        self.power_pellets = self._load_sliced('obj/power_pellet', 16)
        self.fruits = self._load_sliced('obj/fruits', FRUIT_SIZE)
        self._load_pac_man()
        self._load_ghosts()

    def _load_pac_man(self) -> None:
        """Cut pacman.png into one animation per direction.

        Front row = moving down, back row = moving up, side row = moving
        right, mirrored side row = moving left. The ``leaning`` set tilts
        the side frames forward, for extra speed feel.
        """
        rows = self._load_rows('obj/pacman')
        side = rows[PAC_MAN_SIDE_ROW]
        rows2 = self._load_rows('obj/pacman2')
        side2 = rows2[PAC_MAN_SIDE_ROW]
        self.pac_man = {
            (0, Direction.DOWN): rows[PAC_MAN_FRONT_ROW],
            (0, Direction.UP): rows[PAC_MAN_BACK_ROW],
            (0, Direction.RIGHT): side,
            (0, Direction.LEFT): mirror(side),
            (1, Direction.DOWN): rows2[PAC_MAN_FRONT_ROW],
            (1, Direction.UP): rows2[PAC_MAN_BACK_ROW],
            (1, Direction.RIGHT): side2,
            (1, Direction.LEFT): mirror(side2),
        }

    def _load_ghosts(self) -> None:
        """Load every ghost."""
        self.ghosts: dict[str, GhostSprites] = {}
        for name in ('ghost_frightened', 'blinky', 'pinky', 'inky', 'clyde'):
            rows = self._load_rows(f'obj/{name}')
            bodies = rows[GHOST_BODY_ROW]
            eyes = rows[GHOST_EYES_ROW]
            self.ghosts[name] = GhostSprites(bodies, eyes, mirror(eyes))
        ghost_eyes = self._load_sliced('obj/ghost_eyes', 16)
        self.ghost_eyes = {
            Direction.NONE: ghost_eyes[0],
            Direction.DOWN: flip(ghost_eyes[2], False, True),
            Direction.UP: ghost_eyes[2],
            Direction.RIGHT: ghost_eyes[1],
            Direction.LEFT: flip(ghost_eyes[1], True, False),
        }

    def _load_rows(self, path: str) -> tuple[Frames, ...]:
        """Load a character sheet as rows of ``SHEET_COLUMNS`` frames."""
        return split_rows(self._load_sliced(path), SHEET_COLUMNS)

    def _load_quick(self, path: str) -> Surface:
        """Load one PNG from the graphics folder, keeping transparency.

        Args:
            path: Image path inside ``assets/gfx``, without extension.

        Raises:
            AssetError: If the file is missing or not a readable image.
        """
        file = asset_path(f'gfx/{path}.png')
        try:
            return load(file).convert_alpha()
        except (PygameError, OSError) as err:
            raise AssetError(
                f"cannot load image '{file}'") from err

    def _load_sliced(self, path: str, size: int = TILE_SIZE) -> Frames:
        """Load a sprite sheet and cut it into square pieces.

        Args:
            path: Image path inside ``assets/gfx``, without extension.
            size: Width and height of one piece, in pixels.

        Returns:
            The pieces, left to right and top to bottom.

        Raises:
            AssetError: If the image cannot be loaded or does not divide
                evenly into ``size`` by ``size`` pieces.
        """
        image = self._load_quick(path)
        rect = image.get_rect()
        if rect.w % size or rect.h % size:
            raise AssetError(
                f"image '{path}' is {rect.w}x{rect.h} pixels, which does "
                f'not divide into {size}x{size} pieces')

        result = []
        for y in range(rect.h // size):
            for x in range(rect.w // size):
                subrect = Rect(x * size, y * size, size, size)
                result.append(image.subsurface(subrect).copy())
        return tuple(result)


ASSETS = Assets()
