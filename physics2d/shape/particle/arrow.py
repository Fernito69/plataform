from typing import TYPE_CHECKING, Literal

from constants import PI
from model.base import PointF, VectorF
from model.theme import RGB, Theme
from physics2d.model.shared import BoundingBox, RenderInfo
from physics2d.shape.base import Shape
from physics2d.shape.line import Line

if TYPE_CHECKING:
    from physics2d.physics2d import Physics2D

type ArrowType = Literal["regular", "cool"]


class Arrow(Shape):
    _type: ArrowType

    def __init__(
        self,
        engine: "Physics2D",
        position: PointF,
        _type: ArrowType = "cool",
        angle: float = 0,
        scale_factor: float = 1,
        color: RGB = RGB(),
        thickness: float = 1,
        thickness_gradient_threshold: float = 0.5,
        initial_velocity: VectorF = VectorF(0, 0),
        pulsate_freq: float = 0,
        pulsate_amplitude: float = 0,
        initial_angular_velocity: float = 0,
    ):
        super().__init__(
            engine=engine,
            center_of_mass=PointF(0, 0),
            name="Arrow",
            density=1,
            volume=1,
            is_collideable=False,
            angle=angle,
            initial_angular_velocity=initial_angular_velocity,
        )

        # TODO: implement multiple lines!!!
        self._type = _type
        self.angle = angle
        self.angular_velocity = initial_angular_velocity
        self.theme = Theme(color)
        self.position = position
        self.engine = engine
        self.scale_factor = scale_factor
        self.thickness = thickness
        self.thickness_gradient_threshold = thickness_gradient_threshold
        self.velocity = initial_velocity
        self.pulsate_freq = pulsate_freq
        self.pulsate_amplitude = pulsate_amplitude

    def get_render_info(self) -> list[RenderInfo]:
        return [info for shape in self._generate_shapes() for info in shape.get_render_info()]

    def _apply_movement(self) -> None:
        if not any(a != 0 for a in self.velocity):
            return

        self.position += self.velocity
        self._update_center_of_mass()

    def _rotate(self) -> None:
        if not self.angular_velocity:
            return

        self.angle = (self.angle + self.angular_velocity) % (2 * PI)

    def do_your_thing(self) -> None:
        self._apply_movement()
        self._rotate()

    def get_bounding_box(self) -> BoundingBox | None:
        # TODO: fix this!
        return BoundingBox(
            min_x=-1000,
            max_y=+1000,
            max_x=1000,
            min_y=-100,
        )

    def _update_center_of_mass(self) -> None:
        box = self.get_bounding_box()
        if not box:
            return

        self.center_of_mass = PointF(
            x=(box.min_x + box.max_x) / 2,
            y=(box.min_y + box.max_y) / 2,
        )

    def _generate_shapes(self) -> list["Shape"]:
        shapes: list["Shape"] = []

        shapes += self._vertices_to_lines(_arrow_vertex_compendium[self._type])

        return shapes

    def _vertices_to_lines(
        self,
        list_of_vertices: list[list[PointF]],
    ) -> list["Shape"]:
        shapes: list["Shape"] = []

        for char_vertices in list_of_vertices:
            shapes += [
                self._generate_traces((vertex, char_vertices[vertex_idx + 1]))
                for vertex_idx, vertex in enumerate(char_vertices[:-1])
            ]
        return shapes

    def _generate_traces(
        self,
        points: tuple[PointF, PointF],
    ) -> "Shape":
        _char_position_offset = ARROW_SIZE * self.scale_factor
        _char_initial_position = self.position + PointF(x=_char_position_offset, y=0)
        point1 = _char_initial_position + self.scale_factor * points[0]
        point2 = _char_initial_position + self.scale_factor * points[1]

        if self.angle:
            point1 = point1.rotate_2d(self.angle, self.position)
            point2 = point2.rotate_2d(self.angle, self.position)

        return Line(
            points=(point1, point2),
            engine=self.engine,
            theme=self.theme,
            thickness=self.thickness,
            thickness_gradient_threshold=self.thickness_gradient_threshold,
            initial_velocity=self.velocity,
            pulsate_amplitude=self.pulsate_amplitude,
            pulsate_freq=self.pulsate_freq,
        )


"""
# Data
"""


ARROW_SIZE = 8

_COOL_ARROW = [
    PointF(-4, 4),
    PointF(4, 0),
]

_REGULAR_ARROW_1 = [
    PointF(-1, 4),
    PointF(4, 0),
    PointF(-1, -4),
]

_REGULAR_ARROW_2 = [
    PointF(-4, 0),
    PointF(4, 0),
]

_arrow_vertex_compendium: dict[ArrowType, list[list[PointF]]] = {
    # Letters
    "cool": [_COOL_ARROW],
    "regular": [_REGULAR_ARROW_1, _REGULAR_ARROW_2],
}
