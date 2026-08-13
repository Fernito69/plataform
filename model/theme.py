from dataclasses import dataclass, field
from typing import Literal

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


@dataclass
class RGB:
    r: int = 127
    g: int = 127
    b: int = 127


# TODO: make this an enum
type SequencingType = Literal["random", "sequential", "back&forth"]


@dataclass
class Theme:
    line_type: Line | None = None
    color: RGB | None = None
    bg_color: RGB | None = None
    custom_line_chars: list[str] | None = None
    # only relevant if custom_line_chars is not None
    custom_line_type: SequencingType = "random"
