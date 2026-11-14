from abc import abstractmethod
from typing import TYPE_CHECKING

from constants import PI
from model.base import PointF, VectorF
from model.theme import BR, RGB, Theme
from physics2d.entities.base import PhysicsEntity
from physics2d.entities.model.shared import ParticleGenerator
from physics2d.shape.particle.text_particle import TextParticle

if TYPE_CHECKING:
    from physics2d.physics2d import Physics2D
    from physics2d.shape.base import Shape


class Pickable(PhysicsEntity):
    engine: "Physics2D"
    _particle_generator: ParticleGenerator | None
    extra_shapes: list["Shape"]

    pickup_message: str | None
    pickup_message_color: RGB

    def __init__(
        self,
        engine: "Physics2D",
        position: PointF,
        size: float,
        theme: Theme,
        secondary_theme: Theme | None = None,
        color_gradient_exponent: float = 1,
        color_gradient_exponent_end: float | None = None,
        color_gradient_exponent_cycling_factor: float = 5,
        angle: float = 0,
        affected_by_gravity: bool = False,
        initial_velocity: VectorF = VectorF(0, 0),
        initial_angular_velocity: float = 0,
        own_gravity: float | None = None,
        floating_multi: float = 0,
        color_cycling_factor: float = 0,
        x_stretching_factor: float = 1,
        y_stretching_factor: float = 1,
        final_x_stretching_factor: float | None = None,
        final_y_stretching_factor: float | None = None,
        x_elliptical_oscillation_frequency: float | None = None,
        y_elliptical_oscillation_frequency: float | None = None,
        particle_generator: ParticleGenerator | None = None,
        extra_shapes: list["Shape"] = [],
        pickup_message: str | None = None,
        pickup_message_color: RGB | None = None,
    ) -> None:
        self.engine = engine
        self.pickup_message = pickup_message
        self.pickup_message_color = pickup_message_color or theme.color or RGB()

        super().__init__(
            engine=engine,
            position=position,
            density=1,
            size=size,
            theme=theme,
            secondary_theme=secondary_theme,
            color_gradient_exponent=color_gradient_exponent,
            color_gradient_exponent_end=color_gradient_exponent_end,
            color_gradient_exponent_cycling_factor=color_gradient_exponent_cycling_factor,
            angle=angle,
            affected_by_gravity=affected_by_gravity,
            initial_velocity=initial_velocity,
            initial_angular_velocity=initial_angular_velocity,
            own_gravity=own_gravity,
            floating_multi=floating_multi,
            color_cycling_factor=color_cycling_factor,
            x_stretching_factor=x_stretching_factor,
            y_stretching_factor=y_stretching_factor,
            final_x_stretching_factor=final_x_stretching_factor,
            final_y_stretching_factor=final_y_stretching_factor,
            x_elliptical_oscillation_frequency=x_elliptical_oscillation_frequency,
            y_elliptical_oscillation_frequency=y_elliptical_oscillation_frequency,
            is_collideable=True,
            particle_generator=particle_generator,
            extra_shapes=extra_shapes,
        )

    def do_your_thing(self) -> None:
        super().do_your_thing()

        for shape in self.extra_shapes:
            shape.do_your_thing()

        if self.engine.scenario.player.would_collide_with(self):
            self._pick_up()

    def _pick_up(self) -> None:
        self._grant_player_something()
        self._pick_up_effect()

        self.engine.scenario.pickables = [
            p for p in self.engine.scenario.pickables if p is not self
        ]

    def _show_pickup_message(
        self,
        life_time: int | None = None,
        final_scale_factor: float | None = None,
        initial_color: RGB | None = None,
        ending_color: RGB | None = None,
    ) -> None:
        if not self.pickup_message:
            return

        scale_factor = final_scale_factor or (self.size / 5)
        life_time = life_time or int(self.size * 7)
        initial_color = initial_color or 1.5 * self.pickup_message_color
        ending_color = ending_color or self.pickup_message_color.copy(opacity=0.01)

        for row_idx, row_text in enumerate(self.pickup_message.split(BR)):
            row_height_plus_sep = 8 + 2
            text = TextParticle(
                engine=self.engine,
                position=self.position
                - PointF(
                    x=0,
                    y=scale_factor * row_height_plus_sep * row_idx,
                ),
                text=row_text,
                initial_color=initial_color,
                ending_color=ending_color,
                # ending_color=.4*self.pickup_message_color,
                thickness=1,
                # thickness_gradient_threshold=0.1,
                life_time=life_time,
                scale_factor=scale_factor / 1.7,
                final_scale_factor=scale_factor,
                initial_velocity=0.2 * self.engine.player.velocity.rotate_2d(PI / 4),
                changes_exponentially=True,
                initial_angular_velocity=0.01,
            )
            self.engine.scenario.fg_shapes[0:0] = [text]

    @abstractmethod
    def _grant_player_something(self) -> None: ...

    @abstractmethod
    def _pick_up_effect(self) -> None: ...
