from typing import TYPE_CHECKING

from model.base import VectorF, PointF
from model.theme import RGB, Theme
from physics2d.entities.equipment.thruster import Thruster
from physics2d.shape.base import Shape
from physics2d.shape.model.shared import TransitionType
from physics2d.shape.particle.circular_particle import CircularParticle
from utils import random_offset

if TYPE_CHECKING:
    from physics2d.entities.base import PhysicsEntity
    from physics2d.physics2d import Physics2D


class ChamorroThruster(Thruster):
    """Standard issue"""

    def __init__(self, engine: "Physics2D"):
        super().__init__(
            engine=engine,
            particle_generator=chamorro_thruster,
            name="ChamorroThruster",
            player_theme=Theme(
                color=RGB(0, 0, 230),
            ),
            max_speed=4,
            accel=2.2,
            decel=2.2,
        )


######################################


def chamorro_thruster(engine: "Physics2D", source: "PhysicsEntity") -> None:
    pieces: list[Shape] = []

    _smoke_density = 3
    _cheese_color = RGB(255, 255, 0)

    main_cheese = CircularParticle(
        origin=source.center - 3 * source.velocity,
        initial_velocity=(-source.velocity).as_vector(),
        size=7,
        size_change_type=TransitionType.LINEAR_DECREASE,
        initial_color=_cheese_color,
        ending_color=_cheese_color.copy(opacity=0.1),
        ending_color_fade_type=TransitionType.LINEAR_DECREASE,
        life_time=10,
        engine=engine,
    )
    pieces.append(main_cheese)
    engine.scenario.bg_shapes.extend(pieces)

    holes = []
    cheese_positions = (
        [PointF(-2.3, 2.3), PointF(2.3, -2.3)]
        if engine.scenario.now() % 2 == 0
        else [PointF(-2.3, 2.3), PointF(2.3, -2.3), PointF(0, 0)]
    )

    for pos in cheese_positions:
        hole = CircularParticle(
            origin=source.position - 3 * pos - source.velocity,
            initial_velocity=(-source.velocity * 2).as_vector(),
            size=0.8,
            size_change_type=TransitionType.LINEAR_DECREASE,
            initial_color=RGB(0, 0, 0),
            ending_color=RGB(0, 0, 0).copy(opacity=0.1),
            ending_color_fade_type=TransitionType.LINEAR_DECREASE,
            life_time=10,
            engine=engine,
        )
        holes.append(hole)

    engine.scenario.bg_shapes[0:0] = holes
