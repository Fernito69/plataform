from typing import TYPE_CHECKING

from model.base import PointF
from model.theme import RGB, Theme
from physics2d.constants import SHOTGUN_COLOR
from physics2d.entities.equipment.weapons.shotgun import Shotgun
from physics2d.pickable.base import Pickable
from physics2d.shape.particle.circular_particle import CircularParticle
from utils import random_offset

if TYPE_CHECKING:
    from physics2d.entities.base import PhysicsEntity
    from physics2d.entities.model.shared import ParticleGenerator
    from physics2d.physics2d import Physics2D
    from physics2d.shape.base import Shape


class ShotgunPickup(Pickable):
    def __init__(
        self,
        engine: "Physics2D",
        position: PointF,
    ) -> None:
        super().__init__(
            engine,
            theme=Theme(SHOTGUN_COLOR),
            secondary_theme=Theme(0.1 * SHOTGUN_COLOR),
            color_gradient_exponent_end=0,
            color_gradient_exponent=1,
            size=10,
            position=position,
            particle_generator=_weapon_flame(SHOTGUN_COLOR),
        )

    def _grant_player_something(self) -> None:
        self.engine.player.grant_weapon(Shotgun(self.engine))


def _weapon_flame(color: RGB) -> "ParticleGenerator":
    def _w(engine: "Physics2D", source: "PhysicsEntity") -> None:
        pieces: list[Shape] = []

        for _ in range(3):
            # little particles doing particle stuff
            sonic_challa = CircularParticle(
                origin=(source.center),
                size=(0.8 + random_offset()),
                initial_color=color,
                ending_color=0.1 * color,
                life_time=10,
                floating_multi=1,
                engine=engine,
            )
            pieces.append(sonic_challa)

        engine.scenario.bg_shapes[0:0] = pieces

    return _w


#############################################################
