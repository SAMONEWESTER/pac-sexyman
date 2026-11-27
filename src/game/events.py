from dataclasses import dataclass


@dataclass(frozen=True)
class GameEvent:
    pass


@dataclass(frozen=True)
class FrightenGhostsEvent(GameEvent):
    duration: float


@dataclass(frozen=True)
class EatDotEvent(GameEvent):
    player_index: int
    big: bool = False


@dataclass(frozen=True)
class EatFruitEvent(GameEvent):
    player_index: int


@dataclass(frozen=True)
class EatGhostEvent(GameEvent):
    player_index: int


@dataclass(frozen=True)
class CameraShakeEvent(GameEvent):
    amount: float
