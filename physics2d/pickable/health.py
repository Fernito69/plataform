from typing import TYPE_CHECKING

from model.base import PointF, VectorF
from model.theme import RGB, Theme
from physics2d.pickable.base import Pickable
from physics2d.shape.particle.circular_particle import CircularParticle
from utils import random_offset

if TYPE_CHECKING:
    from physics2d.entities.base import PhysicsEntity
    from physics2d.entities.model.shared import ParticleGenerator
    from physics2d.physics2d import Physics2D
    from physics2d.shape.base import Shape

_HEALTH_COLOR = RGB(0, 255, 0)


def _particles(color: RGB) -> "ParticleGenerator":
    def _p(engine: "Physics2D", source: "PhysicsEntity") -> None:
        pieces: list[Shape] = []

        for _ in range(1):
            # little particles doing particle stuff
            challita = CircularParticle(
                origin=(source.center + VectorF.random_offset_vector(source.radius * 2)),
                size=1 + random_offset(),
                initial_color=color,
                ending_color=color.copy(opacity=0.1),
                life_time=5,
                floating_multi=0.2,
                engine=engine,
                gravity=-0.05,
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

        super().__init__(
            engine,
            theme=Theme(_HEALTH_COLOR.copy(opacity=0.5)),
            secondary_theme=Theme(0.1 * _HEALTH_COLOR.copy(opacity=0.5)),
            color_gradient_exponent_end=0,
            color_gradient_exponent=1,
            size=amount**0.333,
            position=position,
            particle_generator=_particles(_HEALTH_COLOR),
        )

    def _grant_player_something(self) -> None:
        self.engine.player.grant_health(self._amount)


#############################################################
