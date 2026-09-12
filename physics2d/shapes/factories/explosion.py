from random import random
from typing import TYPE_CHECKING

from model.base import PointF, VectorF
from model.theme import RGB
from physics2d.shapes.model.shared import TransitionType
from physics2d.shapes.particle import CircularParticle
from utils import get_vector_angle, random_offset, random_offset_vector

if TYPE_CHECKING:
    from physics2d.entities.base import PhysicsEntity
    from physics2d.scenario.scenario import Scenario


def explosion(scenario: "Scenario", source: "PhysicsEntity", size: float) -> None:
    particles: list[CircularParticle] = []

    eye_x = source.center.x - source.velocity.x
    eye_y = source.center.y - source.velocity.y

    core_explosion_1 = CircularParticle(
        origin=PointF(x=eye_x + random_offset(), y=eye_y + random_offset()),
        initial_velocity=source.velocity,
        size=size * 0.5,
        size_change_type=TransitionType.LINEAR_DECREASE,
        initial_color=RGB(255, 255, 255, 1),
        ending_color=RGB(180, 180, 120, intensity=1),  # smokelike
        life_time=20,
        gravity=-0.08,
    )
    core_explosion_2 = CircularParticle(
        origin=PointF(x=eye_x + random_offset(), y=eye_y + random_offset()),
        initial_velocity=source.velocity,
        size=size * 0.75,
        size_change_type=TransitionType.LINEAR_DECREASE,
        initial_color=RGB(255, 255, 80, 1),
        ending_color=RGB(140, 140, 30, intensity=1),  # smokelike
        life_time=25,
        gravity=-0.075,
    )
    particles.append(core_explosion_1)
    particles.append(core_explosion_2)

    # METEOR KINDA TRAIL
    _main_explosion_color = (
        RGB(
            255,
            160 * random(),
            50 * random(),
        ).with_intensity(1)
        if random_offset() > 0
        else RGB(
            255,
            255 - 30 * random(),
            1 * random(),
        ).with_intensity(1)
    )

    main_explosion = CircularParticle(
        origin=PointF(x=eye_x + random_offset(), y=eye_y + random_offset()),
        initial_velocity=source.velocity,
        size=size,
        size_change_type=TransitionType.LINEAR_DECREASE,
        initial_color=_main_explosion_color,
        ending_color=RGB(30, 30, 30, intensity=1),  # smokelike
        life_time=30,
        gravity=-0.07,
    )
    particles.append(main_explosion)

    secondary_explosions: list[CircularParticle] = []
    _sec_size = size**0.5

    for _ in range(round(size)):
        _sec_explosion_color = (
            RGB(
                255,
                90 * random(),
                50 * random(),
            ).with_intensity(1)
            if random_offset() > 0
            else RGB(
                255,
                255 - 30 * random(),
                1 * random(),
            ).with_intensity(1)
        )

        _factor = size * 1.5
        sec_explosion = CircularParticle(
            origin=PointF(x=eye_x + _factor * random_offset(), y=eye_y + _factor * random_offset()),
            initial_velocity=source.velocity,
            size=_sec_size,
            size_change_type=TransitionType.LINEAR_DECREASE,
            initial_color=_sec_explosion_color,
            ending_color=RGB(30, 30, 30, intensity=1),  # smokelike
            life_time=20,
            gravity=-0.08,
            floating_multi=0.1,
            particle_generator=smoke_generator,
        )
        secondary_explosions.append(sec_explosion)

    scenario.fg_pieces[0:0] = secondary_explosions

    # smoke_trails: list[CircularParticle] = []

    # for i in range(round(size)):
    #     smoke_trail = CircularParticle(
    #         origin=PointF(x=eye_x + (size / 2) * random_offset(), y=eye_y + (size / 2) * random()),
    #         initial_velocity=(source.velocity + random_offset_vector() * size).as_vector(),
    #         size=_sec_size,
    #         size_change_type=TransitionType.LINEAR_DECREASE,
    #         initial_color=RGB(110, 60, 10, 1),
    #         ending_color=RGB(10, 10, 10, 1),  # smokelike
    #         life_time=50,
    #         # floating_multi=0.2,
    #         gravity=0.07,
    #     )

    #     smoke_trails.append(smoke_trail)

    # if i % 3 == 0:
    #     scenario.bg_pieces[0:0] = smoke_trails
    # else:
    #     scenario.fg_pieces[0:0] = smoke_trails

    for _ in range(round(size * 3)):
        # TODO: make these sparks and other useful things into their own class
        sparks = CircularParticle(
            origin=PointF(
                x=eye_x + random_offset() * source.radius * 2,
                y=eye_y + random_offset() * source.radius * 2,
            ),
            initial_velocity=(
                VectorF(x=random_offset() * 5, y=random_offset() * 5) + 1 * -source.velocity
            ).as_vector(),
            size=0.5,
            initial_color=RGB(255, 255, 200, 1),  # almost white hot
            ending_color=RGB(40, 5, 0, 1),  # dark orange
            life_time=70,
            gravity=0.1,
        )
        particles.append(sparks)

    scenario.bg_pieces[0:0] = particles


