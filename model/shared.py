from abc import abstractmethod

from pynput import mouse as _pynput_mouse

from model.keyboard import KeyboardKeys
from terminal import is_mouse_pressed, is_pressed


class KeyboardHandler:
    """Any class that uses the @on_key_press decorator has to inherit from KeyboardHandler"""

    _pressed_key_map: dict[KeyboardKeys, bool] = {}

    def _set_pressed_key(self, key: KeyboardKeys, val: bool):
        self._pressed_key_map[key] = val

    def _is_pressed(self, key: KeyboardKeys) -> bool:
        return is_pressed(key)
        # return self._pressed_key_map.get(key) or False

    @abstractmethod
    def handle_keyboard_input(cls) -> None:
        pass


class MouseHandler:
    """Any class that uses the @on_mouse_press decorator has to inherit from KeyboardHandler"""

    _pressed_mouse_map: dict[_pynput_mouse.Button, bool] = {}

    def _set_pressed_button(self, button: _pynput_mouse.Button, val: bool):
        self._pressed_mouse_map[button] = val

    def _is_mouse_pressed(self, button: _pynput_mouse.Button) -> bool:
        return is_mouse_pressed(button)
        # return self._pressed_key_map.get(key) or False

    @abstractmethod
    def handle_mouse_input(cls) -> None:
        pass


class Engine:
    @abstractmethod
    def main_loop(cls) -> None:
        pass
