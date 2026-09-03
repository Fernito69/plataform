import math
from abc import abstractmethod
from dataclasses import dataclass
from typing import Callable

from constants import ALMOST_ZERO, HALF_PIXEL
from factories.theme import White
from model.base import PointF, VectorF
from model.theme import RGB, Theme
from physics2d.constants import DEFAULT_GRAVITY_ACCELERATION
from physics2d.model.shared import RenderInfo
from utils import distance_from_line_to_point, mix_colors, rotate_point, shuffle_list


@dataclass
class GetCircunferenceEquationResponse:
    get_ys: Callable[[float], tuple[float, float] | tuple[None, None]]
    get_xs: Callable[[float], tuple[float, float] | tuple[None, None]]


class Shape:
    name: str
    theme: Theme
    secondary_theme: Theme | None

    # in radians
    angle: float
    center_of_mass: PointF
    _affected_by_gravity: bool
    _own_gravity_accel: float | None
    velocity: VectorF
    angular_velocity: float
    # if > 0, it floats around randomly, like brownian motion
    floating_multi: float

    def __init__(
        self,
        center_of_mass: PointF,
        name: str,
        theme: Theme = Theme(),
        angle: float = 0,
        affected_by_gravity: bool = False,
        initial_velocity: VectorF = VectorF(0, 0),
        initial_angular_velocity: float = 0,
        own_gravity: float | None = None,
        secondary_theme: Theme | None = None,
        floating_multi: float = 0,
    ):
        self.theme = theme
        self.secondary_theme = secondary_theme
        self.name = name
        self.angle = angle
        self._affected_by_gravity = affected_by_gravity
        self.velocity = initial_velocity
        self._own_gravity_accel = own_gravity
        self.floating_multi = floating_multi
        self.angular_velocity = initial_angular_velocity
        self.center_of_mass = center_of_mass

    def _apply_gravity(self, gravity_accel: float = DEFAULT_GRAVITY_ACCELERATION) -> None:
        if not self._affected_by_gravity and not self._own_gravity_accel:
            return
        self.velocity = VectorF(
            self.velocity.x,
            self.velocity.y - (self._own_gravity_accel or gravity_accel),
        )

    @abstractmethod
    def get_render_info(cls) -> list[RenderInfo]:
        # Each shape should do its thing
        raise NotImplementedError(f"Shape must have a get_render_info method")

    @abstractmethod
    def would_collide(self, shape: "Shape") -> bool:
        """Determines wheter the current shape would collide with a particular shape, given their location"""

        # Each shape should do its thing
        raise NotImplementedError(f"Shape must have a would_collide method")

    @abstractmethod
    def apply_angular_momentum(self, momentum: VectorF) -> None:
        # TODO: implement
        pass

    @abstractmethod
    def update_center_of_mass(cls) -> None:
        # Each entity should do its thing
        raise NotImplementedError(
            f"{cls.name or 'UnknownPiece'} must have a calc_center_of_mass method"
        )

    @abstractmethod
    def rotate(cls) -> None:
        # Each entity should do its thing
        raise NotImplementedError(f"{cls.name or 'UnknownPiece'} must have a rotate method")

    @abstractmethod
    def _get_color(cls, x: int | None = None, y: int | None = None) -> RGB:
        # Each entity should do its thing
        raise NotImplementedError(f"{cls.name or 'UnknownPiece'} must have a _get_color method")

    def _float_around(self) -> None:
        if self.floating_multi == 0:
            return

        self.velocity = (
            self.velocity
            + VectorF(self.floating_multi * shuffle_list(), self.floating_multi * shuffle_list())
        ).as_vector()

    @abstractmethod
    def _apply_movement(cls) -> None:
        # Each entity should do its thing
        raise NotImplementedError(
            f"{cls.name or 'UnknownPiece'} must have an apply_movement method"
        )


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
    ):
        self.points = points
        self.thickness = thickness

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
        )

    def update_center_of_mass(self) -> None:
        self.center_of_mass = PointF(
            (self.points[0].x + self.points[1].x) / 2,
            (self.points[0].y + self.points[1].y) / 2,
        )

    def would_collide(self, colliding_shape: Shape) -> bool:
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


