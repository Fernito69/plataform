from dataclasses import dataclass
from enum import StrEnum, auto

from model.theme import Theme


# TODO: decommission this in favor of lifesteps? we should have linear and exponential, decrease of increase is determined by the delta between LifeSteps
class TransitionType(StrEnum):
    LINEAR_DECREASE = auto()
    EXPONENTIAL_DECREASE = auto()
    NONE = auto()
    LINEAR_INCREASE = auto()


@dataclass
class LifeStep:
    life_tick: int
    theme: Theme | None
    theme_change: TransitionType = TransitionType.NONE


@dataclass
class LineLifeStep(LifeStep):
    thickness: float | None = None


@dataclass
class CircleLifeStep(LifeStep):
    radius: float | None = None
