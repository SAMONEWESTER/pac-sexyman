"""Loading and slicing of all game graphics."""

from dataclasses import dataclass

import pygame
from pygame import Rect, Surface
from pygame import error as PygameError
from pygame.image import load
from pygame.transform import flip

from .asset_path import asset_path
from .animation import Animation
from ..errors import AssetError
from ..grid import Direction
from .sprite_tools import Frames, mirror, split_rows, fade

SHEET_COLUMNS: int = 4
"Animation frames per row in the character sprite sheets."

# Rows of pacman.png.
PAC_MAN_FRONT_ROW: int = 0
PAC_MAN_BACK_ROW: int = 1
PAC_MAN_SIDE_ROW: int = 2

# Rows of blinky.png (and of any other ghost sheet).
GHOST_BODY_ROW: int = 0
GHOST_EYES_ROW: int = 1

GHOST_NAMES: list[str] = [
    'blinky', 'pinky', 'inky', 'clyde', 'winky', 'ghost_frightened']

# Rect size templates.
RECT_8: Rect = Rect(0, 0, 8, 8)
RECT_16: Rect = Rect(0, 0, 16, 16)
RECT_32: Rect = Rect(0, 0, 32, 32)
RECT_8X16: Rect = Rect(0, 0, 8, 16)

# Font character sizes.
ALPHA_LOWER_WIDTHS: dict[str, int] = {
    'a': 8, 'b': 8, 'c': 7, 'd': 8, 'e': 8, 'f': 6, 'g': 8, 'h': 8, 'i': 4,
    'j': 6, 'k': 7, 'l': 5, 'm': 12, 'n': 8, 'o': 8, 'p': 8, 'q': 8, 'r': 7,
    's': 8, 't': 6, 'u': 8, 'v': 8, 'w': 12, 'x': 8, 'y': 8, 'z': 8,}
ALPHA_UPPER_WIDTHS: dict[str, int] = {
    'A': 9, 'B': 8, 'C': 9, 'D': 9, 'E': 8, 'F': 8, 'G': 9, 'H': 8, 'I': 6,
    'J': 8, 'K': 8, 'L': 8, 'M': 10, 'N': 9, 'O': 9, 'P': 8, 'Q': 9, 'R': 8,
    'S': 8, 'T': 8, 'U': 9, 'V': 9, 'W': 14, 'X': 9, 'Y': 8, 'Z': 8,}
PUNCTUATION_WIDTHS: dict[str, int] = {
    '.': 4, ',': 4, '!': 4, '?': 8, '-': 8}


AnimationKey = tuple[str, Direction]
AnimationDict = dict[AnimationKey, Animation]


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


