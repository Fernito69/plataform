import math

from constants import ALMOST_ZERO, HALF_PIXEL, PI
from factories.theme import RGB, White
from model.base import Point2F, Vector2F
from model.theme import Theme
from physics2d.model.shared import RenderInfo
from physics2d.scenario.piece import ScenarioPiece
from utils import (
    add_tuple,
    distance_between_points,
    distance_from_line_to_point,
    mix_colors,
    rotate_point,
)


class Line(ScenarioPiece):
    points: tuple[Point2F, Point2F]
    thickness: float

    _pulsate_freq: float
    _pulsate_amplitude: float

    def __init__(
        self,
        points: tuple[Point2F, Point2F],
        theme: Theme = Theme(),
        angle: float = 0,
        thickness: float = 1,
        affected_by_gravity: bool = False,
        initial_velocity: Vector2F = (0, 0),
        own_gravity: float | None = None,
        secondary_theme: Theme | None = None,
        floating_multi: float = 0,
        pulsate_freq: float = 0,
        pulsate_amplitude: float = 0,
        initial_angular_velocity: float = 0,
        name: str = "Line",
    ):
        self.points = points
        self.thickness = thickness

        self._pulsate_freq = pulsate_freq
        self._pulsate_amplitude = pulsate_amplitude

        self.update_center_of_mass()

        super().__init__(
            name=name,
            center_of_mass=self.center_of_mass,
            theme=theme,
            angle=angle,
            affected_by_gravity=affected_by_gravity,
            initial_velocity=initial_velocity,
            own_gravity=own_gravity,
            secondary_theme=secondary_theme,
            floating_multi=floating_multi,
            initial_angular_velocity=initial_angular_velocity,
        )

    _counter: float = 0

    def _pulsate(self) -> None:
        if self._pulsate_freq == 0 or self._pulsate_amplitude == 0:
            return

        self._counter = (self._counter + self._pulsate_freq) % (2 * PI)
        self.thickness += math.sin(self._counter) * self._pulsate_amplitude

    def update_center_of_mass(self) -> None:
        self.center_of_mass = (
            (self.points[0][0] + self.points[1][0]) / 2,
            (self.points[0][1] + self.points[1][1]) / 2,
        )

    def rotate(self) -> None:
        new_angle = 0
        if self.angular_velocity != 0:
            distance_from_center_to_farthest_point = distance_between_points(
                self.center_of_mass, self.points[0]
            ).distance
            new_angle = self.angular_velocity / (
                distance_from_center_to_farthest_point or ALMOST_ZERO
            )

        if not new_angle:
            return

        self.points = (
            rotate_point(self.points[0], self.center_of_mass, new_angle),
            rotate_point(self.points[1], self.center_of_mass, new_angle),
        )
        self.angle = new_angle

    def _get_color(self, x: int | None = None, y: int | None = None) -> RGB:
        if not self.secondary_theme:
            return self.theme.color or White()

        # check which direction is the widest (literally the same as rectangle)
        vertex_1, vertex_2 = self.points
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

    def apply_movement(self) -> None:
        self._float_around()
        self._pulsate()
        self.rotate()

        if not any(a != 0 for a in self.velocity):
            return

        self.points = (
            add_tuple(self.points[0], self.velocity),
            add_tuple(self.points[1], self.velocity),
        )
        self.update_center_of_mass()

    def return_render_info(self) -> list[RenderInfo]:
        piece_info = []
        min_x, max_x = sorted(
            (
                self.points[0][0],
                self.points[1][0],
            )
        )
        min_y, max_y = sorted(
            (
                self.points[0][1],
                self.points[1][1],
            )
        )

        for x in range(math.floor(min_x - self.thickness), math.ceil(max_x + self.thickness)):
            for y in range(math.floor(min_y - self.thickness), math.ceil(max_y + self.thickness)):
                distance = distance_from_line_to_point(
                    self.points, (x + HALF_PIXEL, y + HALF_PIXEL)
                ).distance

                if distance > self.thickness:
                    continue

                piece_info.append(
                    RenderInfo(
                        distance_to_pixel_center=distance / (abs(self.thickness) or ALMOST_ZERO),
                        color=self._get_color(x, y),
                        point=(x, y),
                    )
                )

        return piece_info
