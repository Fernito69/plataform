import os
import platform
from functools import wraps

from mappings.keyboard import default_keyboard_mapping
from model.keyboard import KeyboardKeys

if platform.system() == "Windows":
    import ctypes

    def is_pressed(key: KeyboardKeys) -> bool:
        value = default_keyboard_mapping[key]
        return ctypes.windll.user32.GetAsyncKeyState(ord(value.upper())) & 0x8000
else:
    from pynput import keyboard as _pynput_keyboard

    _pressed_keys = set()

    def _on_press(key):
        try:
            _pressed_keys.add(key.char.lower())
        except AttributeError:
            pass

    def _on_release(key):
        try:
            _pressed_keys.discard(key.char.lower())
        except AttributeError:
            pass

    _listener = _pynput_keyboard.Listener(on_press=_on_press, on_release=_on_release)
    _listener.daemon = True
    _listener.start()

    def is_pressed(key: KeyboardKeys) -> bool:
        value = default_keyboard_mapping[key]
        return value.lower() in _pressed_keys


if os.name == "nt":
    import msvcrt

    def get_key():
        if not msvcrt.kbhit():
            return None

        # getwch() returns a Unicode character, so decoding isn't needed.
        key = msvcrt.getwch()

        # Arrow and other special keys return a two-character sequence.
        if key in ("\x00", "\xe0"):
            special_key = msvcrt.getwch()

            # WASD controls.
            return {
                "H": "w",  # Up
                "P": "s",  # Down
                "K": "a",  # Left
                "M": "d",  # Right
            }.get(special_key)

        return key.lower()


def clear():
    os.system("cls" if os.name == "nt" else "clear")


def on_key_press(key: KeyboardKeys, act_once_per_press: bool = False):
    def decorator(func):
        @wraps(func)
        def wrapper(self, *args, **kwargs):
            pressed = is_pressed(key)

            if pressed and not act_once_per_press:
                return func(self, *args, **kwargs)

            was_pressed = self._pressed_key_map.get(key, False)

            if pressed and not was_pressed:
                self._set_pressed_key(key, True)
                func(self, *args, **kwargs)

            elif not pressed and was_pressed:
                self._set_pressed_key(key, False)

        return wrapper

    return decorator
