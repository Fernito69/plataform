# TODO: refactor this file into proper entity-based files
from dataclasses import dataclass

# map glyphs
EMPTY_SPACE = " "


# Double lines
@dataclass
class Line:
    UL: str
    UR: str
    LL: str
    LR: str
    H: str
    V: str
    CR: str
    CL: str
    CD: str
    CU: str
    CA: str


DoubleLines = Line(
    UL="╔",
    UR="╗",
    LL="╚",
    LR="╝",
    H="═",
    V="║",
    CR="╠",
    CL="╣",
    CD="╦",
    CU="╩",
    CA="╬",
)


SingleLines = Line(
    UL="┌",
    UR="┐",
    LL="└",
    LR="┘",
    H="─",
    V="│",
    CR="├",
    CL="┤",
    CD="┬",
    CU="┴",
    CA="┼",
)


# physics / gameplay tuning
IMMUNE_TIME = 30
GRAVITY_ACCELERATION = 0.3
ENEMY_MOV_FACTOR = 0.1

# screen
FPS = 20
X_RESOLUTION = 80
Y_RESOLUTION = 25
