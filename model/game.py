from enum import StrEnum, auto


class GameMode(StrEnum):
    MODE_2D = auto()
    MODE_PHYSICS_2D = auto()
    MODE_3D = auto()
    MODE_3D_V2 = auto()


class GameStatus(StrEnum):
    RUNNING = auto()
    PAUSED = auto()
    GAMEOVER = auto()
    QUIT = auto()
