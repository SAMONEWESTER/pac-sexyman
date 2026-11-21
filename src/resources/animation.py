from typing import Iterable, Iterator

from pygame import Surface
from ..utils.get_time import get_time


class Animation:
    def __init__(
            self,
            frames: Iterable[Surface],
            duration: float = 1.0,
            loop: bool = True
            ) -> None:
        self.frames: tuple[Surface, ...] = tuple(frames)
        self.duration = duration
        self.loop = loop

        if not self.frames:
            raise ValueError("Animation must contain at least one frame.")
        if duration <= 0:
            raise ValueError("Duration must be greater than zero.")

        self.length = len(self.frames)

        self.playing = True
        self._start_time = get_time()
        self._paused_elapsed = 0.0

    def play(self) -> None:
        if self.playing:
            return

        self._start_time = get_time() - self._paused_elapsed
        self.playing = True

    def pause(self) -> None:
        if not self.playing:
            return

        self._paused_elapsed = get_time() - self._start_time
        self.playing = False

    def stop(self) -> None:
        self.playing = False
        self._paused_elapsed = 0.0

    def restart(self) -> None:
        self._paused_elapsed = 0.0
        self._start_time = get_time()
        self.playing = True

    @property
    def elapsed(self) -> float:
        if self.playing:
            return get_time() - self._start_time
        return self._paused_elapsed

    @property
    def finished(self) -> bool:
        return not self.loop and self.elapsed >= self.duration

    @property
    def frame(self) -> Surface:
        elapsed = self.elapsed

        if not self.loop and elapsed >= self.duration:
            return self.frames[-1]

        progress = (elapsed % self.duration) / self.duration
        index = int(progress * self.length)

        return self.frames[index]

    def __len__(self) -> int:
        return self.length

    def __bool__(self) -> bool:
        return bool(self.frames)

    def __getitem__(self, index: int) -> Surface:
        return self.frames[index]

    def __iter__(self) -> Iterator[Surface]:
        return iter(self.frames)

    def __contains__(self, item: Surface) -> bool:
        return item in self.frames