import math
import random
from collections.abc import Callable
from dataclasses import dataclass
from random import random
from typing import Any
from constants import PI
from model.base import DistVector3D, PointF, ScreenPos, Slope, VectorF
from model.theme import RGB
from three_d_renderer.constants import DEFAULT_DISTANCE_TO_SPEC, PIXEL_ASPECT_RATIO

# TODO: separate functions here in a file per domain

######################
"""  RANDOM """
######################


# TODO: now that this is built-in in VectorF, deprecate it
def random_offset_vector(scale_x: float = 1, scale_y: float = 1, scale_z: float = 1) -> VectorF:
    return VectorF(random_offset(scale_x), random_offset(scale_y), random_offset(scale_z))


def random_offset(scale: Any = 1) -> float:
    """
    returns a random number between -.5 and .5, good for shuffling lists. Also receives an optional scale factor
    """
    return scale * (0.5 - random())


######################
"""  COLOR  """
######################

_RESET = "\033[0m"
_FG_CODE = "\033[38;2;"
_BG_CODE = "\033[48;2;"


def _encode_rgb(color: RGB) -> str:
    return f"{color.r};{color.g};{color.b}"


def extract_color_from_string(text: str) -> RGB:
    if not has_color(text):
        return RGB(0, 0, 0)

    rgb_string = text.split(_FG_CODE)[1].split("m")[0]
    r, g, b = rgb_string.split(";")
    return RGB(int(r), int(g), int(b))


# TODO: get rid of this function in favor of RGB.mix_with
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


##################################
"""  POINT/VECTOR ARITMETIC  """
##################################


# Instead of diameter, pass an Entity3D and call an internal get diameter function
# I think distance_to_border doesn't work because the size is not the diameter in the current way we are creating the entities
def distance_between_points(
    p1: PointF,
    p2: PointF,
    diameter_p2: float | None = 0.0,
) -> DistVector3D:
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


# TODO: deprecate in favor of PointF.rotate()
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
    slope: Slope


def distance_from_line_to_point(
    line: tuple[PointF, PointF], point: PointF
) -> DistanceFromLineToPointResponse:
    line_point_1, line_point_2 = line
    original_m = get_slope(line_point_1, line_point_2)

    # edge case 1: when slope is infinite! straight distance from point to line
    if original_m == "+Inf" or original_m == "-Inf":
        return DistanceFromLineToPointResponse(
            distance=abs(point.x - line_point_1.x),
            intersection=PointF(line_point_1.x, point.y),
            slope=original_m,
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


def get_slope(point1: PointF, point2: PointF) -> Slope:
    if point2.x - point1.x == 0:
        return "+Inf" if point1.y >= point2.y else "-Inf"
    return (point2.y - point1.y) / (point2.x - point1.x)


def get_slope_from_vector(vector: VectorF) -> Slope:
    if vector.x == 0:
        return "+Inf" if vector.y >= 0 else "-Inf"
    return vector.y / vector.x


def get_perpendicular_slope(point1: PointF, point2: PointF) -> Slope:
    m = get_slope(point1, point2)
    return (
        0
        if m == "+Inf"
        else -0
        if m == "-Inf"
        else "+Inf"
        if m == 0
        else "-Inf"
        if m == -0
        else -1 / m
    )


def get_normal_unit_vector_from_line(point1: PointF, point2: PointF) -> VectorF:
    perpendicular_m = get_perpendicular_slope(point1, point2)
    angle = get_angle_from_slope(perpendicular_m)
    return get_vector_from_angle(angle)


def get_normal_vectors(vector: VectorF, unit_vector: bool = False) -> tuple[VectorF, VectorF]:
    m = get_slope_from_vector(vector)
    angle = get_angle_from_slope(m) % PI
    magnitude = 1 if unit_vector else abs(vector)
    return (
        get_vector_from_angle(angle + PI / 2, magnitude),
        get_vector_from_angle(angle - PI / 2, magnitude),
    )


def get_vector_from_angle(angle: float, magnitude: float = 1) -> VectorF:
    return (magnitude * VectorF(x=math.cos(angle), y=math.sin(angle))).as_vector()


def get_angle_from_slope(slope: Slope) -> float:
    return (
        PI / 2
        if slope == "+Inf"
        else -PI / 2
        if slope == "-Inf"
        else 0
        if slope == 0
        else math.atan(slope)
    )


def get_line_angle(point1: PointF, point2: PointF) -> float:
    return get_angle_from_slope(get_slope(point1, point2))


# TODO: make it built in into VectorF
def get_vector_angle(vector: VectorF) -> float:
    return get_angle_from_slope(get_slope(vector, 2 * vector))


@dataclass
class GetLineEquationResponse:
    get_y: Callable[[float], float]
    get_x: Callable[[float], float]
    m: Slope


def get_line_equations(point1: PointF, point2: PointF) -> GetLineEquationResponse:
    m = get_slope(point1, point2)

    def get_y(x: float) -> float:
        if m == "+Inf" or m == "-Inf":
            return point1.y
        return m * (x - point1.x) + point1.y

    def get_x(y: float):
        if m == "+Inf" or m == "-Inf" or m == 0:
            return point1.x
        return ((y - point1.y) / m) + point1.x

    return GetLineEquationResponse(get_y, get_x, m)


##################################
"""  3D PROJECTION  """
##################################


def project_3d_into_2d(
    point3: PointF,
    curr_resolution: ScreenPos,
    spec_angle: VectorF = VectorF(0, 0, 0),
    spec_position: PointF = PointF(0, 0, 0),
    fov: float = DEFAULT_DISTANCE_TO_SPEC,
    pixel_aspect_ratio: float = PIXEL_ASPECT_RATIO,
) -> PointF | None:
    X_RES, Y_RES = curr_resolution

    x, y, z = normalize_vertex_according_to_another(point3, spec_position, spec_angle)

    if y <= 0:
        return

    x_pos = (x * fov / y) + (X_RES / 2)
    y_pos = ((z * fov / y) + (Y_RES / 2)) / pixel_aspect_ratio

    return PointF(x_pos, y_pos)


def normalize_vertex_according_to_another(
    vertex: PointF, reference_vertex: PointF, reference_vertex_angle: VectorF
) -> PointF:
    """takes an absolutely-positioned vertex and transforms it according to another's position and angle"""
    # Normalize by angle: for now only x-axis, since we have only one degree of freedom for rotation
    rotated_point = rotate_point(
        PointF(vertex.x, vertex.y),
        PointF(reference_vertex.x, reference_vertex.y),
        -reference_vertex_angle.x,
    )
    rotated_vertex = PointF(
        x=rotated_point.x,
        y=rotated_point.y,
        z=vertex.z,
    )
    # Normalize by position
    return rotated_vertex - reference_vertex
