import math

from factories.theme import RGB, White
from model.base import Point2F, Vector2F
from model.theme import Theme
from physics2d.model.base import RenderInfo
from physics2d.scenario.piece import ScenarioPiece
from utils import add_tuple, mix_colors, vector_length


class Rectangle(ScenarioPiece):
    vertices: tuple[Point2F, Point2F]

    def __init__(
        self,
        vertices: tuple[Point2F, Point2F],
        theme: Theme = Theme(),
        angle: float = 0,
        affected_by_gravity: bool = False,
        initial_velocity: Vector2F = (0, 0),
        own_gravity: float | None = None,
        secondary_theme: Theme | None = None,
        floating_multi: float = 0,
    ):
        self.vertices = vertices
        # TODO: refactor into findle_middle_point
        center_of_mass = (
            (self.vertices[0][0] - self.vertices[1][0]) / 2,
            (self.vertices[0][1] - self.vertices[1][1]) / 2,
        )
        super().__init__(
            name="Rectangle",
            theme=theme,
            angle=angle,
            affected_by_gravity=affected_by_gravity,
            initial_velocity=initial_velocity,
            own_gravity=own_gravity,
            secondary_theme=secondary_theme,
            floating_multi=floating_multi,
            center_of_mass=center_of_mass,
        )

    def apply_movement(self) -> None:
        self._float_around()

        if not any(a != 0 for a in self.velocity):
            return

        self.vertices = (
            add_tuple(self.vertices[0], self.velocity),
            add_tuple(self.vertices[1], self.velocity),
        )
        self.center_of_mass = (
            self.center_of_mass[0] + self.velocity[0],
            self.center_of_mass[1] + self.velocity[1],
        )

    def _get_color(self, x: int | None = None, y: int | None = None) -> RGB:
        if not self.secondary_theme:
            return self.theme.color or White()

        # check which direction is the widest

        vertex_1, vertex_2 = self.vertices
        width = abs(vertex_1[0] - vertex_2[0])
        height = abs(vertex_1[1] - vertex_2[1])

        apply_gradient_horizontally: bool = width >= height
        if (
            apply_gradient_horizontally
            and x is None
            or not apply_gradient_horizontally
            and y is None
        ):
            raise IndexError("What's wrong with you?")

        color_ratio: float = (
            abs(vertex_1[0] - x) / width
            if apply_gradient_horizontally and x is not None
            else abs(vertex_1[1] - y) / height
            if y is not None
            else 0
        )

        color: RGB = mix_colors(
            [
                (self.theme.color or White()).with_intensity(color_ratio),
                (self.secondary_theme.color or White()).with_intensity(1 - color_ratio),
            ]
        )

        return color

    def return_render_info(self) -> list[RenderInfo]:
        piece_info = []
        min_x, max_x = sorted(
            (
                self.vertices[0][0],
                self.vertices[1][0],
            )
        )
        min_y, max_y = sorted(
            (
                self.vertices[0][1],
                self.vertices[1][1],
            )
        )

        _DELTA = 1

        for x in range(math.floor(min_x), math.ceil(max_x)):
            for y in range(math.floor(min_y), math.ceil(max_y)):
                # TODO: make this with angles, it gets a bit more tricky
                if min_x > x > max_x or min_y > y > max_y:
                    continue

                distance_left_x = abs(x - min_x + 1)
                distance_right_x = abs(x - max_x)
                distance_down_y = abs(y - min_y + 1)
                distance_up_y = abs(y - max_y)

                distance_x = (
                    1 - distance_left_x
                    if distance_left_x < _DELTA
                    else 1 - distance_right_x
                    if distance_right_x < _DELTA
                    else 0
                )
                distance_y = (
                    1 - distance_up_y
                    if distance_up_y < _DELTA
                    else 1 - distance_down_y
                    if distance_down_y < _DELTA
                    else 0
                )

                piece_info.append(
                    RenderInfo(
                        distance_to_pixel_center=vector_length((distance_x, distance_y)),
                        color=self._get_color(x, y).with_intensity(),
                        point=(x, y),
                    )
                )

        return piece_info
