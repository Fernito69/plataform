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
GRAVITY_ACCELERATION = 0.3
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
