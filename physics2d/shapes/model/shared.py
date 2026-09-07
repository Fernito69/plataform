from enum import StrEnum, auto


class TransitionType(StrEnum):
    LINEAR_DECREASE = auto()
    EXPONENTIAL_DECREASE = auto()
    NONE = auto()
    LINEAR_INCREASE = auto()
