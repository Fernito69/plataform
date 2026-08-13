from enum import StrEnum, auto


class KeyCategory(StrEnum):
    MENU = auto()
    MOVEMENT = auto()


class MenuKeys(StrEnum):
    QUIT = auto()
    SWITCH_MODE = auto()


class MovementKeys(StrEnum):
    JUMP = auto()
    LEFT = auto()
    RIGHT = auto()
    DOWN = auto()


KeyboardKeys = MenuKeys | MovementKeys
