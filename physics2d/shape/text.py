from typing import TYPE_CHECKING

from model.base import PointF, VectorF
from model.theme import RGB, Theme
from physics2d.model.shared import BoundingBox, RenderInfo
from physics2d.shape.base import Shape
from physics2d.shape.line import Line

if TYPE_CHECKING:
    from physics2d.physics2d import Physics2D


class Text(Shape):
    def __init__(
        self,
        engine: "Physics2D",
        position: PointF,
        text: str = "",
        scale_factor: float = 1,
        text_color: RGB = RGB(),
        thickness: float = 1,
        thickness_gradient_threshold: float = 0.5,
        initial_velocity: VectorF = VectorF(0, 0),
        pulsate_freq: float = 0,
        pulsate_amplitude: float = 0,
    ):
        super().__init__(
            engine=engine,
            # TODO: do properly
            center_of_mass=PointF(0, 0),
            name=text,
            density=1,
            volume=1,
            is_collideable=False,
        )

        self.text = text
        self.theme = Theme(text_color)
        self.position = position
        self.engine = engine
        self.scale_factor = scale_factor
        self.thickness = thickness
        self.thickness_gradient_threshold = thickness_gradient_threshold
        self.velocity = initial_velocity
        self.pulsate_freq = pulsate_freq
        self.pulsate_amplitude = pulsate_amplitude

    def _get_char_height(self) -> float:
        is_lowercase = self.text == self.text.lower()
        return self.scale_factor * (
            LOWERCASE_CHAR_HEIGHT if is_lowercase else UPPERCASE_CHAR_HEIGHT
        )

    def get_render_info(self) -> list[RenderInfo]:
        return [info for shape in self.generate(text=self.text) for info in shape.get_render_info()]

    def _apply_movement(self) -> None:
        if not any(a != 0 for a in self.velocity):
            return

        self.position += self.velocity

    def do_your_thing(self) -> None:
        self._apply_movement()

    def get_bounding_box(self) -> BoundingBox | None:
        min_x, max_y, _ = self.position

        return BoundingBox(
            min_x=min_x,
            max_y=max_y,
            max_x=min_x * self.scale_factor * len(self.text),
            min_y=max_y - self.scale_factor,
        )

    def _get_char_width(self) -> float:
        return CHAR_WIDTH * self.scale_factor

    def generate(
        self,
        text: str,
        offset_by_char_height: bool = True,
        extra_offset: PointF = PointF(0, 0),
    ) -> list["Shape"]:
        shapes: list["Shape"] = []
        self.text = text

        for char_idx, char in enumerate(text):
            if _char_vertex_compendium.get(char, None) is not None:
                shapes += self._vertices_to_lines(
                    _char_vertex_compendium[char],
                    char_idx,
                    offset_by_char_height,
                    extra_offset,
                )

        return shapes

    def _vertices_to_lines(
        self,
        list_of_char_vertices: list[list[PointF]],
        char_idx: int,
        offset_by_char_height: bool,
        extra_offset: PointF,
    ) -> list["Shape"]:
        shapes: list["Shape"] = []

        for char_vertices in list_of_char_vertices:
            shapes += [
                self._generate_char_trace(
                    (
                        vertex,
                        char_vertices[vertex_idx + 1],
                    ),
                    char_idx,
                    offset_by_char_height,
                    extra_offset,
                )
                for vertex_idx, vertex in enumerate(char_vertices[:-1])
            ]
        return shapes

    def _generate_char_trace(
        self,
        points: tuple[PointF, PointF],
        char_idx: int,
        offset_by_char_height: bool,
        extra_offset: PointF,
    ) -> "Shape":
        _char_position_offset = char_idx * (CHAR_WIDTH + SPACE_BETWEEN_CHARS) * self.scale_factor
        _char_initial_position = self.position + PointF(
            x=_char_position_offset + extra_offset.x,
            y=extra_offset.y,
        )
        # TODO: rethink this for text that's longer than 1 char
        if offset_by_char_height:
            _char_initial_position -= PointF(
                x=self._get_char_width() / 2,
                y=self._get_char_height() / 2,
            )

        return Line(
            points=(
                _char_initial_position + self.scale_factor * points[0],
                _char_initial_position + self.scale_factor * points[1],
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

SPACE_BETWEEN_CHARS = 2
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

_B_1 = [
    PointF(0, 0),
    PointF(3, 0),
    PointF(4, 1.5),
    PointF(4, 3),
    PointF(3, 4.5),
    PointF(0, 4.5),
    PointF(0, 0),
]
_B_2 = [
    PointF(3, 4.5),
    PointF(4, 5.5),
    PointF(4, 7),
    PointF(3, 8),
    PointF(0, 8),
    PointF(0, 4.5),
]
_b_1 = [
    PointF(0, 0),
    PointF(3, 0),
    PointF(4, 1),
    PointF(4, 2),
    PointF(3, 3),
    PointF(0, 3),
    PointF(0, 0),
]
_b_2 = [
    PointF(3, 3),
    PointF(4, 4),
    PointF(4, 5),
    PointF(3, 6),
    PointF(0, 6),
    PointF(0, 3),
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
_d = [
    PointF(0, 0),
    PointF(3, 0),
    PointF(4, 1),
    PointF(4, 5),
    PointF(2, 6),
    PointF(0, 6),
    PointF(0, 1.5),
]

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

_k_2 = [
    PointF(0, 0),
    PointF(0, 6),
]
_k_1 = [
    PointF(4, 0),
    PointF(0, 2),
    PointF(4, 4),
]
_K_2 = [
    PointF(0, 0),
    PointF(0, 8),
]
_K_1 = [
    PointF(4, 0),
    PointF(0, 4.5),
    PointF(4.5, 8),
]

_l = [
    PointF(0, 6),
    PointF(0, 0.5),
    PointF(0.5, 0),
    PointF(4, 0),
]

_L = [
    PointF(0, 8),
    PointF(0, 1),
    PointF(1, 0),
    PointF(4, 0),
]

_m = [
    PointF(0, 0),
    PointF(0, 6),
    PointF(2, 4),
    PointF(4, 6),
    PointF(4, 0),
]

_M = [
    PointF(0, 0),
    PointF(0, 8),
    PointF(2, 5),
    PointF(4, 8),
    PointF(4, 0),
]

_n = [
    PointF(0, 0),
    PointF(0, 6),
    PointF(4, 0),
    PointF(4, 6),
]

_N = [
    PointF(0, 0),
    PointF(0, 8),
    PointF(4, 0),
    PointF(4, 8),
]

_ñ_2 = [
    PointF(1, 7),
    PointF(3, 7),
]

_Ñ_2 = [
    PointF(1, 9),
    PointF(3, 9),
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


_P = [
    PointF(0, 0),
    PointF(0, 8),
    PointF(2.5, 8),
    PointF(4, 6.5),
    PointF(4, 5.5),
    PointF(2.5, 4),
    PointF(1, 4),
]
_p = [
    PointF(0, 0),
    PointF(0, 6),
    PointF(3, 6),
    PointF(4, 5),
    PointF(4, 4),
    PointF(3, 3),
    PointF(1, 3),
]

_q_2 = [
    PointF(2, 1.5),
    PointF(3, -1.5),
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

_T_1 = [
    PointF(2, 0),
    PointF(2, 8),
]
_T_2 = [
    PointF(0, 8),
    PointF(4, 8),
]
_t_1 = [
    PointF(2, 0),
    PointF(2, 6),
]
_t_2 = [
    PointF(0, 6),
    PointF(4, 6),
]

_U = [
    PointF(0, 8),
    PointF(0, 1.5),
    PointF(1, 0),
    PointF(3, 0),
    PointF(4, 1.5),
    PointF(4, 8),
]
_u = [
    PointF(0, 6),
    PointF(0, 1),
    PointF(1, 0),
    PointF(3, 0),
    PointF(4, 1),
    PointF(4, 6),
]

_V = [
    PointF(0, 8),
    PointF(2, 0),
    PointF(4, 8),
]
_v = [
    PointF(0, 6),
    PointF(2, 0),
    PointF(4, 6),
]

_W = [
    PointF(0, 8),
    PointF(1, 0),
    PointF(2, 4),
    PointF(3, 0),
    PointF(4, 8),
]
_w = [
    PointF(0, 6),
    PointF(1, 0),
    PointF(2, 3),
    PointF(3, 0),
    PointF(4, 6),
]

_X_1 = [
    PointF(0, 8),
    PointF(4, 0),
]
_X_2 = [
    PointF(4, 8),
    PointF(0, 0),
]

_x_1 = [
    PointF(0, 6),
    PointF(4, 0),
]
_x_2 = [
    PointF(4, 6),
    PointF(0, 0),
]

_Y_1 = [
    PointF(0, 8),
    PointF(2, 4.5),
    PointF(4, 8),
]
_Y_2 = [
    PointF(2, 0),
    PointF(2, 4),
]

_y_1 = [
    PointF(0, 6),
    PointF(2, 3.5),
    PointF(4, 6),
]
_y_2 = [
    PointF(2, 0),
    PointF(2, 3),
]

_Z = [
    PointF(0, 8),
    PointF(4, 8),
    PointF(0, 0),
    PointF(4, 0),
]

_z = [
    PointF(0, 6),
    PointF(4, 6),
    PointF(0, 0),
    PointF(4, 0),
]

_APOSTROPHE = [
    PointF(3, 8),
    PointF(2.5, 6.5),
]

_DOT = [
    PointF(2, 0),
    PointF(2, 0.1),
]

_COMMA = [
    PointF(2, 0),
    PointF(1, -2),
]

_EXCLAMATION_MARK_1 = [
    PointF(2, 2),
    PointF(2, 8),
]

_EXCLAMATION_MARK_2 = [
    PointF(2, 0),
    PointF(2, 0.1),
]

_PLUS_1 = [
    PointF(0, 4),
    PointF(4, 4),
]

_PLUS_2 = [
    PointF(2, 6),
    PointF(2, 2),
]


_1 = [
    PointF(3, 0),
    PointF(3, 8),
    PointF(2, 6),
]

_2 = [
    PointF(4, 0),
    PointF(0, 0),
    PointF(4, 4),
    PointF(4, 6.5),
    PointF(2.5, 8),
    PointF(1.5, 8),
    PointF(0, 6.5),
]

_3 = [
    PointF(0, 7),
    PointF(1, 8),
    PointF(3, 8),
    PointF(4, 7),
    PointF(4, 5),
    PointF(2.5, 4),
    PointF(4, 3),
    PointF(4, 1),
    PointF(3, 0),
    PointF(1, 0),
    PointF(0, 1),
]

_4 = [
    PointF(4, 0),
    PointF(4, 8),
    PointF(0, 3),
    PointF(4, 3),
]

_5 = [
    PointF(4, 8),
    PointF(0, 8),
    PointF(0, 4),
    PointF(1, 5),
    PointF(3, 5),
    PointF(4, 4),
    PointF(4, 1),
    PointF(3, 0),
    PointF(1, 0),
    PointF(0, 1),
]

_6 = [
    PointF(4, 8),
    PointF(2, 8),
    PointF(0, 6),
    PointF(0, 1),
    PointF(1, 0),
    PointF(3, 0),
    PointF(4, 1),
    PointF(4, 3),
    PointF(3, 4),
    PointF(0, 4),
]

_7 = [
    PointF(0, 8),
    PointF(4, 8),
    PointF(1, 0),
]

_8 = [
    PointF(1, 0),
    PointF(3, 0),
    PointF(4, 1),
    PointF(4, 3),
    PointF(0, 5),
    PointF(0, 7),
    PointF(1, 8),
    PointF(3, 8),
    PointF(4, 7),
    PointF(4, 5),
    PointF(0, 3),
    PointF(0, 1),
    PointF(1, 0),
]
_9 = [PointF(4 - p.x, 8 - p.y) for p in _6]

_char_vertex_compendium: dict[str, list[list[PointF]]] = {
    # Letters
    "A": [_A],
    "a": [_a],
    "B": [_B_1, _B_2],
    "b": [_b_1, _b_2],
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
    "K": [_K_1, _K_2],
    "k": [_k_1, _k_2],
    "L": [_L],
    "l": [_l],
    "M": [_M],
    "m": [_m],
    "N": [_N],
    "n": [_n],
    "Ñ": [_N, _Ñ_2],
    "ñ": [_n, _ñ_2],
    "O": [_O],
    "o": [_o],
    "P": [_P],
    "p": [_p],
    "Q": [_q_2, _O],
    "q": [_q_2, _o],
    "R": [_R],
    "r": [_r_pt1, _r_pt2],
    "S": [_S],
    "s": [_s],
    "T": [_T_1, _T_2],
    "t": [_t_1, _t_2],
    "U": [_U],
    "u": [_u],
    "V": [_V],
    "v": [_v],
    "W": [_W],
    "w": [_w],
    "X": [_X_1, _X_2],
    "x": [_x_1, _x_2],
    "Y": [_Y_1, _Y_2],
    "y": [_y_1, _y_2],
    "Z": [_Z],
    "z": [_z],
    # Numbers
    "0": [_0_1, _O],
    "1": [_1],
    "2": [_2],
    "3": [_3],
    "4": [_4],
    "5": [_5],
    "6": [_6],
    "7": [_7],
    "8": [_8],
    "9": [_9],
    # Symbols
    " ": [],
    "'": [_APOSTROPHE],
    ".": [_DOT],
    ",": [_COMMA],
    "!": [_EXCLAMATION_MARK_1, _EXCLAMATION_MARK_2],
    "+": [_PLUS_1, _PLUS_2],
}

"""
Dedicated to my friend and mentor Jared. It is through your always thoughtful advice that I've been able to develop the skills to make this even possible
"""
