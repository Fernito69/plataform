import math
from dataclasses import dataclass
from typing import TYPE_CHECKING, Callable

from constants import PI
from model.base import PointF, VectorF
from model.theme import RGB, Theme
from physics2d.model.shared import RenderInfo
from physics2d.shapes.line import Line
from physics2d.shapes.shape import Shape
from utils import distance_from_line_to_point, get_line_angle

if TYPE_CHECKING:
    from physics2d.physics2d import Physics2D


@dataclass
class GetCircunferenceEquationResponse:
    get_ys: Callable[[float], tuple[float, float] | tuple[None, None]]
    get_xs: Callable[[float], tuple[float, float] | tuple[None, None]]


# TODO: this shouldn't be hardcoded, should be associated to friction coef
_DECEL_FACTOR = 0.2


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
        density: float = 1,
    ):
        self.center = center
        self.radius = radius
        self.update_center_of_mass()
        self.density = density
        self.volume = PI * (self.radius**2)
        self.weight = self.volume * self.density
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
            volume=self.volume,
            density=self.density,
        )

    # TODO: unify with PlayerBlob
    def _apply_friction(self) -> None:
        if self.velocity.y > 0:
            self.velocity = (self.velocity + VectorF(0, -_DECEL_FACTOR)).as_vector()
        if self.velocity.y < 0:
            self.velocity = (self.velocity + VectorF(0, _DECEL_FACTOR)).as_vector()
        if self.velocity.x > 0:
            self.velocity = (self.velocity + VectorF(-_DECEL_FACTOR, 0)).as_vector()
        if self.velocity.x < 0:
            self.velocity = (self.velocity + VectorF(_DECEL_FACTOR, 0)).as_vector()
        if 0 <= self.velocity.x < _DECEL_FACTOR:
            self.velocity.x = 0
        if 0 <= self.velocity.y < _DECEL_FACTOR:
            self.velocity.y = 0

    # TODO: this doesn't run, is overridden by CircunferencePiece
    def _apply_movement(self, engine: "Physics2D") -> None:
        self._float_around()

        self.would_collide_with(engine.scenario.player, engine)

        # TOOD: why enabling this prevents the player collision from working
        # for p in scenario .solid_pieces:
        #     self.would_collide_with(p)

        if not any(a != 0 for a in self.velocity):
            return

        self.center = PointF(self.center.x + self.velocity.x, self.center.y + self.velocity.y)
        self.update_center_of_mass()
        self._apply_friction()

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

    # TODO: generalize this, every entity should know what to do!
    # TODO: this should somehow return the normal of the collision point AND the theoretical point of collision
    # TODO: should should calculate ACTUAL kinetic energy transfer
    def would_collide_with(self, colliding_shape: Shape, engine: "Physics2D") -> None:
        if not self.is_collideable or not colliding_shape.is_collideable:
            return

        # TODO: this doesn't work, if velocity is too high, we get fucked
        new_pos = (0.5 * self.velocity) + self.center

        if isinstance(colliding_shape, Circunference):
            # if the distance between their centers is less than the sum of both radii, it means they would collide
            if abs(new_pos - colliding_shape.center) <= self.radius + colliding_shape.radius:
                # TODO: Ideally it's the reflection angle at the point of collision, but this works for now
                # TODO: Fix the logic of this energy transfer
                denominator = self.weight + colliding_shape.weight

                # TODO: energy transfer should consider kinetic energy e = m*v^2
                self_transfer_factor = colliding_shape.weight / denominator
                other_shape_transfer_factor = self.weight / denominator
                # self_transfer_factor = 1
                # other_shape_transfer_factor = 1
                self_transfer_factor = colliding_shape.weight / denominator
                other_shape_transfer_factor = self.weight / denominator

                # raise NotImplementedError(
                #     f"NAME: {self.name}, self factor: {self_transfer_factor}, other factor: {other_shape_transfer_factor}"
                # )
                new_velocity = (
                    (-self.velocity * self_transfer_factor)
                    + (colliding_shape.velocity * other_shape_transfer_factor)
                ).as_vector()

                engine.display.debug_log(
                    f"NAME: {self.name}, SELF CONTRI: {(-self.velocity * self_transfer_factor)}, OTHER CONTRI: {(colliding_shape.velocity * other_shape_transfer_factor)}",
                )

                self.velocity = new_velocity

        if isinstance(colliding_shape, Line):
            if (
                colliding_shape.is_in_hitbox_area(self.center, self.radius)
                and distance_from_line_to_point(colliding_shape.points, self.center).distance
                < self.radius + colliding_shape.thickness
            ):
                angle_vel = get_line_angle(self.center, new_pos)
                angle_line = get_line_angle(*colliding_shape.points)
                res_angle = angle_line + PI - angle_vel

                factor_x = 1 if self.velocity.x < 0 else -1
                factor_y = 1 if self.velocity.y < 0 else -1

                new_velocity = (
                    abs(self.velocity)
                    * VectorF(x=factor_x * math.cos(res_angle), y=factor_y * math.sin(res_angle))
                ).as_vector()
                engine.display.debug_log(
                    f"PREV VEL: {self.velocity}, NEW VEL: {new_velocity} - vel angle: {angle_vel * 180 / PI}, line angle: {angle_line * 180 / PI}, res: {res_angle * 180 / PI}"
                )

                self.velocity = new_velocity

        # TODO: add the other shapes
