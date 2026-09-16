import os
import platform
from functools import wraps
from threading import Lock

from pynput import mouse as _pynput_mouse

from mappings.keyboard import default_keyboard_mapping
from model.keyboard import KeyboardKeys

if platform.system() == "Windows":
    import ctypes

    def is_pressed(key: KeyboardKeys) -> bool:
        value = default_keyboard_mapping[key]
        return ctypes.windll.user32.GetAsyncKeyState(ord(value.upper())) & 0x8000
else:
    from pynput import keyboard as _pynput_keyboard

    def _normalize_key(key) -> str | None:
        if key == _pynput_keyboard.Key.space:
            return " "

        if isinstance(key, _pynput_keyboard.KeyCode):
            return key.char.lower() if key.char is not None else None

        return None

    _pressed_keys = set()

    def _on_press(key):
        value = _normalize_key(key)
        if value is not None:
            _pressed_keys.add(value)

    def _on_release(key):
        value = _normalize_key(key)
        if value is not None:
            _pressed_keys.discard(value)

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


_mouse_lock = Lock()
_mouse_previous_position: tuple[float, float] | None = None
_mouse_delta = (0.0, 0.0)
_mouse_scroll_delta = 0.0


def _on_mouse_move(x: float, y: float) -> None:
    global _mouse_previous_position, _mouse_delta

    with _mouse_lock:
        if _mouse_previous_position is not None:
            previous_x, previous_y = _mouse_previous_position
            dx, dy = _mouse_delta

            # Accumulate movement between game updates.
            _mouse_delta = (
                dx + x - previous_x,
                dy + y - previous_y,
            )

        _mouse_previous_position = (x, y)


def consume_mouse_movement() -> tuple[float, float]:
    """Return accumulated movement and reset it for the next frame."""
    global _mouse_delta

    with _mouse_lock:
        movement = _mouse_delta
        _mouse_delta = (0.0, 0.0)
        return movement


def _on_mouse_scroll(x: float, y: float, dx: float, dy: float) -> None:
    global _mouse_scroll_delta

    with _mouse_lock:
        _mouse_scroll_delta += dy


def consume_mouse_scroll() -> int:
    global _mouse_scroll_delta

    with _mouse_lock:
        # Preserve fractional scrolling until it adds up to a step.
        steps = int(_mouse_scroll_delta)
        _mouse_scroll_delta -= steps
        return steps


_pressed_mouse_buttons: set[_pynput_mouse.Button] = set()


def _on_mouse_click(
    x: float,
    y: float,
    button: _pynput_mouse.Button,
    pressed: bool,
) -> None:
    with _mouse_lock:
        if pressed:
            _pressed_mouse_buttons.add(button)
        else:
            _pressed_mouse_buttons.discard(button)


def is_mouse_pressed(
    button: _pynput_mouse.Button = _pynput_mouse.Button.left,
) -> bool:
    with _mouse_lock:
        return button in _pressed_mouse_buttons


_mouse_listener = _pynput_mouse.Listener(
    on_move=_on_mouse_move,
    on_click=_on_mouse_click,
    on_scroll=_on_mouse_scroll,
)
_mouse_listener.start()


def stop_mouse_listener() -> None:
    _mouse_listener.stop()


##############
# DECORATORS #
##############


def on_key_press(key: KeyboardKeys, act_once_per_press: bool = False):
    """Any class that uses this decorator has to inherit
    from the KeyboardHandler mixin in model.shared"""

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


# TODO: create on_mouse_release
def on_mouse_press(
    button: _pynput_mouse.Button = _pynput_mouse.Button.left,
    act_once_per_press: bool = False,
):
    """Any class that uses this decorator has to inherit
    from the MouseHandler mixin in model.shared"""

    def decorator(func):
        @wraps(func)
        def wrapper(self, *args, **kwargs):
            pressed = is_mouse_pressed(button)

            if not act_once_per_press:
                if pressed:
                    return func(self, *args, **kwargs)
                return None

            was_pressed = self._pressed_mouse_map.get(button, False)
            self._set_pressed_button(button, True)

            if pressed and not was_pressed:
                return func(self, *args, **kwargs)

            elif not pressed and was_pressed:
                self._set_pressed_button(button, False)

        return wrapper

    return decorator
