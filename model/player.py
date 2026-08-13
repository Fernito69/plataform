from enum import StrEnum, auto


class PlayerStatus(StrEnum):
    ALIVE = auto()
    DEAD = auto()
    QUIT = auto()
    MODE_2D = auto()
    MODE_3D = auto()
    EXIT = auto()
