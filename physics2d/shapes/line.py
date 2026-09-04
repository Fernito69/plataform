import math

from constants import ALMOST_ZERO, HALF_PIXEL
from factories.theme import White
from model.base import PointF, VectorF
from model.theme import RGB, Theme
from physics2d.model.shared import RenderInfo
from physics2d.shapes.shape import Shape
from utils import distance_from_line_to_point, mix_colors, rotate_point


class Line(Shape):
    points: tuple[PointF, PointF]
    thickness: float

    def __init__(
        self,
        points: tuple[PointF, PointF],
        thickness: float,
        theme: Theme,
        secondary_theme: Theme | None = None,
        angle: float = 0,
        affected_by_gravity: bool = False,
        initial_velocity: VectorF = VectorF(0, 0),
        initial_angular_velocity: float = 0,
        own_gravity: float | None = None,
        floating_multi: float = 0,
        density: float = 1,
    ):
        self.points = points
        self.thickness = thickness
        self.density = density
        self.volume = abs(points[0] - points[1]) * thickness
        self.weight = self.volume * density

        self.update_center_of_mass()
        Shape.__init__(
            self,
            theme=theme,
            angle=angle,
            affected_by_gravity=affected_by_gravity,
            initial_velocity=initial_velocity,
            initial_angular_velocity=initial_angular_velocity,
            own_gravity=own_gravity,
            secondary_theme=secondary_theme,
            floating_multi=floating_multi,
            center_of_mass=self.center_of_mass,
            name="Line",
            volume=self.volume,
            density=density,
        )

    def update_center_of_mass(self) -> None:
        self.center_of_mass = PointF(
            (self.points[0].x + self.points[1].x) / 2,
            (self.points[0].y + self.points[1].y) / 2,
        )

    def would_collide_with(self, colliding_shape: Shape) -> bool:
        # TODO: implement
        return False

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

        for x in range(math.floor(min_x - self.thickness), math.ceil(max_x + self.thickness)):
            for y in range(math.floor(min_y - self.thickness), math.ceil(max_y + self.thickness)):
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

    def rotate(self) -> None:
        new_angle = 0
        if self.angular_velocity != 0:
            distance_from_center_to_farthest_point = abs(self.center_of_mass - self.points[0])
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

        color: RGB = mix_colors(
            [
                (self.theme.color or White()).with_intensity(color_ratio),
                (self.secondary_theme.color or White()).with_intensity(1 - color_ratio),
            ]
        )

        return color

    def _apply_movement(self) -> None:
        self._float_around()
        self.rotate()

        if not any(a != 0 for a in self.velocity):
            return

        self.points = (
            (self.points[0] + self.velocity),
            (self.points[1] + self.velocity),
        )
        self.update_center_of_mass()
