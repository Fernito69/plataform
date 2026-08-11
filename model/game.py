from enum import StrEnum, auto


class GameStatus(StrEnum):
    PLAYING = auto()
    PAUSED = auto()
    GAMEOVER = auto()
