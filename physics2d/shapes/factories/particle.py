from random import random
from typing import TYPE_CHECKING

from model.base import PointF, VectorF
from model.theme import RGB
from physics2d.shapes.model.shared import TransitionType
from physics2d.shapes.particle import Particle
from utils import random_offset

if TYPE_CHECKING:
    from physics2d.scenario.scenario import Scenario
    from physics2d.shapes.circunference import Circunference

_THRUST_FIRE_SPAWN_RANDOMNESS_FACTOR = 2
_THRUST_FIRE_DISTANCE_FACTOR = 1


def meteor_trail(scenario: "Scenario", source: "Circunference") -> None:
    pieces: list[Particle] = []

    for _i in range(1, int(source.radius * 2)):
        i = _i / 2
        distance_factor = (source.radius - i) * _THRUST_FIRE_DISTANCE_FACTOR
        eye_x = source.center.x - source.velocity.x * distance_factor
        eye_y = source.center.y - source.velocity.y * distance_factor

        is_odd = _i % 2 == 1
        _randomness_multi = random() * 2
        _radius_factor = random() * 1.2

        # METEOR KINDA TRAIL
        _meteor_color = (
            RGB(
                255,
                (i - 1) * 90,
                (i - 1) * 50,
            ).with_intensity(1)
            if is_odd
            else RGB(
                255,
                255 - (i - 1) * 30,
                (i - 1) * 1,
            ).with_intensity(1)
        )

        thrust_fire = Particle(
            origin=PointF(
                x=eye_x
                + random_offset() * _THRUST_FIRE_SPAWN_RANDOMNESS_FACTOR * _randomness_multi
                + random_offset() * 0.5,
                y=eye_y
                + random_offset() * _THRUST_FIRE_SPAWN_RANDOMNESS_FACTOR * _randomness_multi
                + random_offset() * 0.5,
            ),
            initial_velocity=VectorF(
                x=source.velocity.x * _THRUST_FIRE_SPAWN_RANDOMNESS_FACTOR * _randomness_multi * 0.1
                + random_offset() * 0.5,
                y=source.velocity.y * _THRUST_FIRE_SPAWN_RANDOMNESS_FACTOR * _randomness_multi * 0.1
                + random_offset() * 0.5,
            ),
            size=i * _radius_factor,
            size_change_type=TransitionType.LINEAR_DECREASE,
            initial_color=_meteor_color,
            ending_color=RGB(100, 100, 100, intensity=0.1),  # smokelike
            life_time=50,
            gravity=-0.02,
        )
        pieces.append(thrust_fire)

    vel_magnitude = abs(source.velocity)
    for _ in range(round(vel_magnitude)):
        sparks = Particle(
            origin=PointF(
                x=eye_x + random_offset() * 0.2,
                y=eye_y + random_offset() * 0.2,
            ),
            initial_velocity=(
                VectorF(x=random_offset() * 5, y=random_offset() * 5) + 1 * -source.velocity
            ).as_vector(),
            size=0.8,
            initial_color=RGB(255, 255, 255, 1),  # white hot
            ending_color=RGB(200, 127, 0, 1),  # Yellow
            life_time=50,
            gravity=0.1,
        )
        pieces.append(sparks)

    pieces = sorted(pieces, key=random_offset)

    scenario.bg_pieces[0:0] = pieces
    # for index in range(len(pieces)):
    #     if index % 3 == 0:
    #         scenario.fg_pieces.append(pieces[index])
    #     else:
    #         scenario.bg_pieces.append(pieces[index])


def ln2_vapor(scenario: "Scenario", source: "Circunference") -> None:
    pieces: list[Particle] = []
    velocity_magnitude = abs(source.velocity)

    for _i in range(1, int(source.radius * 2)):
        i = _i / 2
        distance_factor = (source.radius - i) * _THRUST_FIRE_DISTANCE_FACTOR
        eye_x = source.center.x - source.velocity.x * distance_factor
        eye_y = source.center.y - source.velocity.y * distance_factor

        is_odd = _i % 2 == 1
        _randomness_multi = random() * 3
        _radius_factor = random() * 1

        # Liquid N2 trail
        _ln2_color = (
            RGB(
                127,
                223 - (i - 1) * 14,
                255 - (i - 1) * 5,
            ).with_intensity(1)
            if is_odd
            else RGB(
                127,
                220 - (i - 1) * 10,
                255 - (i - 1) * 14,
            ).with_intensity(1)
        )

        vapor = Particle(
            origin=PointF(
                x=eye_x
                + random_offset() * _THRUST_FIRE_SPAWN_RANDOMNESS_FACTOR * _randomness_multi
                + random_offset() * 0.5,
                y=eye_y
                + random_offset() * _THRUST_FIRE_SPAWN_RANDOMNESS_FACTOR * _randomness_multi
                + random_offset() * 0.5,
            ),
            initial_velocity=VectorF(
                x=source.velocity.x * _THRUST_FIRE_SPAWN_RANDOMNESS_FACTOR * _randomness_multi * 0.1
                + random_offset() * 0.5,
                y=source.velocity.y * _THRUST_FIRE_SPAWN_RANDOMNESS_FACTOR * _randomness_multi * 0.1
                + random_offset() * 0.5,
            ),
            # radius=i * math.cos((size - i) / size),
            size=i * _radius_factor,
            size_change_type=TransitionType.LINEAR_DECREASE,
            initial_color=_ln2_color,
            ending_color=RGB(177, 255, 255),  # N2 like
            ending_color_fade_type=TransitionType.LINEAR_DECREASE,
            life_time=50,
            gravity=0.02,
            floating_multi=0.1 * velocity_magnitude,
        )
        pieces.append(vapor)

        if i % 10 == 0:
            icy_sparks = Particle(
                origin=PointF(
                    x=eye_x + random_offset() * 0.1 + source.velocity.x * 3,
                    y=eye_y + source.velocity.y * 3,
                ),
                initial_velocity=(
                    -VectorF(x=random_offset() * 1, y=random_offset() * velocity_magnitude)
                    + 0.5 * source.velocity
                ).as_vector(),
                size=0.8,
                initial_color=RGB(255, 255, 255, 1),
                life_time=50,
                gravity=0.1,
            )
            # pieces.append(icy_sparks)
            scenario.bg_pieces.append(icy_sparks)

    pieces = sorted(pieces, key=random_offset)

    for index in range(len(pieces)):
        if index % 8 == 0:
            scenario.fg_pieces.append(pieces[index])
        else:
            scenario.bg_pieces.append(pieces[index])


def sonic_wave(scenario: "Scenario", source: "Circunference") -> None:
    pieces: list[Particle] = []

    vel_magnitude = abs(source.velocity)

    _initial_color = RGB(
        0 + (vel_magnitude * random()) * 80, 255 - (vel_magnitude * random()) * 10, 200, 1
    )
    sonic_boom = Particle(
        origin=(source.center - source.velocity) - VectorF(x=random_offset(), y=random_offset()),
        initial_velocity=(
            -0.4
            * VectorF(x=source.velocity.x + random_offset(), y=source.velocity.y + random_offset())
        ).as_vector(),
        size=source.radius * (1 + vel_magnitude / 7),
        size_change_type=TransitionType.EXPONENTIAL_DECREASE,
        initial_color=_initial_color,
        ending_color=RGB(0, 0, 0, 0),
        ending_color_fade_type=TransitionType.LINEAR_DECREASE,
        life_time=15,
        floating_multi=1,
    )
    pieces.append(sonic_boom)

    scenario.bg_pieces[0:0] = pieces