class Circunference(Shape):
    center: PointF
    radius: float

    def __init__(
        self,
        center: PointF,
        radius: float,
        theme: Theme,
        angle: float = 0,
        affected_by_gravity: bool = False,
        initial_velocity: VectorF = VectorF(0, 0),
        initial_angular_velocity: float = 0,
        own_gravity: float | None = None,
        secondary_theme: Theme | None = None,
        floating_multi: float = 0,
    ):
        self.center = center
        self.radius = radius
        self.update_center_of_mass()
        Shape.__init__(
            self,
            theme=theme,
            angle=angle,
            secondary_theme=secondary_theme,
            own_gravity=own_gravity,
            initial_angular_velocity=initial_angular_velocity,
            affected_by_gravity=affected_by_gravity,
            floating_multi=floating_multi,
            initial_velocity=initial_velocity,
            center_of_mass=self.center_of_mass,
            name="Circunference",
        )

    def _apply_movement(self) -> None:
        self._float_around()

        if not any(a != 0 for a in self.velocity):
            return
        self.center = PointF(self.center.x + self.velocity.x, self.center.y + self.velocity.y)
        self.update_center_of_mass()

    def update_center_of_mass(self) -> None:
        self.center_of_mass = self.center

    def get_circunference_equations(
        self,
    ) -> GetCircunferenceEquationResponse:
        def get_ys(x: float) -> tuple[float, float] | tuple[None, None]:
            root_arg = self.radius**2 - (x - self.center.x) ** 2
            if root_arg < 0:
                return (None, None)
            root = root_arg**0.5
            return (self.center.y - root, self.center.y + root)

        def get_xs(y: float) -> tuple[float, float] | tuple[None, None]:
            root_arg = self.radius**2 - (y - self.center.y) ** 2
            if root_arg < 0:
                return (None, None)
            root = root_arg**0.5
            return (self.center.x - root, self.center.x + root)

        return GetCircunferenceEquationResponse(get_xs=get_xs, get_ys=get_ys)

    def get_render_info(self) -> list[RenderInfo]:
        piece_info = []
        min_x, max_x = sorted(
            (
                self.center.x + self.radius,
                self.center.x - self.radius,
            )
        )
        min_y, max_y = sorted(
            (
                self.center.y + self.radius,
                self.center.y - self.radius,
            )
        )

        eq = self.get_circunference_equations()

        for x in range(math.floor(min_x - 1), math.ceil(max_x + 1)):
            y1, y2 = eq.get_ys(x)

            # TODO: here we need to do something to make the upper border render
            if y1 is None or y2 is None:
                continue

            for y in range(math.floor(min_y - 1), math.ceil(max_y + 1)):
                x1, x2 = eq.get_xs(y)

                if x1 is None or x2 is None:
                    continue

                # TODO: good proxy with good performance, but maybe can be done better
                distance = min(
                    max(
                        0,
                        y - y2,
                        y1 - y,
                    ),
                    max(
                        0,
                        x - x2,
                        x1 - x,
                    ),
                )
                if distance > 1:
                    continue

                piece_info.append(
                    RenderInfo(
                        distance_to_pixel_center=distance,
                        color=self.theme.color or RGB(255, 255, 255),
                        point=PointF(x, y),
                    )
                )

        return piece_info

    # this only makes sense if we implement textured circunferences
    def rotate(self) -> None:
        pass

    def would_collide(self, colliding_shape: Shape) -> bool:
        new_pos = self.velocity + self.center
        
        if isinstance(colliding_shape, Circunference):
            # if the distance between their centers is less than the sum of both radii, it means they would collide
            return self.radius + colliding_shape.radius >= abs(new_pos - colliding_shape.center)

        if isinstance(colliding_shape, Line):
            # TODO: implement
            return False

        return False
