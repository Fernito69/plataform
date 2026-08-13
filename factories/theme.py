from model.theme import RGB, DoubleLines, Theme

"""
COLORS
"""


# Receives a float between 0 and 1
def _normalize(v: float) -> int:
    return round(max(min(v, 1), v, 0))


# intensity can go from 0% to 100% -> 0 to 1
_DEFAULT_INTENSITY: float = 0.7


def MakeColor(
    intensity: float = _DEFAULT_INTENSITY,
    rgb_values: tuple[int, int, int] = (255, 255, 255),
):
    r = _normalize(intensity * rgb_values[0])
    g = _normalize(intensity * rgb_values[1])
    b = _normalize(intensity * rgb_values[2])

    return RGB(r, g, b)


def Green(intensity: float = _DEFAULT_INTENSITY) -> RGB:
    return MakeColor(intensity, (0, 255, 0))


def Red(intensity: float = _DEFAULT_INTENSITY) -> RGB:
    return MakeColor(intensity, (255, 0, 0))


def Yellow(intensity: float = _DEFAULT_INTENSITY) -> RGB:
    return MakeColor(intensity, (255, 255, 0))


def Blue(intensity: float = _DEFAULT_INTENSITY) -> RGB:
    return MakeColor(intensity, (0, 0, 255))


def White(intensity: float = _DEFAULT_INTENSITY) -> RGB:
    return MakeColor(intensity, (255, 255, 255))


def Cyan(intensity: float = _DEFAULT_INTENSITY) -> RGB:
    return MakeColor(intensity, (0, 255, 255))


def Magenta(intensity: float = _DEFAULT_INTENSITY) -> RGB:
    return MakeColor(intensity, (255, 0, 255))


"""
THEMES
"""
DefaultTheme = Theme(line_type=DoubleLines)

JungleTheme = Theme(
    color=Green(),
    bg_color=MakeColor(1, (120, 73, 40)),
    # TODO: split into vertical and horizontal
    custom_line_chars=[
        "▓",
        "█",
        "▓",
        "▒",
        "░",
        "░",
        "▄",
        "▀",
    ],  # "#", "@", "§", "$", "&"],
    custom_line_type="random",
)


CandyTheme = Theme(
    color=Red(),
    bg_color=MakeColor(1, (255, 212, 232)),
    custom_line_chars=[" ", "▄", "█" "▀", "▀"],
    custom_line_type="sequential",
)
