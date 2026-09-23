from typing import TYPE_CHECKING

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

    _final_radius: float

    def __init__(
        self,
        origin: PointF | PhysicsEntity,
        size: float,
        initial_color: RGB,
        engine: "Physics2D",
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
        # TODO: why's this x2?
        self.radius = size * 2
        self._final_radius = final_radius or (self.radius * 2)

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

        super().__init__(
            initial_color=initial_color,
            ending_color=ending_color,
            ending_color_fade_type=ending_color_fade_type,
            life_time=life_time,
            size_change_type=size_change_type,
            floating_multi=floating_multi,
            particle_generator=particle_generator,
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
        )

    def _handle_life_time(self) -> None:
        # basic stuff
        if self.life_time is None or self._original_life_time is None:
            return
        self.life_time -= 1

        # size changes
        match self.size_change_type:
            case TransitionType.LINEAR_DECREASE:
                self.radius -= self.radius / (self.life_time + 1)
            case TransitionType.EXPONENTIAL_DECREASE:
                self.radius *= self.life_time / self._original_life_time
            case TransitionType.LINEAR_INCREASE:
                _factor = self.life_time / self._original_life_time
                self.radius = (_factor * self.radius) + ((1 - _factor) * self._final_radius)
            case TransitionType.NONE:
                ...

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
            )

    def do_your_thing(self) -> None:
        self._apply_movement()
        return super().do_your_thing()

    def _apply_movement(self) -> None:
        if self.source:
            self.position = self.source.position
            self.center = self.position
            self.update_center_of_mass()
            return
        PhysicsEntity._apply_movement(self)
