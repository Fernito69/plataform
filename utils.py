from model.shared import (
    Coord2,
    Coord3,
    DistVector2D,
    DistVector3D,
    Number,
    Vector2,
    Vector3,
)
from model.theme import RGB

RESET = "\033[0m"


def colored(text: str, color: RGB | None = None, bg_color: RGB | None = None) -> str:
    fg_code = f"\033[38;2;{color.r};{color.g};{color.b}m" if color else ""
    bg_code = f"\033[48;2;{bg_color.r};{bg_color.g};{bg_color.b}m" if bg_color else ""
    reset_code = RESET if color or bg_color else ""

    return f"{fg_code}{bg_code}{text}{reset_code}"


def add_tuple(
    orig: tuple[Number, Number], add: tuple[Number, Number]
) -> tuple[Number, Number]:
    return (orig[0] + add[0], orig[1] + add[1])


def add_triplet(
    orig: tuple[Number, Number, Number] | list[Number],
    add: tuple[Number, Number, Number] | list[Number],
) -> tuple[Number, Number, Number]:
    return (orig[0] + add[0], orig[1] + add[1], orig[2] + add[2])


def subtract_triplet(
    victim: tuple[Number, Number, Number] | list[Number],
    subtracter: tuple[Number, Number, Number] | list[Number],
) -> tuple[Number, Number, Number]:
    return (
        victim[0] - subtracter[0],
        victim[1] - subtracter[1],
        victim[2] - subtracter[2],
    )


def vector_length(v: Vector3 | Vector2) -> float:
    return (v[0] ** 2 + v[1] ** 2 + (v[2] ** 2 if len(v) == 3 else 0)) ** 0.5


def distance_between_points(
    p1: Coord2 | Coord3, p2: Coord2 | Coord3
) -> DistVector2D | DistVector3D:
    if len(p1) != len(p2):
        raise IndexError("They should have the same length")

    x = p1[0] - p2[0]
    y = p1[1] - p2[1]

    if len(p1) == 2:
        return DistVector2D(vector_length((x, y)), (x, y))

    z = p1[2] - p2[0]

    if len(p1) == 3 and len(p2) == 3:
        return DistVector3D(vector_length([x, y, z]), [x, y, z])  # TODO: type properly

    return DistVector2D(0, (0, 0))
