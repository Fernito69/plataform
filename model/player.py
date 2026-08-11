from enum import StrEnum, auto


class PlayerStatus(StrEnum):
    ALIVE = auto()
    DEAD = auto()
    QUIT = auto()
    EXIT = auto()
