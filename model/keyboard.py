from enum import StrEnum, auto


class KeyCategory(StrEnum):
    MENU = auto()
    MOVEMENT = auto()


class DisplayKeys(StrEnum):
    INCREASE_X_RESOLUTION = auto()
    INCREASE_Y_RESOLUTION = auto()
    DECREASE_X_RESOLUTION = auto()
    DECREASE_Y_RESOLUTION = auto()
    SWITCH_CHAR_MODE = auto()
    DECREASE_DISTANCE_FOG = auto()
    INCREASE_DISTANCE_FOG = auto()
    SWITCH_ANTIALIASING = auto()
    INCREASE_FOV = auto()
    DECREASE_FOV = auto()


class MenuKeys(StrEnum):
    QUIT = auto()
    SWITCH_3D_MODE = auto()
    SWITCH_2D_MODE = auto()


class MovementKeys(StrEnum):
    UP = auto()
    LEFT = auto()
    RIGHT = auto()
    DOWN = auto()
    FLY_UP = auto()
    FLY_DOWN = auto()


KeyboardKeys = MenuKeys | MovementKeys | DisplayKeys