class Assets:
    "Holds every image the game uses, loaded once at startup."

    def load_all(self) -> None:
        """Load all images. Requires an active display.

        Raises:
            AssetError: If an image is missing or unusable.
        """
        self.tilesets = tuple(
            self.__load_sliced('tileset/' + str(i)) for i in range(4))

        self.pac_dots = self.__load_sliced('obj/pac_dot', RECT_8)
        self.power_pellets = self.__load_sliced('obj/power_pellet', RECT_16)
        self.fruits = self.__load_sliced('obj/fruits', RECT_16)

        self.pacman = self.__load_pac_man()
        self.ghosts = self.__load_ghosts()
        self.ghost_eyes_old = self.__load_ghost_eyes()

        self.pacmanimations = [self.__build_pacmanimation(i) for i in range(4)]
        self.ghost_animations = {
            x: self.__build_ghost_animations(x) for x in GHOST_NAMES}

        # HUD.
        self.font = self.__load_font()
        self.numbers = self.__load_sliced('hud/numbers', RECT_8X16)
        self.extra_life = self.__load_sliced('hud/extra_life', RECT_16)
        self.time = self.__load_quick('hud/time')
        self.player_join_prompt = self.__load_sliced(
            'hud/player_join_prompt', Rect(0, 0, 32, 16))
        self.time_card = self.__load_quick('hud/time_card')
        self.player_card = self.__load_sliced(
            'hud/player_card', Rect(0, 0, 80, 42))

    def __build_pacmanimation(self, player: int) -> AnimationDict:
        rows = [
            [r[0], r[1], r[2], r[1], r[3]]
            for r in self.__load_rows(f'obj/pacman{player}')
        ]
        return {
            ('walk', Direction.S): Animation(rows[0], 0.25),
            ('walk', Direction.N): Animation(rows[1], 0.25),
            ('walk', Direction.E): Animation(rows[2], 0.25),
            ('walk', Direction.W): Animation(
                (flip(x, 1, 0) for x in rows[2]), 0.25),
        }

    def __build_ghost_animations(self, name: str) -> AnimationDict:
        def __join(frames: Frames, b: Surface) -> Frames:
            result = tuple(f.copy() for f in frames)
            for f in result:
                f.blit(b, (0, 0))
            return result

        rows = self.__load_rows(f'obj/ghost/{name}')
        return {
            ('walk', Direction.S): Animation(__join(rows[0], rows[1][0]), 0.25),
            ('walk', Direction.N): Animation(__join(rows[0], rows[1][1]), 0.25),
            ('walk', Direction.E): Animation(__join(rows[0], rows[1][2]), 0.25),
            ('walk', Direction.W): Animation(__join(rows[0], rows[1][3]), 0.25),
        }

    def __load_pac_man(self) -> dict[tuple[int, Direction, bool], Frames]:
        """Cut pacman.png into one animation per direction.

        Front row = moving down, back row = moving up, side row = moving
        right, mirrored side row = moving left. The ``leaning`` set tilts
        the side frames forward, for extra speed feel.
        """
        result = {}
        for i in range(4):
            rows = self.__load_rows('obj/pacman' + str(i))
            side = rows[PAC_MAN_SIDE_ROW]
            result.update({
                (i, Direction.S, False): rows[PAC_MAN_FRONT_ROW],
                (i, Direction.N, False): rows[PAC_MAN_BACK_ROW],
                (i, Direction.E, False): side,
                (i, Direction.W, False): mirror(side),
                (i, Direction.S, True): fade(rows[PAC_MAN_FRONT_ROW], 64),
                (i, Direction.N, True): fade(rows[PAC_MAN_BACK_ROW], 64),
                (i, Direction.E, True): fade(side, 64),
                (i, Direction.W, True): fade(mirror(side), 64),
            })

        return result

    def __load_ghosts(self) -> dict[str, GhostSprites]:
        "Load every ghost."
        result = {}
        for name in (
                'ghost_frightened',
                'blinky',
                'pinky',
                'inky',
                'clyde',
                'winky'):
            rows = self.__load_rows(f'obj/ghost/{name}')
            bodies = rows[GHOST_BODY_ROW]
            eyes = rows[GHOST_EYES_ROW]
            result[name] = GhostSprites(bodies, eyes)
        return result

    def __load_ghost_eyes(self) -> dict[Direction, Surface]:
        ghost_eyes = self.__load_sliced('obj/ghost/ghost_eyes', RECT_16)
        return {
            Direction.NONE: ghost_eyes[0],
            Direction.S: flip(ghost_eyes[2], False, True),
            Direction.N: ghost_eyes[2],
            Direction.E: ghost_eyes[1],
            Direction.W: flip(ghost_eyes[1], True, False),
        }

    def __load_font(self) -> dict[str, Surface]:
        "Load the font sheet and cut it into characters."
        def __load_font_row(
                widths: dict[str, int], y: int) -> dict[str, Surface]:
            result: dict[str, Surface] = {}
            x = 0
            for char, width in widths.items():
                rect = Rect(x, y, width, 16)
                result[char] = image.subsurface(rect).copy()
                x += width
            return result

        image = self.__load_quick('hud/font')
        return (
            {' ': Surface((6, 16), flags=pygame.SRCALPHA)} |
            __load_font_row(ALPHA_LOWER_WIDTHS, 0) |
            __load_font_row(ALPHA_UPPER_WIDTHS, 16) |
            __load_font_row({chr(i): 8 for i in range(48, 58)}, 32) |
            __load_font_row(PUNCTUATION_WIDTHS, 48)
        )

    def __load_rows(self, path: str) -> tuple[Frames, ...]:
        "Load a character sheet as rows of ``SHEET_COLUMNS`` frames."
        return split_rows(self.__load_sliced(path), SHEET_COLUMNS)

    def __load_quick(self, path: str) -> Surface:
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

    def __load_sliced(self, path: str, rect: Rect = RECT_32) -> Frames:
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
        image = self.__load_quick(path)
        image_rect = image.get_rect()
        if image_rect.w % rect.w or image_rect.h % rect.h:
            raise AssetError(
                f"image '{path}' is {image_rect.w}x{image_rect.h} pixels,"
                f" which does not divide into {rect.w}x{rect.h} pieces")

        result = []
        for y in range(image_rect.h // rect.h):
            for x in range(image_rect.w // rect.w):
                subrect = Rect(x * rect.w, y * rect.h, rect.w, rect.h)
                result.append(image.subsurface(subrect).copy())
        return tuple(result)


ASSETS = Assets()
