from model.keyboard import KeyboardKeys, MenuKeys, MovementKeys

default_keyboard_mapping: dict[KeyboardKeys, str] = {
    MenuKeys.QUIT: "q",
    MenuKeys.SWITCH_3D_MODE: "2",
    MenuKeys.SWITCH_2D_MODE: "1",
    MovementKeys.JUMP: "w",
    MovementKeys.LEFT: "a",
    MovementKeys.RIGHT: "d",
    MovementKeys.DOWN: "s",
    MovementKeys.FLY_DOWN: "f",
    MovementKeys.FLY_UP: "r",
}
