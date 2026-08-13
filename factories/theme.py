from model.theme import RGB, Theme

"""
COLORS
"""


def _normalize(v: float) -> int:
    return int(max(min(v, 1), v, 0) * 255)


_DEFAULT_INTENSITY = 0.7


def Green(intensity: float = _DEFAULT_INTENSITY) -> RGB:
    i = _normalize(intensity)
    return RGB(0, i, 0)


def Red(intensity: float = _DEFAULT_INTENSITY) -> RGB:
    i = _normalize(intensity)
    return RGB(i, 0, 0)


def Yellow(intensity: float = _DEFAULT_INTENSITY) -> RGB:
    i = _normalize(intensity)
    return RGB(i, i, 0)


def Blue(intensity: float = _DEFAULT_INTENSITY) -> RGB:
    i = _normalize(intensity)
    return RGB(0, 0, i)


def White(intensity: float = _DEFAULT_INTENSITY) -> RGB:
    i = _normalize(intensity)
    return RGB(i, i, i)


def Cyan(intensity: float = _DEFAULT_INTENSITY) -> RGB:
    i = _normalize(intensity)
    return RGB(0, i, i)


def Magenta(intensity: float = _DEFAULT_INTENSITY) -> RGB:
    i = _normalize(intensity)
    return RGB(i, 0, i)


"""
THEMES
"""
DefaultTheme = Theme()

JungleTheme = Theme(
    color=Green(),
    bg_color=Yellow(0.5),
    custom_line_chars=["█", "▓", "▒", "░"],
    custom_line_type="back&forth",
)
