from model.keyboard import DisplayKeys, KeyboardKeys, MenuKeys, MovementKeys

default_keyboard_mapping: dict[KeyboardKeys, str] = {
    MenuKeys.QUIT: "q",
    MenuKeys.SWITCH_3D_MODE: "2",
    MenuKeys.SWITCH_2D_MODE: "1",
    MovementKeys.UP: "w",
    MovementKeys.LEFT: "a",
    MovementKeys.RIGHT: "d",
    MovementKeys.DOWN: "s",
    MovementKeys.FLY_DOWN: "c",
    MovementKeys.FLY_UP: "r",
    DisplayKeys.DECREASE_X_RESOLUTION: "7",
    DisplayKeys.INCREASE_X_RESOLUTION: "8",
    DisplayKeys.DECREASE_Y_RESOLUTION: "9",
    DisplayKeys.INCREASE_Y_RESOLUTION: "0",
    DisplayKeys.SWITCH_CHAR_MODE: "v",
    DisplayKeys.DECREASE_DISTANCE_FOG: "4",
    DisplayKeys.INCREASE_DISTANCE_FOG: "3",
    DisplayKeys.SWITCH_ANTIALIASING: "p",
    DisplayKeys.DECREASE_FOV: "g",
    DisplayKeys.INCREASE_FOV: "f",
    DisplayKeys.SHUFFLE_COLORS: "m",
}
