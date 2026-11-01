from typing import TYPE_CHECKING

from model.base import PointF
from model.theme import RGB, Theme
from physics2d.constants import SHOTGUN_COLOR
from physics2d.entities.equipment.weapons.shotgun import Shotgun
from physics2d.pickable.base import Pickable
from physics2d.shape.line import Line
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
            extra_shapes=_letter_s(engine, position),
        )

    def _grant_player_something(self) -> None:
        self.engine.player.grant_weapon(Shotgun(self.engine))


def _letter_s(engine: "Physics2D", position: PointF, factor: float = 1.7) -> list["Shape"]:
    _letter_color = Theme(SHOTGUN_COLOR.get_gradient(RGB(255, 255, 255)))

    def _l(points: tuple[PointF, PointF]) -> Line:
        return Line(
            points=(
                position + points[0],
                position + points[1],
            ),
            engine=engine,
            theme=_letter_color,
            thickness=factor / 2,
            thickness_gradient_threshold=0.5,
        )

    letter_shapes: list["Shape"] = [
        _l((factor * PointF(-1, 0), factor * PointF(1, 0))),
        _l((factor * PointF(-1, 0), factor * PointF(-1.5, 0.5))),
        _l((factor * PointF(-1.5, 0.5), factor * PointF(-1.5, 1))),
        _l((factor * PointF(-1.5, 1), factor * PointF(-1, 1.5))),
        _l((factor * PointF(-1, 1.5), factor * PointF(1.5, 1.5))),
        _l((factor * PointF(1, 0), factor * PointF(1.5, -0.5))),
        _l((factor * PointF(1.5, -0.5), factor * PointF(1.5, -1))),
        _l((factor * PointF(1.5, -1), factor * PointF(1, -1.5))),
        _l((factor * PointF(1, -1.5), factor * PointF(-1.5, -1.5))),
    ]
    return letter_shapes


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
