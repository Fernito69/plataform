from typing import TYPE_CHECKING

from model.base import VectorF
from model.theme import RGB
from physics2d.shapes.model.shared import TransitionType
from physics2d.shapes.particle import CircularParticle
from utils import (
    get_vector_angle,
    random_offset,
    random_offset_vector,
)

if TYPE_CHECKING:
    from physics2d.scenario.scenario import Scenario
    from physics2d.shapes.circunference import Circunference


def machine_gun(scenario: "Scenario", source: "Circunference") -> None:
    _fire_1_color = (
        RGB(
            255,
            200,
            50,
        ).with_intensity(1)
        if random_offset() > 0
        else RGB(
            255,
            150,
            0,
        ).with_intensity(1)
    )
    fire_1 = CircularParticle(
        origin=source.center + 5 * (source.get_last_known_direction()) + random_offset_vector(),
        initial_velocity=source.velocity,
        size=4,
        size_change_type=TransitionType.EXPONENTIAL_DECREASE,
        initial_color=_fire_1_color,
        ending_color=RGB(150, 120, 30, intensity=1),
        life_time=5,
    )
    fire_2 = CircularParticle(
        origin=source.center + 7.5 * (source.get_last_known_direction()) + random_offset_vector(),
        initial_velocity=source.velocity,
        size=3.5,
        size_change_type=TransitionType.EXPONENTIAL_DECREASE,
        initial_color=RGB(
            255,
            120,
            20,
        ).with_intensity(1),
        ending_color=RGB(150, 90, 30, intensity=1),
        life_time=5,
    )
    fire_3 = CircularParticle(
        origin=source.center
        + 10 * (source.get_last_known_direction())
        + 2 * random_offset_vector(),
        initial_velocity=source.velocity,
        size=2,
        size_change_type=TransitionType.EXPONENTIAL_DECREASE,
        initial_color=RGB(
            255,
            80,
            20,
        ).with_intensity(1),
        ending_color=RGB(120, 60, 20, intensity=1),
        life_time=5,
    )
    fire_white = CircularParticle(
        origin=source.center + 4.5 * (source.get_last_known_direction()) + random_offset_vector(),
        initial_velocity=source.velocity,
        size=3,
        size_change_type=TransitionType.EXPONENTIAL_DECREASE,
        initial_color=RGB(255, 200, 255, 1),
        ending_color=RGB(200, 150, 200, 1),
        life_time=4,
    )
    sparks: list[CircularParticle] = []
    if scenario.now() % 3 == 0:
        spark = CircularParticle(
            origin=source.center
            + 4.5 * (source.get_last_known_direction() + random_offset_vector()),
            initial_velocity=(
                source.velocity
                + 5
                * (
                    source.get_last_known_direction()
                    + VectorF(0, random_offset() * 2).rotate(
                        get_vector_angle(source.get_last_known_direction())
                    )
                )
            ).as_vector(),
            size=0.5,
            size_change_type=TransitionType.NONE,
            initial_color=RGB(255, 255, 200, 1),  # almost white hot
            ending_color=RGB(80, 10, 0, 1),  # dark orange
            life_time=5,
            gravity=0.1,
        )
        sparks.append(spark)

    scenario.fg_pieces.extend(sparks + [fire_white, fire_1, fire_2, fire_3])


################


def shotgun(scenario: "Scenario", source: "Circunference") -> None:
    # TODO: this is copy/paste, generalize
    _fire_1_color = (
        RGB(
            255,
            200,
            50,
        ).with_intensity(1)
        if random_offset() > 0
        else RGB(
            255,
            150,
            0,
        ).with_intensity(1)
    )
    fire_1 = CircularParticle(
        origin=source.center + 7 * (source.get_last_known_direction()) + random_offset_vector(),
        initial_velocity=source.velocity,
        size=6,
        size_change_type=TransitionType.EXPONENTIAL_DECREASE,
        initial_color=_fire_1_color,
        ending_color=RGB(150, 120, 30, intensity=1),
        life_time=7,
    )
    fire_2 = CircularParticle(
        origin=source.center + 9 * (source.get_last_known_direction()) + random_offset_vector(),
        initial_velocity=source.velocity,
        size=5,
        size_change_type=TransitionType.EXPONENTIAL_DECREASE,
        initial_color=RGB(
            255,
            120,
            20,
        ).with_intensity(1),
        ending_color=RGB(150, 90, 30, intensity=1),
        life_time=6,
    )
    fire_3 = CircularParticle(
        origin=source.center
        + 13 * (source.get_last_known_direction())
        + 2 * random_offset_vector(),
        initial_velocity=source.velocity,
        size=4,
        size_change_type=TransitionType.EXPONENTIAL_DECREASE,
        initial_color=RGB(
            255,
            80,
            20,
        ).with_intensity(1),
        ending_color=RGB(120, 60, 20, intensity=1),
        life_time=5,
    )
    fire_white = CircularParticle(
        origin=source.center + 6 * (source.get_last_known_direction()) + random_offset_vector(),
        initial_velocity=source.velocity,
        size=6,
        size_change_type=TransitionType.EXPONENTIAL_DECREASE,
        initial_color=RGB(255, 200, 255, 1),
        ending_color=RGB(200, 150, 200, 1),
        life_time=5,
    )
    sparks: list[CircularParticle] = []

    spark = CircularParticle(
        origin=source.center + 6 * (source.get_last_known_direction() + random_offset_vector()),
        initial_velocity=(
            source.velocity
            + 5
            * (
                source.get_last_known_direction()
                + VectorF(0, random_offset() * 2).rotate(
                    get_vector_angle(source.get_last_known_direction())
                )
            )
        ).as_vector(),
        size=0.5,
        size_change_type=TransitionType.NONE,
        initial_color=RGB(255, 255, 200, 1),  # almost white hot
        ending_color=RGB(80, 10, 0, 1),  # dark orange
        life_time=5,
        gravity=0.1,
    )
    sparks.append(spark)

    scenario.fg_pieces.extend(sparks + [fire_white, fire_1, fire_2, fire_3])
