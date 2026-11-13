from typing import TYPE_CHECKING

from model.base import PointF, VectorF
from model.theme import RGB, Theme
from physics2d.pickable.base import Pickable
from physics2d.shape.model.shared import TransitionType
from physics2d.shape.particle.circular_particle import CircularParticle
from physics2d.shape.text import Text
from utils import random_offset

if TYPE_CHECKING:
    from physics2d.entities.base import PhysicsEntity
    from physics2d.entities.model.shared import ParticleGenerator
    from physics2d.physics2d import Physics2D
    from physics2d.shape.base import Shape

_HEALTH_COLOR = RGB(0, 255, 0)


def _particles(color: RGB, life_time: int) -> "ParticleGenerator":
    def _p(engine: "Physics2D", source: "PhysicsEntity") -> None:
        pieces: list[Shape] = []

        for _ in range(1):
            # little particles doing particle stuff
            challita = CircularParticle(
                origin=(source.center + VectorF.random_offset_vector(source.radius * 2)),
                size=1 + random_offset(),
                initial_color=color,
                ending_color=color.copy(opacity=0.1),
                life_time=life_time,
                floating_multi=0.7,
                engine=engine,
                gravity=-0.06,
            )
            pieces.append(challita)

        engine.scenario.bg_shapes += pieces

    return _p


#####


class HealthPickup(Pickable):
    _amount: int

    def __init__(
        self,
        engine: "Physics2D",
        position: PointF,
        amount: int,
    ) -> None:
        self._amount = amount
        size = amount**0.333
        scale_factor = size / 6
        thickness = scale_factor * 0.7

        text = Text(
            engine=engine,
            position=position + PointF(0.5, -0.5),
            text_color=_HEALTH_COLOR.get_gradient(RGB(255, 255, 255)),
            scale_factor=scale_factor,
            thickness=thickness,
            pulsate_freq=0.5,
            pulsate_amplitude=0.3,
            # initial_velocity=PointF(0.1, 0.12121221).as_vector(),
        )

        super().__init__(
            engine,
            theme=Theme(_HEALTH_COLOR.copy(opacity=0.5)),
            secondary_theme=Theme(0.1 * _HEALTH_COLOR.copy(opacity=0.5)),
            color_gradient_exponent_end=0,
            color_gradient_exponent=1,
            size=size,
            position=position,
            particle_generator=_particles(_HEALTH_COLOR, size),
            extra_shapes=text.generate("+"),
            pickup_message=f"+{amount}",
        )

    def _grant_player_something(self) -> None:
        self.engine.player.grant_health(self._amount)

    def _pick_up_effect(self) -> None:
        self.engine.scenario.bg_shapes.append(
            CircularParticle(
                origin=self,
                size=0.3,
                size_change_type=TransitionType.LINEAR_INCREASE,
                initial_color=_HEALTH_COLOR,
                ending_color=_HEALTH_COLOR.copy(opacity=0.01),
                life_time=round(self.size * 3),
                final_radius=self.size * 2,
                engine=self.engine,
                particle_generator=_particles(_HEALTH_COLOR, round(self.size * 2)),
            )
        )


#############################################################
