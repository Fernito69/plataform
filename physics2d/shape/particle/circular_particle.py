import math
from typing import TYPE_CHECKING

from constants import ALMOST_ZERO
from model.base import PointF, VectorF
from model.theme import RGB, Theme
from physics2d.entities.base import PhysicsEntity
from physics2d.entities.model.shared import ParticleGenerator
from physics2d.shape.model.shared import TransitionType
from physics2d.shape.particle.base import Particle

if TYPE_CHECKING:
    from physics2d.physics2d import Physics2D


class CircularParticle(Particle, PhysicsEntity):
    origin: PointF | PhysicsEntity
    size: float

    source: PhysicsEntity | None

    _initial_radius: float
    _final_radius: float

    _initial_x_factor: float
    _final_x_factor: float | None
    _initial_y_factor: float
    _final_y_factor: float | None

    _x_elliptical_oscillation_frequency: float | None
    _y_elliptical_oscillation_frequency: float | None

    def __init__(
        self,
        origin: PointF | PhysicsEntity,
        size: float,
        initial_color: RGB,
        engine: "Physics2D",
        x_stretching_factor: float = 1,
        y_stretching_factor: float = 1,
        final_x_stretching_factor: float | None = None,
        final_y_stretching_factor: float | None = None,
        initial_velocity: VectorF = VectorF(0, 0),
        gravity: float | None = None,
        ending_color: RGB | None = None,
        life_time: int | None = None,
        size_change_type: TransitionType = TransitionType.NONE,
        ending_color_fade_type: TransitionType = TransitionType.LINEAR_DECREASE,
        floating_multi: float = 0,
        is_collideable: bool = False,
        particle_generator: ParticleGenerator | None = None,
        density: float = 1,
        final_radius: float | None = None,
        offset_from_origin: VectorF = VectorF(0, 0),
        x_elliptical_oscillation_frequency: float | None = None,
        y_elliptical_oscillation_frequency: float | None = None,
        initial_angular_velocity: float = 0,
        name="Particle",
    ):
        self._engine = engine
        self.life_time = life_time
        self._original_life_time = life_time
        self.initial_color = initial_color
        self.ending_color = ending_color
        self.ending_color_fade_type = ending_color_fade_type
        self.size_change_type = size_change_type
        self.theme = Theme(color=initial_color)
        self.secondary_theme = Theme(color=ending_color)
        self._own_gravity_accel = gravity
        self._affected_by_gravity = gravity is not None
        self.floating_multi = floating_multi
        self.velocity = initial_velocity

        self.radius = size
        self._initial_radius = self.radius
        self._final_radius = final_radius or self.radius

        self._x_elliptical_oscillation_frequency = x_elliptical_oscillation_frequency
        self._y_elliptical_oscillation_frequency = y_elliptical_oscillation_frequency

        origin = origin if isinstance(origin, PointF) else origin.position
        # TODO: why does this not seem to work?
        self.source = None if isinstance(origin, PointF) else origin

        origin = origin + offset_from_origin

        self.center = origin
        self.position = origin
        self.is_collideable = is_collideable
        self._particle_generator = particle_generator
        self.density = density
        self.name = name
        self.initial_angular_velocity = initial_angular_velocity

        super().__init__(
            initial_color=initial_color,
            ending_color=ending_color,
            ending_color_fade_type=ending_color_fade_type,
            life_time=life_time,
            size_change_type=size_change_type,
            floating_multi=floating_multi,
        )
        PhysicsEntity.__init__(
            self,
            theme=self.theme,
            secondary_theme=self.secondary_theme,
            affected_by_gravity=self._affected_by_gravity,
            own_gravity=gravity,
            floating_multi=floating_multi,
            initial_velocity=initial_velocity,
            position=origin,
            is_collideable=is_collideable,
            density=density,
            size=size * 2,
            name=name,
            engine=engine,
            particle_generator=particle_generator,
            x_stretching_factor=x_stretching_factor,
            y_stretching_factor=y_stretching_factor,
            initial_angular_velocity=initial_angular_velocity,
        )

        self.x_factor = 1 / x_stretching_factor**2
        self.y_factor = 1 / y_stretching_factor**2
        self._initial_x_factor = self.x_factor
        self._initial_y_factor = self.y_factor
        self._final_x_factor = (
            1 / (final_x_stretching_factor or ALMOST_ZERO) ** 2
            if final_x_stretching_factor is not None
            else None
        )
        self._final_y_factor = (
            1 / (final_y_stretching_factor or ALMOST_ZERO) ** 2
            if final_y_stretching_factor is not None
            else None
        )

    def _handle_life_time(self) -> None:
        # basic stuff
        if self.life_time is None or self._original_life_time is None:
            return
        self.life_time -= 1

        _life_time_factor = self.life_time / self._original_life_time

        # size changes
        match self.size_change_type:
            case TransitionType.LINEAR_DECREASE:
                # self.radius -= self.radius / (self.life_time + 1)
                self.radius = self._initial_radius * _life_time_factor
            case TransitionType.EXPONENTIAL_DECREASE:
                self.radius *= _life_time_factor
                # TODO: decomission this, starting and final size should decide this
            case TransitionType.LINEAR_INCREASE:
                self.radius = (_life_time_factor * self.radius) + (
                    (1 - _life_time_factor) * self._final_radius
                )
            case TransitionType.NONE:
                ...

        # factor changes
        if self._final_x_factor is not None and self._x_elliptical_oscillation_frequency is None:
            self.x_factor = (
                self._initial_x_factor**0.5 * _life_time_factor
                + self._final_x_factor**0.5 * (1 - _life_time_factor)
            ) ** 2
        if self._final_y_factor is not None and self._y_elliptical_oscillation_frequency is None:
            # _f = _life_time_factor**0.1
            # self.y_factor = self._initial_y_factor * _f + self._final_y_factor * (1 - _f)
            self.y_factor = (
                self._initial_y_factor**0.5 * _life_time_factor
                + self._final_y_factor**0.5 * (1 - _life_time_factor)
            ) ** 2

        # color changes
        if (
            self.ending_color
            and self.theme.color
            and self.ending_color_fade_type != TransitionType.NONE
        ):
            factor = (
                self.life_time / self._original_life_time
                if self.ending_color_fade_type == TransitionType.LINEAR_DECREASE
                else 1 - self.life_time / self._original_life_time
            )
            # ending_factor = 1 - factor
            ending_factor = 1
            self.theme.color = RGB(
                r=self.initial_color.r * factor + self.ending_color.r * ending_factor,
                g=self.initial_color.g * factor + self.ending_color.g * ending_factor,
                b=self.initial_color.b * factor + self.ending_color.b * ending_factor,
                intensity=self.initial_color.intensity * factor
                + self.ending_color.intensity * ending_factor,
                opacity=self.initial_color.opacity * factor
                + self.ending_color.opacity * ending_factor,
            )

    _ellipticallity_counter: int = 0

    def _handle_ellipticallity(self):
        if (
            self._final_x_factor is not None
            and self._x_elliptical_oscillation_frequency is not None
        ):
            _factor = (
                math.sin(
                    # TODO: make _x_elliptical_oscillation_frequency actually sync with time
                    math.radians(
                        self._ellipticallity_counter * self._x_elliptical_oscillation_frequency
                    )
                )
                ** 2
            )

            self.x_factor = self._final_x_factor * _factor + self._initial_x_factor * (1 - _factor)
        if (
            self._final_y_factor is not None
            and self._y_elliptical_oscillation_frequency is not None
        ):
            _factor = (
                math.sin(
                    # TODO: make _y_elliptical_oscillation_frequency actually sync with time
                    math.radians(
                        self._ellipticallity_counter * self._y_elliptical_oscillation_frequency
                    )
                )
                ** 2
            )

            self.y_factor = self._final_y_factor * _factor + self._initial_y_factor * (1 - _factor)

        self._ellipticallity_counter += 1

    def do_your_thing(self) -> None:
        self._apply_movement()
        self._handle_life_time()
        self._handle_ellipticallity()

    def _get_color(self, curr_idx: int, total: int) -> RGB:
        # No gradient handling for particle (for now?)
        return self.theme.color or RGB()

    def _apply_movement(self) -> None:
        if self.source:
            self.position = self.source.position
            self.center = self.position
            self._update_center_of_mass()
            return

        PhysicsEntity._apply_movement(self)
