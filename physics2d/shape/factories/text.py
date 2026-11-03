from typing import TYPE_CHECKING

from model.base import PointF
from model.theme import RGB, Theme
from physics2d.shape.line import Line

if TYPE_CHECKING:
    from physics2d.physics2d import Physics2D
    from physics2d.shape.base import Shape


class Text:
    def __init__(
        self,
        engine: "Physics2D",
        position: PointF,
        factor: float = 1.7,
        letter_color: RGB = RGB(),
        thickness: float = 1,
        thickness_gradient_threshold: float = 0.5,
    ):
        self.theme = Theme(letter_color)
        self.position = position
        self.engine = engine
        self.factor = factor
        self.thickness = thickness
        self.thickness_gradient_threshold = thickness_gradient_threshold

    def _get_char_height(self) -> float:
        is_lowercase = self._text == self._text.lower()
        return (LOWERCASE_CHAR_HEIGHT if is_lowercase else UPPERCASE_CHAR_HEIGHT) * self.factor

    def _get_char_width(self) -> float:
        return CHAR_WIDTH * self.factor

    """"""
    _text: str

    def get_text(
        self,
        text: str,
        offset_by_char_height: bool = True,
        extra_offset: PointF = PointF(0, 0),
    ) -> list["Shape"]:
        shapes: list["Shape"] = []
        self._text = text

        for letter_idx, letter in enumerate(text):
            if _letter_points.get(letter, None) is not None:
                shapes += self._coords_to_lines(
                    _letter_points[letter],
                    letter_idx,
                    offset_by_char_height,
                    extra_offset,
                )

        return shapes

    def _coords_to_lines(
        self,
        letter_points: list[PointF],
        letter_idx: int,
        offset_by_char_height: bool,
        extra_offset: PointF,
    ) -> list["Shape"]:
        # TODO: this assumes letters are always made of consecutive lines! must be fixed
        return [
            self._make_line(
                (
                    point,
                    letter_points[point_idx + 1],
                ),
                letter_idx,
                offset_by_char_height,
                extra_offset,
            )
            for point_idx, point in enumerate(letter_points[:-1])
        ]

    def _make_line(
        self,
        points: tuple[PointF, PointF],
        letter_idx: int,
        offset_by_char_height: bool,
        extra_offset: PointF,
    ) -> "Shape":
        _offset = letter_idx * (CHAR_WIDTH + SPACE_BETWEEN_LETTERS) * self.factor
        _letter_initial_position = self.position + PointF(
            x=_offset + extra_offset.x,
            y=extra_offset.y,
        )
        if offset_by_char_height:
            _letter_initial_position -= PointF(
                x=self._get_char_width() / 2,
                y=self._get_char_height() / 2 - 1,
            )

        return Line(
            points=(
                _letter_initial_position + self.factor * points[0],
                _letter_initial_position + self.factor * points[1],
            ),
            engine=self.engine,
            theme=self.theme,
            thickness=self.thickness,
            thickness_gradient_threshold=self.thickness_gradient_threshold,
        )


"""
# Letter data
"""

SPACE_BETWEEN_LETTERS = 2
UPPERCASE_CHAR_HEIGHT = 8
LOWERCASE_CHAR_HEIGHT = 6

CHAR_WIDTH = 4

_S = [
    PointF(0, 0),
    PointF(3, 0),
    PointF(4, 1),
    PointF(4, 3),
    PointF(3, 4),
    PointF(1, 4),
    PointF(0, 5),
    PointF(0, 7),
    PointF(1, 8),
    PointF(4, 8),
]
_s = [
    PointF(0, 0),
    PointF(3, 0),
    PointF(4, 1),
    PointF(4, 2),
    PointF(3, 3),
    PointF(1, 3),
    PointF(0, 4),
    PointF(0, 5),
    PointF(1, 6),
    PointF(4, 6),
]

_O = [
    PointF(1, 0),
    PointF(3, 0),
    PointF(4, 2),
    PointF(4, 6),
    PointF(3, 8),
    PointF(1, 8),
    PointF(0, 6),
    PointF(0, 2),
    PointF(1, 0),
]
_o = [
    PointF(1, 0),
    PointF(3, 0),
    PointF(4, 1),
    PointF(4, 5),
    PointF(3, 6),
    PointF(1, 6),
    PointF(0, 5),
    PointF(0, 1),
    PointF(1, 0),
]

_letter_points: dict[str, list[PointF]] = {
    "S": _S,
    "s": _s,
    "O": _O,
    "o": _o,
}
