import math
from dataclasses import dataclass
from typing import TYPE_CHECKING, Callable

from model.base import PointF, VectorF
from model.theme import RGB, Theme
from physics2d.model.shared import RenderInfo
from physics2d.shapes.shape import Shape

if TYPE_CHECKING:
    from physics2d.shapes.line import Line


@dataclass
class GetCircunferenceEquationResponse:
    get_ys: Callable[[float], tuple[float, float] | tuple[None, None]]
    get_xs: Callable[[float], tuple[float, float] | tuple[None, None]]


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
