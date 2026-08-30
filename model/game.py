from enum import StrEnum, auto


class GameMode(StrEnum):
    PLATFORMER_V1 = auto()
    PHYSICS_2D = auto()
    VOXELS_3D = auto()
    LINES_3D = auto()


class GameStatus(StrEnum):
    RUNNING = auto()
    PAUSED = auto()
    GAMEOVER = auto()
    QUIT = auto()
