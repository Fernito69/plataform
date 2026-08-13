from dataclasses import dataclass, field
from typing import Literal

from constants import DoubleLines, Line


@dataclass
class RGB:
    r: int = 127
    g: int = 127
    b: int = 127


_DEFAULT_LINES = DoubleLines


@dataclass
class Theme:
    color: RGB | None = None
    bg_color: RGB | None = None
    line_type: Line = field(default_factory=lambda: _DEFAULT_LINES)
    custom_line_chars: list[str] | None = None
    # only relevant if custom_line_chars is not None
    custom_line_type: Literal["random", "sequential", "back&forth"] = "random"
