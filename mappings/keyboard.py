from model.keyboard import KeyboardKeys, KeyCategory, MenuKeys, MovementKeys

keyboard_mapping: dict[KeyCategory, dict[KeyboardKeys, str]] = {
    KeyCategory.MENU: {
        MenuKeys.QUIT: "q",
    },
    KeyCategory.MOVEMENT: {
        MovementKeys.JUMP: "w",
        MovementKeys.LEFT: "a",
        MovementKeys.RIGHT: "d",
        MovementKeys.DOWN: "s",
    },
}


def get_key(key: KeyboardKeys) -> str:
    return keyboard_mapping[KeyCategory.MOVEMENT][key]
