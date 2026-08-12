from dataclasses import dataclass, field
from typing import Literal

from constants import DoubleLines, Line

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


_DEFAULT_LINES = DoubleLines


@dataclass
class Theme:
    color: Color | None = None
    bg_color: Color | None = None
    line_type: Line = field(default_factory=lambda: _DEFAULT_LINES)
    custom_line_chars: list[str] | None = None
    # only relevant if custom_line_chars is not None
    custom_line_type: Literal["random", "sequential", "back&forth"] = "random"
