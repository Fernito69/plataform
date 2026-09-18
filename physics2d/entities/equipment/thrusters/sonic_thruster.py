from random import random
from typing import TYPE_CHECKING

from model.base import VectorF
from model.theme import RGB, Theme
from physics2d.entities.equipment.thruster import Thruster
from physics2d.shape.base import Shape
from physics2d.shape.model.shared import TransitionType
from physics2d.shape.particle.circular_particle import CircularParticle
from utils import random_offset

if TYPE_CHECKING:
    from physics2d.entities.base import PhysicsEntity
    from physics2d.scenario.scenario import Scenario


class SonicThruster(Thruster):
    """I dunno!"""

    def __init__(self, scenario: "Scenario"):
        super().__init__(
            scenario=scenario,
            particle_generator=sonic_wave,
            name="SonicThruster",
            player_theme=Theme(
                color=RGB(122, 23, 255),
            ),
            max_speed=7,
            accel=2,
            decel=1.5,
        )


def sonic_wave(scenario: "Scenario", source: "PhysicsEntity") -> None:
    pieces: list[Shape] = []

    vel_magnitude = abs(source.velocity)

    # _initial_color = RGB(
    #     0 + (vel_magnitude * random()) * 80, 255 - (vel_magnitude * random()) * 10, 200, 1
    # )

    _initial_color = RGB(255 - ((8 - vel_magnitude) * random()), 255, 255, 1)

    sonic_boom_vacuum = CircularParticle(
        origin=(source.center + 0.8 * source.velocity)
        - VectorF(x=random_offset(), y=random_offset()),
        initial_velocity=(
            -0.5
            * VectorF(x=source.velocity.x + random_offset(), y=source.velocity.y + random_offset())
        ).as_vector(),
        size=source.radius * (1 + vel_magnitude / 13),
        size_change_type=TransitionType.EXPONENTIAL_DECREASE,
        initial_color=RGB(0, 0, 0, 0),
        ending_color=RGB(0, 0, 0, 0),
        ending_color_fade_type=TransitionType.LINEAR_DECREASE,
        life_time=2,
        floating_multi=1,
    )
    pieces.append(sonic_boom_vacuum)

    sonic_boom_2 = CircularParticle(
        origin=(source.center - 0.2 * source.velocity)
        - VectorF(x=random_offset(), y=random_offset()),
        initial_velocity=(
            -0.4
            * VectorF(x=source.velocity.x + random_offset(), y=source.velocity.y + random_offset())
        ).as_vector(),
        size=source.radius * (1 + vel_magnitude / 10),
        size_change_type=TransitionType.EXPONENTIAL_DECREASE,
        initial_color=_initial_color,
        ending_color=RGB(200, 200, 255, 1),
        ending_color_fade_type=TransitionType.LINEAR_DECREASE,
        life_time=5,
        floating_multi=1,
    )
    pieces.append(sonic_boom_2)

    # MAIN BOOM
    sonic_boom = CircularParticle(
        origin=(source.center - source.velocity) - VectorF(x=random_offset(), y=random_offset()),
        initial_velocity=(
            -0.4
            * VectorF(x=source.velocity.x + random_offset(), y=source.velocity.y + random_offset())
        ).as_vector(),
        size=source.radius * (1 + (vel_magnitude + random()) / 7),
        size_change_type=TransitionType.EXPONENTIAL_DECREASE,
        initial_color=_initial_color,
        ending_color=RGB(127, 0, 255, 1),
        ending_color_fade_type=TransitionType.LINEAR_DECREASE,
        life_time=25,
        floating_multi=1,
    )
    pieces.append(sonic_boom)

    for _ in range(3):
        # little particles doing particle stuff
        sonic_challa = CircularParticle(
            origin=(source.center - source.velocity)
            - VectorF(x=random_offset(), y=random_offset()),
            initial_velocity=(
                -0.4
                * VectorF(
                    x=source.velocity.x + random_offset(), y=source.velocity.y + random_offset()
                )
            ).as_vector(),
            size=(0.8 + random_offset()) * vel_magnitude / 3,
            size_change_type=TransitionType.EXPONENTIAL_DECREASE,
            initial_color=_initial_color,
            ending_color=RGB(127, 0, 255, 1),
            ending_color_fade_type=TransitionType.LINEAR_DECREASE,
            life_time=15,
            floating_multi=6,
        )
        pieces.append(sonic_challa)

    # if scenario.now() % 4 == 0:
    #     normal_1, normal_2 = get_normal_vectors(source.velocity)

    #     def _get_parallel_boom(normal: VectorF) -> Particle:
    #         return Particle(
    #             origin=(source.center - source.velocity),
    #             initial_velocity=(normal + source.velocity).as_vector(),
    #             size=vel_magnitude / 1.5,
    #             size_change_type=TransitionType.EXPONENTIAL_DECREASE,
    #             initial_color=RGB(255, 255, 255, 1),
    #             ending_color=RGB(255, 255, 255),
    #             ending_color_fade_type=TransitionType.NONE,
    #             life_time=15,
    #             floating_multi=0,
    #         )

    #     paralel_boom_1 = _get_parallel_boom(normal_1)
    #     paralel_boom_2 = _get_parallel_boom(normal_2)
    #     pieces.extend([paralel_boom_1, paralel_boom_2])

    # TOOD: y esto?
    _initial_color = RGB(255 - ((8 - vel_magnitude) * random()), 255, 255, 1)

    scenario.bg_shapes[0:0] = pieces
