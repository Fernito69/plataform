from constants import Color
import math

COLOR_CODES = {
    "black": "\033[30m",
    "red": "\033[31m",
    "green": "\033[32m",
    "yellow": "\033[33m",
    "blue": "\033[34m",
    "magenta": "\033[35m",
    "cyan": "\033[36m",
    "white": "\033[37m",
}

BG_COLOR_CODES = {
    "black": "\033[40m",
    "red": "\033[41m",
    "green": "\033[42m",
    "yellow": "\033[43m",
    "blue": "\033[44m",
    "magenta": "\033[45m",
    "cyan": "\033[46m",
    "white": "\033[47m",
}

RESET = "\033[0m"


def colored(
    text: str, color: Color | None = "red", bg_color: Color | None = None
) -> str:
    bg_code = BG_COLOR_CODES[bg_color] if bg_color else ""
    return f"{COLOR_CODES[color or 'red']}{bg_code}{text}{RESET}"


def add_tuple(
    orig: tuple[int | float, int | float], add: tuple[int | float, int | float]
) -> tuple[int | float, int | float]:
    return (orig[0] + add[0], orig[1] + add[1])
