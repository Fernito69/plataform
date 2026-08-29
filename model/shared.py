from abc import abstractmethod

from model.keyboard import KeyboardKeys


class KeyboardHandler:
    """Any class that uses the @on_key_press decorator has to inherit from KeyboardHandler"""

    _pressed_key_map: dict[KeyboardKeys, bool] = {}

    def _set_pressed_key(self, key: KeyboardKeys, val: bool):
        self._pressed_key_map[key] = val

    @abstractmethod
    def handle_player_input(cls) -> None:
        pass
