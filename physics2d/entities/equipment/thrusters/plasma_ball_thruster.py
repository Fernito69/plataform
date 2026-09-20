from typing import TYPE_CHECKING

from model.theme import RGB, Theme
from physics2d.entities.equipment.thruster import Thruster
from physics2d.shape.base import Shape
from physics2d.shape.particle.lightning import Lightning
from utils import random_offset_vector

if TYPE_CHECKING:
    from physics2d.entities.base import PhysicsEntity
    from physics2d.physics2d import Physics2D


class PlasmaBallThruster(Thruster):
    """Looks kewwwl"""

    def __init__(self, engine: "Physics2D"):
        super().__init__(
            engine=engine,
            particle_generator=lightning_bolts,
            name="PlasmaBallThruster",
            player_theme=Theme(
                color=RGB(255, 255, 190),
            ),
            max_speed=8,
            accel=3,
            decel=1.5,
        )


#######################


def lightning_bolts(engine: "Physics2D", source: "PhysicsEntity") -> None:
    pieces: list[Shape] = []

    vel_magnitude = abs(source.velocity) * 4

    _initial_color = RGB(255, 220, 200, 1)
    _ending_color = RGB(0, 0, 100, 1)

    _random_magnitude = (vel_magnitude) + source.radius + (40 if vel_magnitude == 0 else 0)
    _end_point = (
        source.center + source.velocity + random_offset_vector(_random_magnitude, _random_magnitude)
        if vel_magnitude > 0
        else source.center
        + source.velocity
        + random_offset_vector(_random_magnitude, _random_magnitude)
    )

    l1 = Lightning(
        source=source,
        end_point=_end_point,
        initial_color=_initial_color,
        ending_color=_ending_color,
        normal_noise=2,
        parallel_noise=3,
        life_time=5,
        num_segments=15,
        thickness=1.5,
        engine=engine,
        final_thickness=0.001,
    )
    pieces.append(l1)

    engine.scenario.bg_shapes[0:0] = pieces