#################################################################


def smoke_generator(scenario: "Scenario", source: "PhysicsEntity") -> None:
    if random_offset() < 0.25:
        return

    smokes: list[CircularParticle] = []
    main_smoke = CircularParticle(
        origin=source.center,
        initial_velocity=(3 * source.velocity).as_vector(),
        size=source.radius / 2,
        size_change_type=TransitionType.LINEAR_DECREASE,
        initial_color=RGB(110, 90, 90, 1),
        ending_color=RGB(30, 30, 30, 1),  # smokelike
        life_time=30,
        gravity=-0.05,
        # floating_multi=0.1,
    )
    smokes.append(main_smoke)

    if random_offset() > 0:
        scenario.fg_pieces[0:0] = smokes
    else:
        scenario.bg_pieces[0:0] = smokes


#################################################################


def bullet_ricochet(scenario: "Scenario", source: "PhysicsEntity") -> None:
    _main_explosion_color = (
        RGB(
            255,
            150 + 100 * random(),
            150 * random(),
        ).with_intensity(1)
        if random_offset() > 0
        else RGB(
            255,
            255 - 30 * random(),
            100 * random(),
        ).with_intensity(1)
    )

    explosion = CircularParticle(
        origin=source.center + random_offset_vector(),
        initial_velocity=VectorF(0, 0),
        size=2,
        size_change_type=TransitionType.LINEAR_DECREASE,
        initial_color=_main_explosion_color,
        ending_color=RGB(30, 30, 30, intensity=1),  # smokelike
        life_time=15,
        gravity=-0.02,
    )
    scenario.fg_pieces.append(explosion)

    if scenario.now() % 5 < 1:
        return

    ricochet = CircularParticle(
        origin=source.center,
        initial_velocity=(
            (-0.25) * source.velocity
            + VectorF(0, 2 * random_offset()).rotate(
                get_vector_angle((-source.velocity).as_vector())
            )
        ).as_vector(),
        size=0.5,
        initial_color=RGB(255, 255, 240, 1),  # almost white hot
        ending_color=RGB(100, 60, 0, 1),  # dark orange
        life_time=10,
        gravity=0.1,
    )
    scenario.bg_pieces.append(ricochet)


################################################################


def lightning_impact(
    scenario: "Scenario", source: "PhysicsEntity", origin: PointF | None = None
) -> None:
    pieces: list["PhysicsEntity"] = []

    vel_magnitude = 0

    # _initial_color = RGB(
    #     0 + (vel_magnitude * random()) * 80, 255 - (vel_magnitude * random()) * 10, 200, 1
    # )

    _initial_color = RGB(255 - ((8 - vel_magnitude) * random()), 255, 255, 1)
    _origin = origin or source.position

    sonic_boom_2 = CircularParticle(
        origin=_origin + VectorF(x=3 * random_offset(), y=3 * random_offset()),
        initial_velocity=VectorF(0, 0),
        size=2,
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
        origin=_origin + VectorF(x=3 * random_offset(), y=3 * random_offset()),
        initial_velocity=VectorF(0, 0),
        size=3,
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
            origin=_origin + VectorF(x=random_offset(), y=random_offset()),
            initial_velocity=(
                -0.4
                * VectorF(
                    x=source.velocity.x + random_offset(), y=source.velocity.y + random_offset()
                )
            ).as_vector(),
            size=(0.6),
            size_change_type=TransitionType.EXPONENTIAL_DECREASE,
            initial_color=RGB(255, 255, 255, 1),
            ending_color=RGB(127, 0, 255, 1),
            ending_color_fade_type=TransitionType.LINEAR_DECREASE,
            life_time=8,
            floating_multi=6,
        )
        pieces.append(sonic_challa)

    if scenario.now() % 2 == 0:
        # TODO: make Spark factory
        blue_spark = CircularParticle(
            origin=_origin,
            initial_velocity=random_offset_vector(7, 7),
            size=0.5,
            initial_color=RGB(230, 230, 255, 1),
            ending_color=RGB(0, 0, 200, 1),
            life_time=8,
            gravity=0.05,
        )
        scenario.fg_pieces.append(blue_spark)

    scenario.fg_pieces[0:0] = pieces
