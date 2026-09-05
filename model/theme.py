from dataclasses import dataclass
from typing import Literal

EMPTY_SPACE = " "
UPPER_PIXEL_CHAR = "▀"
LOWER_PIXEL_CHAR = "▄"
BR = "\n"


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


# TODO: implement cool methods like in Vector and Point to be able to add two RGBs, etc


@dataclass
class RGB:
    r: int = 127
    g: int = 127
    b: int = 127

    # TODO: intensity is actually transparency, we should rename it
    intensity: float = 1

    def __str__(self):
        return f"rgb({self.r}, {self.g}, {self.b})"

    # TODO: unify these two
    def with_intensity(self, intensity: float | None = None) -> "RGB":
        if intensity is not None:
            self.intensity = max(0, min(1, intensity))

        return RGB(
            int(self.r * self.intensity),
            int(self.g * self.intensity),
            int(self.b * self.intensity),
        )

    def with_intensity_v2(self, intensity: float | None = None) -> "RGB":
        if intensity is not None:
            self.intensity = max(0, min(1, intensity))

        return RGB(
            int(self.r * self.intensity),
            int(self.g * self.intensity),
            int(self.b * self.intensity),
            intensity=self.intensity,
        )

    def mix_with(self, colors: "RGB" | list["RGB"]) -> "RGB":
        colors = [self, *colors] if isinstance(colors, list) else [self, colors]
        
        weighted_intensity = sum([c.intensity for c in colors])
        weighted_sum_r = sum([c.r * c.intensity for c in colors]) / weighted_intensity
        weighted_sum_g = sum([c.g * c.intensity for c in colors]) / weighted_intensity
        weighted_sum_b = sum([c.b * c.intensity for c in colors]) / weighted_intensity

        return RGB(
            r=round(weighted_sum_r),
            g=round(weighted_sum_g),
            b=round(weighted_sum_b),
        )

    def __add__(self, other: "RGB") -> "RGB":
        return RGB(
            r=self.r + other.r,
            g=self.g + other.g,
            b=self.b + other.b,
        )

    def __sub__(self, other: "RGB") -> "RGB":
        return RGB(
            r=self.r - other.r,
            g=self.g - other.g,
            b=self.b - other.b,
        )

    def __iter__(self):
        yield self.r
        yield self.g
        yield self.b


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
