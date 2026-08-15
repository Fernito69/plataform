from model.shared import (
    Point2,
    Point3,
    DistVector2D,
    DistVector3D,
    Number,
    Vector2,
    Vector3,
)
from model.theme import RGB

RESET = "\033[0m"
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


def mix_colors(c1: RGB, c2: RGB) -> RGB:
    return RGB(
        r=round((c2.r + c2.r) / 2),
        g=round((c2.g + c2.g) / 2),
        b=round((c2.b + c2.b) / 2),
    )


def extract_bg_color_from_string(text: str) -> RGB | None:
    if not has_bg_color(text):
        return None

    rgb_string = text.split(_BG_CODE)[1].split("m")[0]
    r, g, b = rgb_string.split(";")
    return RGB(int(r), int(g), int(b))


def colored(text: str, color: RGB | None = None, bg_color: RGB | None = None) -> str:
    fg_code = f"{_FG_CODE}{_encode_rgb(color)}m" if color else ""
    bg_code = f"{_BG_CODE}{_encode_rgb(bg_color)}m" if bg_color else ""
    reset_code = RESET if (color or bg_color) and RESET not in text else ""

    return f"{fg_code}{bg_code}{text}{reset_code}"


def has_color(text: str) -> bool:
    return _FG_CODE in text


def has_bg_color(text: str, black_is_not_condidered_bg: bool = True) -> bool:
    return (
        _BG_CODE in text and not _encode_rgb(RGB(0, 0, 0)) in text
        if black_is_not_condidered_bg
        else _BG_CODE in text
    )


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


# Instead of diameter, pass an Entity3D and call an internal get diameter function
# I think distance_to_border doesn't work because the size is not the diameter in the current way we are creating the entities
def distance_between_points(
    p1: Point2 | Point3, p2: Point2 | Point3, diameter_p2: float | None = 0.0
) -> DistVector3D:
    if len(p1) != len(p2):
        raise IndexError("They should have the same length")

    x = p1[0] - p2[0]
    y = p1[1] - p2[1]

    # TODO: this branching is dumb now. fix
    if len(p1) == 2:
        return DistVector3D(vector_length((x, y)), [x, y, p2[2] if len(p2) == 3 else 0])

    z = p1[2] - p2[0]

    if len(p1) == 3 and len(p2) == 3:
        # TODO: type properly
        vector = [x, y, z]
        distance = vector_length(vector)
        distance_to_border: float | None = (
            distance + diameter_p2 if diameter_p2 else distance
        )
        return DistVector3D(
            distance=distance,
            vector=vector,
            distance_to_border=distance_to_border,
        )

    return DistVector3D(0, [0, 0, 0])
