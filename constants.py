"""Shared constants: map glyphs, colors, physics tuning, and screen size."""

from typing import Literal, Optional

# map glyphs
EMPTY_SPACE = " "
UL = "╔"
UR = "╗"
LL = "╚"
LR = "╝"
H = "═"
V = "║"
CR = "╠"
CL = "╣"
CD = "╦"
CU = "╩"
CA = "╬"

# physics / gameplay tuning
IMMUNE_TIME = 30
GRAVITY_ACCELERATION = .1
ENEMY_MOV_FACTOR = 0.1

# screen
FPS = 30
X_RESOLUTION = 80
Y_RESOLUTION = 25

Color = Literal[
    "black",
    "red",
    "green",
    "yellow",
    "blue",
    "magenta",
    "cyan",
    "white",
]

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
    text: str, color: Optional[Color] = "red", bg_color: Optional[Color] = None
) -> str:
    bg_code = BG_COLOR_CODES[bg_color] if bg_color else ""
    return f"{COLOR_CODES[color or 'red']}{bg_code}{text}{RESET}"
