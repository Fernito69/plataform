from typing import TYPE_CHECKING

from model.base import PointF, VectorF
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
        factor: float = 1,
        letter_color: RGB = RGB(),
        thickness: float = 1,
        thickness_gradient_threshold: float = 0.5,
        initial_velocity: VectorF = VectorF(0, 0),
        pulsate_freq: float = 0,
        pulsate_amplitude: float = 0,
    ):
        self.theme = Theme(letter_color)
        self.position = position
        self.engine = engine
        self.factor = factor
        self.thickness = thickness
        self.thickness_gradient_threshold = thickness_gradient_threshold
        self.velocity = initial_velocity
        self.pulsate_freq = pulsate_freq
        self.pulsate_amplitude = pulsate_amplitude

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
            if _character_vertices.get(letter, None) is not None:
                shapes += self._coords_to_lines(
                    _character_vertices[letter],
                    letter_idx,
                    offset_by_char_height,
                    extra_offset,
                )

        return shapes

    def _coords_to_lines(
        self,
        letter_pointss: list[list[PointF]],
        letter_idx: int,
        offset_by_char_height: bool,
        extra_offset: PointF,
    ) -> list["Shape"]:
        shapes: list["Shape"] = []

        for letter_points in letter_pointss:
            shapes += [
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
        return shapes

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
                y=self._get_char_height() / 2,
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
            initial_velocity=self.velocity,
            pulsate_amplitude=self.pulsate_amplitude,
            pulsate_freq=self.pulsate_freq,
        )


"""
# Letter data
"""

SPACE_BETWEEN_LETTERS = 2
UPPERCASE_CHAR_HEIGHT = 8
LOWERCASE_CHAR_HEIGHT = 6

CHAR_WIDTH = 4

_A = [
    PointF(0, 0),
    PointF(2, 8),
    PointF(4, 0),
    PointF(0.5, 2),
]
_a = [
    PointF(0, 0),
    PointF(2, 6),
    PointF(4, 0),
    PointF(0.5, 1.5),
]

_B = [
    PointF(0, 4),
    PointF(0, 0),
    PointF(2, 0),
    PointF(4, 1),
    PointF(4, 3),
    PointF(2, 4),
    PointF(0, 4),
    PointF(0, 8),
    PointF(2, 8),
    PointF(4, 7),
    PointF(4, 5),
    PointF(2, 4),
]
_b = [
    PointF(0, 0),
    PointF(0, 2),
    PointF(2, 0),
    PointF(4, 1),
    PointF(4, 3),
    PointF(2, 4),
    PointF(0, 2),
    PointF(0, 6),
]

_C = [
    PointF(4, 0),
    PointF(1, 0),
    PointF(0, 1),
    PointF(0, 6),
    PointF(2, 8),
    PointF(3, 8),
    PointF(4, 7),
]
_c = [
    PointF(4, 0),
    PointF(1, 0),
    PointF(0, 1),
    PointF(0, 5),
    PointF(1, 6),
    PointF(3, 6),
    PointF(4, 5),
]

_D = [
    PointF(0, 0),
    PointF(3, 0),
    PointF(4, 1),
    PointF(4, 6),
    PointF(2, 8),
    PointF(0, 8),
    PointF(0, 2),
]
_d = [PointF(4 - p.x, p.y) for p in _b]

_E_1 = [
    PointF(4, 0),
    PointF(1, 0),
    PointF(0, 1),
    PointF(0, 8),
    PointF(4, 8),
]
_E_2 = [
    PointF(4, 4),
    PointF(1, 4),
]
_e = [
    PointF(4, 0),
    PointF(1, 0),
    PointF(0, 1),
    PointF(0, 5),
    PointF(1, 6),
    PointF(3, 6),
    PointF(4, 5),
    PointF(4, 3),
    PointF(1, 3),
]
_f_1 = [
    PointF(1, 0),
    PointF(1, 5),
    PointF(2, 6),
    PointF(4, 6),
]
_f_2 = [
    PointF(0, 3),
    PointF(3, 3),
]
_F_1 = [
    PointF(0, 0),
    PointF(0, 7),
    PointF(1, 8),
    PointF(4, 8),
]
_F_2 = [
    PointF(4, 4),
    PointF(1, 4),
]
_G = [
    PointF(3, 3),
    PointF(4, 3),
    PointF(4, 0),
    PointF(1, 0),
    PointF(0, 1),
    PointF(0, 6),
    PointF(2, 8),
    PointF(3, 8),
    PointF(4, 7),
]
_g = [
    PointF(3, 2),
    PointF(4, 2),
    PointF(4, 0),
    PointF(1, 0),
    PointF(0, 1),
    PointF(0, 4),
    PointF(2, 6),
    PointF(3, 6),
    PointF(4, 5),
]
_H_1 = [
    PointF(0, 0),
    PointF(0, 8),
]
_H_2 = [
    PointF(4, 0),
    PointF(4, 8),
]
_H_3 = [
    PointF(1, 4),
    PointF(3, 4),
]
_h_1 = [
    PointF(0, 0),
    PointF(0, 6),
]
_h_2 = [
    PointF(0, 3),
    PointF(3, 3),
    PointF(4, 2),
    PointF(4, 0),
]


_I = [
    PointF(1, 8),
    PointF(2, 8),
    PointF(2, 0),
    PointF(3, 0),
]
_i_1 = [
    PointF(1, 4),
    PointF(2, 4),
    PointF(2, 0),
    PointF(3, 0),
]
_i_2 = [
    PointF(2, 6),
    PointF(2, 5.9),
]

_J = [
    PointF(0, 0),
    PointF(2, 0),
    PointF(4, 2),
    PointF(4, 8),
    PointF(3, 8),
]
_j_1 = [
    PointF(0, 0),
    PointF(1, 0),
    PointF(2, 1),
    PointF(2, 4),
    PointF(1, 4),
]
_j_2 = [
    PointF(2, 6),
    PointF(2, 5.9),
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
_0_1 = [
    PointF(0, 2),
    PointF(4, 6),
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

_R = [
    PointF(0, 0),
    PointF(0, 8),
    PointF(2, 8),
    PointF(4, 6),
    PointF(4, 5),
    PointF(3, 4),
    PointF(0, 4),
    PointF(4, 0),
]
_r_pt1 = [
    PointF(0, 0),
    PointF(0, 6),
]
_r_pt2 = [
    PointF(0, 5),
    PointF(4, 6),
]

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

_1 = [
    PointF(2, 0),
    PointF(2, 8),
    PointF(1, 6),
]
_character_vertices: dict[str, list[list[PointF]]] = {
    # Letters
    "A": [_A],
    "a": [_a],
    "B": [_B],
    "b": [_b],
    "C": [_C],
    "c": [_c],
    "D": [_D],
    "d": [_d],
    "E": [_E_1, _E_2],
    "e": [_e],
    "F": [_F_1, _F_2],
    "f": [_f_1, _f_2],
    "G": [_G],
    "g": [_g],
    "H": [_H_1, _H_2, _H_3],
    "h": [_h_1, _h_2],
    "I": [_I],
    "i": [_i_1, _i_2],
    "J": [_J],
    "j": [_j_1, _j_2],
    "O": [_O],
    "o": [_o],
    "R": [_R],
    "r": [_r_pt1, _r_pt2],
    "S": [_S],
    "s": [_s],
    # Numbers
    "0": [_0_1, _O],
    "1": [_1],
    # Symbols
    " ": [],
}
