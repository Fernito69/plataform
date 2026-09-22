import math
from typing import TYPE_CHECKING

from constants import ALMOST_ZERO, HALF_PIXEL, PI
from factories.theme import White
from model.base import PointF, VectorF
from model.theme import RGB, Theme
from physics2d.model.shared import RenderInfo
from physics2d.shape.base import Shape
from utils import (
    GetLineEquationResponse,
    distance_from_line_to_point,
    get_line_equations,
)

if TYPE_CHECKING:
    from physics2d.physics2d import Physics2D


class Line(Shape):
    points: tuple[PointF, PointF]
    thickness: float

    _pulsate_freq: float
    _pulsate_amplitude: float

    def __init__(
        self,
        points: tuple[PointF, PointF],
        theme: Theme,
        engine: "Physics2D",
        thickness: float = 1,
        secondary_theme: Theme | None = None,
        angle: float = 0,
        affected_by_gravity: bool = False,
        initial_velocity: VectorF = VectorF(0, 0),
        initial_angular_velocity: float = 0,
        own_gravity: float | None = None,
        floating_multi: float = 0,
        density: float = 1,
        render_behind_player: bool = False,
        pulsate_freq: float = 0,
        pulsate_amplitude: float = 0,
        name: str = "Line",
    ):
        self.points = points
        self.thickness = thickness
        self.density = density
        self.volume = abs(points[0] - points[1]) * thickness
        self.weight = self.volume * density
        self.render_behind_player = render_behind_player
        self._pulsate_freq = pulsate_freq
        self._pulsate_amplitude = pulsate_amplitude

        self.update_center_of_mass()
        super().__init__(
            engine=engine,
            theme=theme,
            angle=angle,
            affected_by_gravity=affected_by_gravity,
            initial_velocity=initial_velocity,
            initial_angular_velocity=initial_angular_velocity,
            own_gravity=own_gravity,
            secondary_theme=secondary_theme,
            floating_multi=floating_multi,
            center_of_mass=self.center_of_mass,
            name=name,
            volume=self.volume,
            density=density,
        )

    def update_center_of_mass(self) -> None:
        self.center_of_mass = PointF(
            (self.points[0].x + self.points[1].x) / 2,
            (self.points[0].y + self.points[1].y) / 2,
        )

    def do_your_thing(self) -> None:
        self._pulsate()
        return super().do_your_thing()

    def _move_by(self, vector: VectorF) -> None:
        self.points = (self.points[0] + vector, self.points[1] + vector)

    def would_collide_with(self, colliding_shape: Shape):
        if not self.is_collideable or not colliding_shape.is_collideable:
            return
        # TODO: implement

    def get_render_info(self) -> list[RenderInfo]:
        piece_info = []
        min_x, max_x = sorted(
            (
                self.points[0].x,
                self.points[1].x,
            )
        )
        min_y, max_y = sorted(
            (
                self.points[0].y,
                self.points[1].y,
            )
        )

        eq = self._get_equations()
        x_range = range(math.floor(min_x - self.thickness), math.ceil(max_x + self.thickness))

        for x in x_range:
            # get y_range:
            prev_y = eq.get_y(x - self.thickness)
            next_y = eq.get_y(x + self.thickness)
            local_min_y = max(min_y, (min(prev_y, next_y)))
            local_max_y = min(max_y, (max(prev_y, next_y)))

            # y_range = range(math.floor(min_y - self.thickness), math.ceil(max_y + self.thickness))
            y_range = range(
                math.floor(local_min_y - self.thickness), math.ceil(local_max_y + self.thickness)
            )

            for y in y_range:
                distance = distance_from_line_to_point(
                    self.points, PointF(x + HALF_PIXEL, y + HALF_PIXEL)
                ).distance

                if distance > self.thickness:
                    continue

                piece_info.append(
                    RenderInfo(
                        distance_to_pixel_center=distance / (abs(self.thickness) or ALMOST_ZERO),
                        color=self._get_color(x, y),
                        point=PointF(x, y),
                    )
                )

        return piece_info

    def _rotate(self) -> None:
        new_angle = 0
        if self.angular_velocity != 0:
            distance_from_center_to_farthest_point = abs(self.center_of_mass - self.points[0])
            new_angle = self.angular_velocity / (
                distance_from_center_to_farthest_point or ALMOST_ZERO
            )

        if not new_angle:
            return

        new_angle = math.radians(new_angle)

        self.points = (
            self.points[0].rotate(new_angle, self.center_of_mass),
            self.points[1].rotate(new_angle, self.center_of_mass),
        )
        self.angle = new_angle

    def is_in_hitbox_area(self, point: PointF, offset: float = 0) -> bool:
        p1, p2 = self.points
        x1, x2 = sorted((p1.x, p2.x))
        y1, y2 = sorted((p1.y, p2.y))
        total_offset = self.thickness + offset
        return (
            point.x >= x1 - total_offset
            and point.x <= x2 + total_offset
            and point.y >= y1 - total_offset
            and point.y <= y2 + total_offset
        )

    _pulsate_counter: float = 0

    def _pulsate(self) -> None:
        if self._pulsate_freq == 0 or self._pulsate_amplitude == 0:
            return

        self._pulsate_counter = (self._pulsate_counter + self._pulsate_freq) % (2 * PI)
        self.thickness += math.sin(self._pulsate_counter) * self._pulsate_amplitude

    def _get_color(self, x: int | None = None, y: int | None = None) -> RGB:
        if not self.secondary_theme:
            return self.theme.color or White()

        # check which direction is the widest (literally the same as rectangle)
        vertex_1, vertex_2 = self.points
        width = abs(vertex_1.x - vertex_2.x)
        height = abs(vertex_1.y - vertex_2.y)

        apply_gradient_horizontally: bool = width >= height
        if (
            apply_gradient_horizontally
            and x is None
            or not apply_gradient_horizontally
            and y is None
        ):
            raise IndexError("What's wrong with you?")

        color_ratio: float = (
            abs(vertex_1.x - x) / width
            if apply_gradient_horizontally and x is not None
            else abs(vertex_1.y - y) / height
            if y is not None
            else 0
        )

        color: RGB = (
            (self.theme.color or White())
            .with_intensity(color_ratio)
            .mix_with((self.secondary_theme.color or White()).with_intensity(1 - color_ratio))
        )

        return color

    def _get_equations(self) -> GetLineEquationResponse:
        return get_line_equations(self.points[0], self.points[1])

    def _apply_movement(self) -> None:
        self._float_around()
        self._rotate()
        self._pulsate()

        if not any(a != 0 for a in self.velocity):
            return

        self.points = (
            (self.points[0] + self.velocity),
            (self.points[1] + self.velocity),
        )
        self.update_center_of_mass()
