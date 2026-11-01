from abc import abstractmethod
from typing import TYPE_CHECKING

from model.base import PointF, VectorF
from model.theme import Theme
from physics2d.entities.base import PhysicsEntity
from physics2d.entities.model.shared import ParticleGenerator

if TYPE_CHECKING:
    from physics2d.physics2d import Physics2D


class Pickable(PhysicsEntity):
    engine: "Physics2D"
    _particle_generator: ParticleGenerator | None

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
    ) -> None:
        self.engine = engine

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
        )

    def do_your_thing(self) -> None:
        super().do_your_thing()

        if self.engine.scenario.player.would_collide_with(self):
            self._pick_up()

    def _pick_up(self) -> None:
        self._grant_player_something()
        self.engine.scenario.pickables = [
            p for p in self.engine.scenario.pickables if p is not self
        ]

    @abstractmethod
    def _grant_player_something(self) -> None: ...
