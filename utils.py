from model.shared import Number
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
    orig: tuple[Number, Number, Number], add: tuple[Number, Number, Number]
) -> tuple[Number, Number, Number]:
    return (orig[0] + add[0], orig[1] + add[1], orig[2] + add[2])
