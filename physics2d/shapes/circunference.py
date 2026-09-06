import math
from dataclasses import dataclass
from typing import TYPE_CHECKING, Callable

from constants import PI
from model.base import PointF, VectorF
from model.theme import RGB, Theme
from physics2d.model.shared import RenderInfo
from physics2d.shapes.line import Line
from physics2d.shapes.shape import Shape
from utils import (
    distance_from_line_to_point,
    get_angle_from_slope,
    get_line_angle,
    get_perpendicular_slope,
)

if TYPE_CHECKING:
    from physics2d.physics2d import Physics2D


@dataclass
class GetCircunferenceEquationResponse:
    get_ys: Callable[[float], tuple[float, float] | tuple[None, None]]
    get_xs: Callable[[float], tuple[float, float] | tuple[None, None]]


# TODO: this shouldn't be hardcoded, should be associated to friction coef
_DECEL_FACTOR = 0.2
# TODO: move to common constants place


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
        life_time: int | None = None,
    ):
        self.center = center
        self.radius = radius
        self.update_center_of_mass()
        self.density = density
        self.volume = PI * (self.radius**2)
        self.weight = self.volume * self.density
        self.life_time = life_time
        self._original_life_time = life_time
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
            life_time=life_time,
        )

    # TODO: unify with PlayerBlob
    def _apply_friction(self) -> None:
        if not self.affected_by_friction:
            return
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
        self._handle_lifetime()

        # TOOD: why enabling this prevents the player collision from working
        # for p in scenario .solid_pieces:
        #     self.would_collide_with(p)

        if not any(a != 0 for a in self.velocity):
            return

        self.center = PointF(self.center.x + self.velocity.x, self.center.y + self.velocity.y)
        self.update_center_of_mass()
        self._apply_friction()

    # TODO: implement at Shape level, and the gray color shouldn't be a setting from here, but from the Theme
    def _handle_lifetime(self) -> None:
        if self.life_time is None or self._original_life_time is None:
            return
        self.life_time -= 1
        self.radius -= self.radius / (self.life_time + 1)

        if self.theme.color:
            _smoke_like = RGB(100, 100, 100, intensity=0.1)
            _ice_like = RGB(177, 255, 255).with_intensity(
                self.life_time / (self._original_life_time or 1)
            )
            self.theme.color = self.theme.color.mix_with([self.theme.color, _ice_like])

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
        piece_info: list[RenderInfo] = []

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

        # Add "trail"
        # if is_player:
        #     for _i in range(1, int(self.radius * 2)):
        #         i = _i / 2
        #         distance_factor = (self.radius - i) * _THRUST_FIRE_DISTANCE_FACTOR
        #         eye_x = self.center.x - self.velocity.x * distance_factor
        #         eye_y = self.center.y - self.velocity.y * distance_factor

        #         is_odd = _i % 2 == 1
        #         _randomness_multi = 3 if is_odd else 1
        #         _radius_factor = 0.5 if is_odd else 1
        #         _color = (
        #             RGB(
        #                 (i - 1) * 50,
        #                 (i - 1) * 50,
        #                 255,
        #             ).with_intensity(1)
        #             if is_odd
        #             else RGB(
        #                 (i - 1) * 90,
        #                 255,
        #                 (i - 1) * 50,
        #             ).with_intensity(1)
        #         )

        #         thrust_fire = Circunference(
        #             center=PointF(
        #                 x=eye_x
        #                 + (random.random() - 0.5)
        #                 * _THRUST_FIRE_SPAWN_RANDOMNESS_FACTOR
        #                 * _randomness_multi,
        #                 y=eye_y
        #                 + (random.random() - 0.5)
        #                 * _THRUST_FIRE_SPAWN_RANDOMNESS_FACTOR
        #                 * _randomness_multi,
        #             ),
        #             initial_velocity=VectorF(
        #                 x=eye_x
        #                 + (random.random() - 0.5)
        #                 * _THRUST_FIRE_SPAWN_RANDOMNESS_FACTOR
        #                 * _randomness_multi,
        #                 y=eye_y
        #                 + (random.random() - 0.5)
        #                 * _THRUST_FIRE_SPAWN_RANDOMNESS_FACTOR
        #                 * _randomness_multi,
        #             ),
        #             # radius=i * math.cos((self.radius - i) / self.radius),
        #             radius=i * _radius_factor,
        #             # theme=Theme(color=RGB(140, (i - 1) * 50, (i - 1) * 100).with_intensity(1)),
        #             theme=Theme(color=_color),
        #             life_time=10,
        #         )

        #         piece_info.extend(thrust_fire.get_render_info())

        eq = self.get_circunference_equations()

        for x in range(math.floor(min_x - 1), math.ceil(max_x + 1)):
            y1, y2 = eq.get_ys(x)

            # TODO: here we need to do something to make the upper border render
            if y1 is None or y2 is None:
                continue

            for y in range(math.floor(min_y - 1), math.ceil(max_y + 1)):
                x1, x2 = eq.get_xs(y)

                if (
                    x1 is None or x2 is None
                    # or (
                    #     (eye_x is not None and round(eye_x) == round(x))
                    #     and (eye_y is not None and round(eye_y) == round(y))
                    # )
                ):
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
        new_pos = (0.6 * self.velocity) + self.center

        # CASE: Ball x Ball
        if isinstance(colliding_shape, Circunference):
            # if the distance between their centers is less than the sum of both radii, it means they would collide
            if abs(new_pos - colliding_shape.center) <= self.radius + colliding_shape.radius:
                # TODO: Ideally it's the reflection angle at the point of collision, but this works for now
                # TODO: Fix the logic of this energy transfer
                denominator = self.weight + colliding_shape.weight
                normal_at_collision = (self.center, colliding_shape.center)
                # only the vel. component parallel to the normal of the collision point

                # TODO: energy transfer should consider kinetic energy e = m*v^2
                self_transfer_factor = colliding_shape.weight / denominator
                other_shape_transfer_factor = self.weight / denominator
                # self_transfer_factor = 1
                # other_shape_transfer_factor = 1

                # TODO: make this a Shape property, and also affected by friction
                elastic_transfer_factor = 0.2 * abs(self.velocity)
                self_transfer_factor = (colliding_shape.weight / denominator) * (
                    1 - elastic_transfer_factor
                )

                # raise NotImplementedError(
                #     f"NAME: {self.name}, self factor: {self_transfer_factor}, other factor: {other_shape_transfer_factor}"
                # )
                # new_velocity = (
                #     (-self.velocity * other_shape_transfer_factor)
                #     + (colliding_shape.velocity * other_shape_transfer_factor)
                # ).as_vector()
                new_velocity = (
                    (colliding_shape.velocity * self_transfer_factor)
                    - (self.velocity * elastic_transfer_factor)
                ).as_vector()

                engine.display.debug_log(
                    f"NAME: {self.name}, SELF CONTRI: {(-self.velocity * self_transfer_factor)}, OTHER CONTRI: {(colliding_shape.velocity * other_shape_transfer_factor)}",
                )

                self.velocity = new_velocity

        # CASE: Line x Ball
        if isinstance(colliding_shape, Line):
            if (
                colliding_shape.is_in_hitbox_area(self.center, self.radius)
                and distance_from_line_to_point(colliding_shape.points, self.center).distance
                < self.radius + colliding_shape.thickness
            ):
                # TODO!!!!! Should be minus/plus double the difference between the normal and itself
                angle_vel = get_line_angle(self.center, new_pos)
                # angle_line = get_line_angle(*colliding_shape.points)
                line_normal_angle = get_angle_from_slope(
                    get_perpendicular_slope(*colliding_shape.points)
                )
                bounce_angle = 2 * line_normal_angle - angle_vel
                # res_angle = angle_line + PI - angle_vel

                # factor_x = -1 if self.velocity.x < 0 else 1
                # factor_y = 1 if self.velocity.y < 0 else -1
                factor_x = 1
                factor_y = 1

                new_velocity = (
                    abs(self.velocity)
                    * VectorF(
                        x=factor_x * math.cos(bounce_angle), y=factor_y * math.sin(bounce_angle)
                    )
                ).as_vector()

                def _get_angle(angle) -> int:
                    return int(angle * 180 / PI)

                engine.display.debug_log(
                    f"PREV VEL: {self.velocity}, NEW VEL: {new_velocity} - vel angle: {_get_angle(angle_vel)}, line normal: {_get_angle(line_normal_angle)}, res: {_get_angle(bounce_angle)}"
                )

                self.velocity = new_velocity

        # TODO: add the other shapes
