from enum import StrEnum, auto


class PlayerStatus(StrEnum):
    PLAYING = auto()
    DEAD = auto()
    END_LEVEL_2D = auto()
