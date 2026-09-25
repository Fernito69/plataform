from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

EMPTY_SPACE = " "
UPPER_PIXEL_CHAR = "▀"
LOWER_PIXEL_CHAR = "▄"

"""
TODO: we have all these options, maybe we can improve the renderer in the future
   ▘ ▝ ▀
 ▖ ▌ ▞ ▛
 ▗ ▚ ▐ ▜
 ▄ ▙ ▟ █
 
 | Character | Code point | Filled area              |
| :-------: | ---------- | ------------------------ |
|    `▀`    | U+2580     | Upper half               |
|    `▁`    | U+2581     | Lower ⅛                  |
|    `▂`    | U+2582     | Lower ¼                  |
|    `▃`    | U+2583     | Lower ⅜                  |
|    `▄`    | U+2584     | Lower half               |
|    `▅`    | U+2585     | Lower ⅝                  |
|    `▆`    | U+2586     | Lower ¾                  |
|    `▇`    | U+2587     | Lower ⅞                  |
|    `█`    | U+2588     | Full block               |
|    `▉`    | U+2589     | Left ⅞                   |
|    `▊`    | U+258A     | Left ¾                   |
|    `▋`    | U+258B     | Left ⅝                   |
|    `▌`    | U+258C     | Left half                |
|    `▍`    | U+258D     | Left ⅜                   |
|    `▎`    | U+258E     | Left ¼                   |
|    `▏`    | U+258F     | Left ⅛                   |
|    `▐`    | U+2590     | Right half               |
|    `░`    | U+2591     | Light shading            |
|    `▒`    | U+2592     | Medium shading           |
|    `▓`    | U+2593     | Dark shading             |
|    `▔`    | U+2594     | Upper ⅛                  |
|    `▕`    | U+2595     | Right ⅛                  |
|    `▖`    | U+2596     | Lower-left quadrant      |
|    `▗`    | U+2597     | Lower-right quadrant     |
|    `▘`    | U+2598     | Upper-left quadrant      |
|    `▙`    | U+2599     | All except upper-right   |
|    `▚`    | U+259A     | Upper-left + lower-right |
|    `▛`    | U+259B     | All except lower-right   |
|    `▜`    | U+259C     | All except lower-left    |
|    `▝`    | U+259D     | Upper-right quadrant     |
|    `▞`    | U+259E     | Upper-right + lower-left |
|    `▟`    | U+259F     | All except upper-left    |

"""
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
    r: int
    g: int
    b: int

    # TODO: intensity is actually transparency, we should rename it
    intensity: float

    def __init__(
        self,
        r: float = 127,
        g: float = 127,
        b: float = 127,
        intensity: float = 1,
    ):
        self.r = min(255, max(0, round(r)))
        self.g = min(255, max(0, round(g)))
        self.b = min(255, max(0, round(b)))
        self.intensity = min(1, max(0, intensity))

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

    # TODO: decommission this, doesn't work!
    def mix_with(self, colors: RGB | list[RGB]) -> RGB:
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

    def get_gradient(
        self,
        target_color: RGB,
        curr_ratio: float = 0.5,  # default value gives 50/50 mix
        total: float = 1,  # assumes "curr_ratio" it's given in %
    ) -> RGB:
        _factor = curr_ratio / total
        return self.with_intensity(1 - _factor) + target_color.with_intensity(_factor)

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

    def __eq__(self, other) -> bool:
        if not isinstance(other, RGB):
            return NotImplemented

        return (
            self.r == other.r
            and self.g == other.g
            and self.b == other.b
            and self.intensity == other.intensity
        )


# TODO: make this an enum
type SequencingType = Literal["random", "sequential", "back&forth"]


@dataclass
class Theme:
    color: RGB | None = None
    bg_color: RGB | None = None
    # TODO: move this legacy platformer_v1 stuff somewhere else
    line_type: Line | None = None
    custom_line_chars: list[str] | None = None
    # only relevant if custom_line_chars is not None
    custom_line_type: SequencingType = "random"
