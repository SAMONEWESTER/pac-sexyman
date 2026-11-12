"""The game over screen: the global top scores of this ruleset."""

from __future__ import annotations

from pygame import SRCALPHA, Rect, Surface
from pygame.draw import rect as draw_rect
from pygame.font import Font
from pygame.sprite import Sprite
from pygame.transform import scale

from ...leaderboard import Leaderboard, LeaderboardStatus, ScoreEntry
from ...resources import FONTS

WIDTH: int = 380
"""Panel width before scaling, in pixels."""

PADDING: int = 18
"""Space between the panel border and its text, in pixels."""

TITLE_HEIGHT: int = 46
"""Space taken by the GAME OVER title, in pixels."""

LINE_HEIGHT: int = 24
"""Space taken by one line of regular text, scores included."""

GAP: int = 12
"""Extra space between the scores and the lines around them."""

BASE_SCREEN_HEIGHT: int = 400
"""Screen height at which the panel is drawn 1:1; it scales in steps."""

WHITE = (255, 255, 255)
GREY = (150, 150, 170)
YELLOW = (255, 221, 0)
BLUE = (33, 33, 222)
BACKGROUND = (0, 0, 16, 240)

Key = tuple[tuple[ScoreEntry, ...], LeaderboardStatus, int, bool]


class LeaderboardPanel(Sprite):
    """Shows the leaderboard in the middle of the screen.

    Scores submitted this session are drawn in yellow.

    Args:
        leaderboard: Where the scores come from.
        screen_size: Size of the window, to center and scale the panel.
    """

    def __init__(
            self,
            leaderboard: Leaderboard,
            screen_size: tuple[int, int],
            ) -> None:
        super().__init__()
        self.leaderboard = leaderboard
        self.screen_size = screen_size
        self.zoom = max(1, screen_size[1] // BASE_SCREEN_HEIGHT)
        self.image = Surface((1, 1), SRCALPHA)
        self.rect = self.image.get_rect()
        self._last_key: Key | None = None

    def update(self, seconds_left: float, can_skip: bool) -> None:
        """Redraw when the scores, status or countdown changed.

        Args:
            seconds_left: Time until the next game starts by itself.
            can_skip: Whether a confirm key may start it right away.
        """
        board = self.leaderboard
        key: Key = (board.entries, board.status, int(seconds_left), can_skip)
        if key == self._last_key:
            return
        self._last_key = key

        panel = self._draw(*key)
        width, height = panel.get_size()
        self.image = scale(panel, (width * self.zoom, height * self.zoom))
        self.rect = self.image.get_rect(
            center=(self.screen_size[0] // 2, self.screen_size[1] // 2))

    # Drawing.
    # --------------------------------------------------------------------------
    def _draw(
            self,
            entries: tuple[ScoreEntry, ...],
            status: LeaderboardStatus,
            seconds_left: int,
            can_skip: bool,
            ) -> Surface:
        board = self.leaderboard
        note = _status_note(status, board.ranked, bool(entries))
        lines = max(len(entries), 1) + 2 + int(bool(note))
        height = PADDING * 2 + TITLE_HEIGHT + GAP * 2 + lines * LINE_HEIGHT
        panel = Surface((WIDTH, height), SRCALPHA)
        panel.fill(BACKGROUND)
        draw_rect(panel, BLUE, Rect(0, 0, WIDTH, height), width=2)

        y = PADDING
        self._text(panel, FONTS.big, 'GAME OVER', YELLOW, y, center=True)
        y += TITLE_HEIGHT
        self._text(panel, FONTS.regular, 'GLOBAL TOP SCORES', GREY, y,
                   center=True)
        y += LINE_HEIGHT + GAP

        if not entries:
            self._text(panel, FONTS.regular, _empty_text(status, board.ranked),
                       WHITE, y, center=True)
            y += LINE_HEIGHT
        for rank, entry in enumerate(entries, start=1):
            color = YELLOW if board.is_own(entry) else WHITE
            self._row(panel, rank, entry, color, y)
            y += LINE_HEIGHT
        y += GAP

        if note:
            self._text(panel, FONTS.regular, note, GREY, y, center=True)
            y += LINE_HEIGHT

        if can_skip:
            prompt = f'PRESS CONFIRM TO PLAY ({seconds_left + 1})'
        else:
            prompt = f'NEXT GAME IN {seconds_left + 1}'
        self._text(panel, FONTS.regular, prompt, WHITE, y, center=True)
        return panel

    def _row(
            self,
            panel: Surface,
            rank: int,
            entry: ScoreEntry,
            color: tuple[int, int, int],
            y: int,
            ) -> None:
        font = FONTS.regular
        self._text(panel, font, f'{rank}.', GREY, y, right=PADDING + 28)
        self._text(panel, font, entry.name, color, y, x=PADDING + 40)
        self._text(panel, font, f'LV {entry.level}', GREY, y,
                   right=WIDTH - PADDING)
        self._text(panel, font, f'{entry.score:,}', color, y,
                   right=WIDTH - PADDING - 72)

    @staticmethod
    def _text(
            panel: Surface,
            font: Font,
            text: str,
            color: tuple[int, int, int],
            y: int,
            *,
            x: int = 0,
            right: int | None = None,
            center: bool = False,
            ) -> None:
        """Draw one line of text, left aligned unless told otherwise."""
        image = font.render(text, False, color)
        if center:
            x = (panel.get_width() - image.get_width()) // 2
        elif right is not None:
            x = right - image.get_width()
        panel.blit(image, (x, y))


def _empty_text(status: LeaderboardStatus, ranked: bool) -> str:
    """What to show in place of the scores when there are none."""
    if status is LeaderboardStatus.DISABLED:
        return 'ONLINE LEADERBOARD IS OFF'
    if status is LeaderboardStatus.LOADING:
        return 'LOADING...'
    if status is LeaderboardStatus.OFFLINE:
        return 'CANNOT REACH THE LEADERBOARD'
    return 'NO SCORES YET. BE THE FIRST!' if ranked else 'NO SCORES YET'


def _status_note(
        status: LeaderboardStatus,
        ranked: bool,
        has_entries: bool,
        ) -> str:
    """A short line under the scores, empty when all is well."""
    if status is LeaderboardStatus.DISABLED:
        return ''
    if not ranked:
        return 'CHEATS ON: SCORES ARE NOT SAVED'
    if status is LeaderboardStatus.OFFLINE and has_entries:
        return 'OFFLINE: SHOWING OLDER SCORES'
    return ''
