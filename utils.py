import math
from collections.abc import Callable
from dataclasses import dataclass
from random import random
from typing import Any

from constants import PI
from model.base import DistVector3D, PointF, VectorF
from model.theme import RGB

_RESET = "\033[0m"
_FG_CODE = "\033[38;2;"
_BG_CODE = "\033[48;2;"

# TODO: separate functions here


def shuffle_list(_: Any | None = None) -> float:
    """
    returns a random number between -.5 and .5, good for shuffling lists
    """
    return 0.5 - random()


def _encode_rgb(color: RGB) -> str:
    return f"{color.r};{color.g};{color.b}"


def extract_color_from_string(text: str) -> RGB:
    if not has_color(text):
        return RGB(0, 0, 0)

    rgb_string = text.split(_FG_CODE)[1].split("m")[0]
    r, g, b = rgb_string.split(";")
    return RGB(int(r), int(g), int(b))


def mix_colors(colores: list[RGB]) -> RGB:
    weighted_intensity = sum([c.intensity for c in colores])
    weighted_sum_r = sum([c.r * c.intensity for c in colores]) / weighted_intensity
    weighted_sum_g = sum([c.g * c.intensity for c in colores]) / weighted_intensity
    weighted_sum_b = sum([c.b * c.intensity for c in colores]) / weighted_intensity

    return RGB(
        r=round(weighted_sum_r),
        g=round(weighted_sum_g),
        b=round(weighted_sum_b),
    )


def extract_bg_color_from_string(text: str) -> RGB:
    if not has_bg_color(text):
        return RGB(0, 0, 0)

    rgb_string = text.split(_BG_CODE)[1].split("m")[0]
    r, g, b = rgb_string.split(";")
    return RGB(int(r), int(g), int(b))


def colored(text: str, color: RGB | None = None, bg_color: RGB | None = None) -> str:
    fg_code = f"{_FG_CODE}{_encode_rgb(color)}m" if color else ""
    bg_code = f"{_BG_CODE}{_encode_rgb(bg_color)}m" if bg_color else ""
    reset_code = _RESET if (color or bg_color) and _RESET not in text else ""

    return f"{fg_code}{bg_code}{text}{reset_code}"


def get_raw_string(s: str) -> str:
    return s.split(_RESET)[0] if _RESET in s else s


def has_color(text: str) -> bool:
    return _FG_CODE in text


def has_bg_color(text: str, black_is_not_condidered_bg: bool = True) -> bool:
    return (
        _BG_CODE in text and not _encode_rgb(RGB(0, 0, 0)) in text
        if black_is_not_condidered_bg
        else _BG_CODE in text
    )


# def add_tuple(
#     orig: tuple[float | int, float | int], add: tuple[float | int, float | int]
# ) -> tuple[float | int, float | int]:
#     return (orig[0] + add[0], orig[1] + add[1])


# # TODO: these are dumb, there must be a way to generalize
# def scale_tuple(
#     orig: tuple[float | int, float | int], multi: float
# ) -> tuple[float | int, float | int]:
#     return (orig[0] * multi, orig[1] * multi)


# def scale_triplet(
#     orig: tuple[float | int, float | int, float | int], multi: float
# ) -> tuple[float | int, float | int, float | int]:
#     return (orig[0] * multi, orig[1] * multi, orig[2] * multi)


def add_triplet(
    orig: tuple[float | int, float | int, float | int],
    add: tuple[float | int, float | int, float | int],
) -> tuple[float | int, float | int, float | int]:
    return (orig[0] + add[0], orig[1] + add[1], orig[2] + add[2])


# def subtract_triplet(
#     victim: tuple[float | int, float | int, float | int],
#     subtracter: tuple[float | int, float | int, float | int],
# ) -> tuple[float | int, float | int, float | int]:
#     return (
#         victim[0] - subtracter[0],
#         victim[1] - subtracter[1],
#         victim[2] - subtracter[2],
#     )


