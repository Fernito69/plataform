from typing import TYPE_CHECKING

from model.base import PointF, VectorF
from model.theme import RGB
from physics2d.entities.base import PhysicsEntity
from physics2d.entities.spawners.utils import get_position
from physics2d.shape.model.shared import TransitionType
from physics2d.shape.particle.circular_particle import CircularParticle
from utils import random_offset

if TYPE_CHECKING:
    from physics2d.physics2d import Physics2D
    from physics2d.shape.base import Shape


def teleport_in_particles(
    engine: "Physics2D",
    source: "PhysicsEntity | PointF",
    size: float = 10,
) -> None:
    pieces: list[Shape] = []

    _initial_color = RGB(80, 255, 80)

    shockwave = CircularParticle(
        engine=engine,
        origin=get_position(source),
        size=size,
        size_change_type=TransitionType.EXPONENTIAL_DECREASE,
        initial_color=_initial_color,
        ending_color=_initial_color.copy(opacity=0),
        ending_color_fade_type=TransitionType.LINEAR_DECREASE,
        life_time=15,
    )
    pieces.append(shockwave)

    shockwave = CircularParticle(
        engine=engine,
        origin=get_position(source),
        size=0,
        final_radius=size,
        size_change_type=TransitionType.LINEAR_INCREASE,
        initial_color=RGB(255, 255, 255),
        ending_color=RGB(255, 255, 255, opacity=0),
        ending_color_fade_type=TransitionType.LINEAR_DECREASE,
        life_time=15,
    )
    pieces.append(shockwave)

    for _ in range(15):
        # little particles doing particle stuff
        velocity: VectorF = source.velocity if isinstance(source, PhysicsEntity) else VectorF(0, 0)

        sonic_challa = CircularParticle(
            origin=(get_position(source) - velocity)
            - VectorF(x=random_offset(), y=random_offset()),
            initial_velocity=(
                -0.4 * VectorF(x=velocity.x + random_offset(), y=velocity.y + random_offset())
            ),
            size=4,
            size_change_type=TransitionType.EXPONENTIAL_DECREASE,
            initial_color=_initial_color,
            ending_color=_initial_color.copy(opacity=0),
            ending_color_fade_type=TransitionType.LINEAR_DECREASE,
            life_time=25,
            floating_multi=5,
            engine=engine,
        )
        pieces.append(sonic_challa)

    engine.scenario.bg_shapes[0:0] = pieces
