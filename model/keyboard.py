from enum import StrEnum, auto


class KeyCategory(StrEnum):
    MENU = auto()
    MOVEMENT = auto()


class DisplayKeys(StrEnum):
    INCREASE_X_RESOLUTION = auto()
    INCREASE_Y_RESOLUTION = auto()
    DECREASE_X_RESOLUTION = auto()
    DECREASE_Y_RESOLUTION = auto()
    SWITCH_RENDERING_MODE = auto()
    DECREASE_VISIBILITY = auto()
    INCREASE_VISIBILITY = auto()
    SWITCH_ANTIALIASING = auto()
    INCREASE_FOV = auto()
    DECREASE_FOV = auto()
    SHUFFLE_COLORS = auto()


class MenuKeys(StrEnum):
    QUIT = auto()
    SWITCH_3D_MODE = auto()
    SWITCH_2D_MODE = auto()
    TOGGLE_ROTATION = auto()


class MovementKeys(StrEnum):
    UP = auto()
    LEFT = auto()
    RIGHT = auto()
    DOWN = auto()
    FLY_UP = auto()
    FLY_DOWN = auto()


KeyboardKeys = MenuKeys | MovementKeys | DisplayKeys
