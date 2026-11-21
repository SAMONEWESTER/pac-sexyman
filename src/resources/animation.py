from typing import Iterable, Iterator

from pygame import Surface
from ..utils.get_time import get_time


class Animation:
    def __init__(
            self,
            frames: Iterable[Surface],
            speed: float = 5.0,
            loop: bool = True
            ) -> None:
        self.frames: tuple[Surface, ...] = tuple(frames)
        self.speed: float = speed
        self.loop: bool = loop

        self.current_frame: int = 0
        self.playing: bool = True
        self.finished: bool = False
        self.start_time: float = -1.0

    def play(self) -> None:
        self.playing = True
        if self.start_time == -1.0:
            self.start_time = get_time()

    def stop(self) -> None:
        self.playing = False
        self.start_time = -1.0

    def pause(self) -> None:
        self.playing = False

    def __len__(self) -> int:
        return len(self.frames)

    def __bool__(self) -> bool:
        return bool(self.frames)

    def __getitem__(self, index: int) -> Surface:
        return self.frames[index]

    def __delitem__(self, index: int) -> None:
        del self.frames[index]

    def __iter__(self) -> Iterator[Surface]:
        return iter(self.frames)

    def __contains__(self, item: Surface) -> bool:
        return item in self.frames