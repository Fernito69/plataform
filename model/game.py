from enum import StrEnum, auto


class GameStatus(StrEnum):
    MODE_2D = auto()
    MODE_3D = auto()
    PAUSED = auto()
    GAMEOVER = auto()
    QUIT = auto()
