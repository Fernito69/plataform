from typing import TYPE_CHECKING

from model.base import VectorF
from model.theme import RGB, Theme
from physics2d.entities.equipment.thruster import Thruster
from physics2d.shape.model.shared import TransitionType
from physics2d.shape.particle.circular_particle import CircularParticle
from physics2d.shape.shape import Shape
from utils import random_offset

if TYPE_CHECKING:
    from physics2d.entities.base import PhysicsEntity
    from physics2d.scenario.scenario import Scenario


class BasicThruster(Thruster):
    """Standard issue"""

    def __init__(self, scenario: "Scenario"):
        super().__init__(
            scenario=scenario,
            particle_generator=standard_thruster,
            name="BasicThruster",
            player_theme=Theme(
                color=RGB(150, 220, 150),
            ),
            max_speed=3.5,
            accel=0.8,
            decel=0.3,
        )


######################################


def standard_thruster(scenario: "Scenario", source: "PhysicsEntity") -> None:
    pieces: list[Shape] = []

    _smoke_density = 3
    for i in range(_smoke_density):
        # little particles doing particle stuff
        smoke = CircularParticle(
            origin=(
                source.center
                - (i + 1 / _smoke_density) * source.velocity
                - source.get_last_known_direction() * 1
            )
            + source.size * VectorF.random_offset_vector(),
            initial_velocity=(
                +0.2 * VectorF.random_offset_vector() - source.get_last_known_direction()
            ).as_vector(),
            size=0.7 + random_offset(),
            size_change_type=TransitionType.LINEAR_DECREASE,
            initial_color=RGB(255, 255, 120),
            ending_color=RGB(0, 60, 0, 1),
            ending_color_fade_type=TransitionType.LINEAR_DECREASE,
            life_time=10,
            gravity=-0.07,
        )
        pieces.append(smoke)

    scenario.bg_pieces[0:0] = pieces
