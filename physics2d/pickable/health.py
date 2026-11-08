from typing import TYPE_CHECKING

from model.base import PointF, VectorF
from model.theme import RGB, Theme
from physics2d.pickable.base import Pickable
from physics2d.shape.factories.text import Text
from physics2d.shape.particle.circular_particle import CircularParticle
from utils import random_offset

if TYPE_CHECKING:
    from physics2d.entities.base import PhysicsEntity
    from physics2d.entities.model.shared import ParticleGenerator
    from physics2d.physics2d import Physics2D
    from physics2d.shape.base import Shape

_HEALTH_COLOR = RGB(0, 255, 0)


def _particles(color: RGB, size: float) -> "ParticleGenerator":
    def _p(engine: "Physics2D", source: "PhysicsEntity") -> None:
        pieces: list[Shape] = []

        for _ in range(1):
            # little particles doing particle stuff
            challita = CircularParticle(
                origin=(source.center + VectorF.random_offset_vector(source.radius * 2)),
                size=1 + random_offset(),
                initial_color=color,
                ending_color=color.copy(opacity=0.1),
                life_time=round(size),
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
        )

    def _grant_player_something(self) -> None:
        self.engine.player.grant_health(self._amount)


#############################################################