# Instead of diameter, pass an Entity3D and call an internal get diameter function
# I think distance_to_border doesn't work because the size is not the diameter in the current way we are creating the entities
def distance_between_points(
    p1: PointF,
    p2: PointF,
    diameter_p2: float | None = 0.0,
    entity: Any = None,
) -> DistVector3D:
    # if len(p1) != len(p2):
    #     print(f"p1: {p1}, p2: {p2} - Entity: {entity.vertices}, {entity.name}")
    #     raise IndexError("They should have the same length")

    vector = (p1 - p2).as_vector()
    distance = abs(vector)
    # TODO: this kinda works but not quite. We have to calculate the distance to the current vertex. this factor should become 1
    distance_to_border: float | None = (
        distance * 0.5 + diameter_p2 if diameter_p2 else distance * 0.5
    )
    # distance_to_border: float = distance + (diameter_p2 / 2) if diameter_p2 else distance
    return DistVector3D(
        distance=distance,
        vector=vector,
        distance_to_edge=distance_to_border,
    )

    return DistVector3D(0, (0, 0, 0))


# def vector_length(v: Vector3F | Vector2F) -> float:
#     return (v[0] ** 2 + v[1] ** 2 + (v[2] ** 2 if len(v) == 3 else 0)) ** 0.5


def rotate_point(point: PointF, rotation_axis: PointF, angle: float) -> PointF:
    if angle == 0:
        return point
    a = math.radians(angle)
    new_x = (
        (point.x - rotation_axis.x) * math.cos(a)
        - (point.y - rotation_axis.y) * math.sin(a)
        + rotation_axis.x
    )
    new_y = (
        (point.x - rotation_axis.x) * math.sin(a)
        + (point.y - rotation_axis.y) * math.cos(a)
        + rotation_axis.y
    )
    return PointF(new_x, new_y)


@dataclass
class DistanceFromLineToPointResponse:
    distance: float
    intersection: PointF
    slope: float | None


def distance_from_line_to_point(
    line: tuple[PointF, PointF], point: PointF
) -> DistanceFromLineToPointResponse:
    line_point_1, line_point_2 = line
    original_m = get_slope(line_point_1, line_point_2)

    # edge case 1: when slope is infinite! straight distance from point to line
    if original_m is None:
        return DistanceFromLineToPointResponse(
            distance=abs(point.x - line_point_1.x),
            intersection=PointF(line_point_1.x, point.y),
            slope=None,
        )

    # edge case 2: when slope is 0! same as above
    if original_m == 0:
        return DistanceFromLineToPointResponse(
            distance=abs(point.y - line_point_1.y),
            intersection=PointF(point.x, line_point_1.y),
            slope=0,
        )

    # get the equation of the perpendicular line
    perpendicular_m = -1 / original_m

    # with (y - y1) = m(x - x1) -> y-intercept = -mx1 + y1
    y_intercept_perp_line = -perpendicular_m * point.x + point.y
    y_intercept_orig_line = -original_m * line_point_1.x + line_point_1.y

    # we equate both to extract x, and then y
    new_x = (y_intercept_perp_line - y_intercept_orig_line) / (original_m - perpendicular_m)
    new_y = perpendicular_m * new_x + y_intercept_perp_line
    intersection = PointF(new_x, new_y)

    # now get distance
    return DistanceFromLineToPointResponse(
        distance=abs(point - intersection),
        intersection=intersection,
        slope=original_m,
    )


def get_slope(point1: PointF, point2: PointF) -> float | None:
    if point2.x - point1.x == 0:
        return None
    return (point2.y - point1.y) / (point2.x - point1.x)


def get_perpendicular_slope(point1: PointF, point2: PointF) -> float | None:
    m = get_slope(point1, point2)
    return 0 if m is None else None if m == 0 else -1 / m


def get_normal_unit_vector(point1: PointF, point2: PointF, velocity: VectorF) -> VectorF:
    perpendicular_m = get_perpendicular_slope(point1, point2)
    angle = (
        0
        if perpendicular_m is None
        else PI / 2
        if perpendicular_m == 0
        else math.atan(perpendicular_m)
    ) % PI
    x_factor = 1 if velocity.x < 0 else -1
    y_factor = 1 if velocity.y < 0 else -1
    return VectorF(x=x_factor * math.cos(angle), y=y_factor * math.sin(angle))


@dataclass
class GetLineEquationResponse:
    get_y: Callable[[float], float]
    get_x: Callable[[float], float]
    m: float | None


def get_line_equations(point1: PointF, point2: PointF) -> GetLineEquationResponse:
    m = get_slope(point1, point2)

    def get_y(x: float) -> float:
        if not m:
            return point1.y
        return m * (x - point1.x) + point1.y

    def get_x(y: float):
        if not m:
            return point1.x
        return ((y - point1.y) / m) + point1.x

    return GetLineEquationResponse(get_y, get_x, m)
