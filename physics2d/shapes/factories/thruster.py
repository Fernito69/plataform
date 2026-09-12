from random import random
from typing import TYPE_CHECKING

from model.base import PointF, VectorF
from model.theme import RGB
from physics2d.shapes.model.shared import TransitionType
from physics2d.shapes.particle import CircularParticle, Lightning
from physics2d.shapes.shape import Shape
from utils import random_offset, random_offset_vector

if TYPE_CHECKING:
    from physics2d.entities.base import PhysicsEntity
    from physics2d.scenario.scenario import Scenario

_THRUST_FIRE_SPAWN_RANDOMNESS_FACTOR = 2
_THRUST_FIRE_DISTANCE_FACTOR = 1


def meteor_trail(scenario: "Scenario", source: "PhysicsEntity") -> None:
    pieces: list[CircularParticle] = []

    vel_magnitude = abs(source.velocity)

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

        thrust_fire = CircularParticle(
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
            size=i * _radius_factor * (1 + vel_magnitude / 5),
            size_change_type=TransitionType.LINEAR_DECREASE,
            initial_color=_meteor_color,
            ending_color=RGB(30, 30, 30, intensity=1),  # smokelike
            life_time=15,
            gravity=-0.07,
        )
        pieces.append(thrust_fire)

    for _ in range(round((vel_magnitude / 3) + 1)):
        if vel_magnitude == 0 and scenario.now() % 8 != 0:
            continue

        sparks = CircularParticle(
            origin=PointF(
                x=eye_x + random_offset() * source.radius * 2,
                y=eye_y + random_offset() * source.radius * 2,
            ),
            initial_velocity=VectorF(0, 0)
            if vel_magnitude == 0
            else (
                VectorF(x=random_offset() * 5, y=random_offset() * 5) + 1 * -source.velocity
            ).as_vector(),
            size=0.5,
            initial_color=RGB(255, 255, 200, 1),  # almost white hot
            ending_color=RGB(40, 5, 0, 1),  # dark orange
            life_time=70,
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


def ln2_vapor(scenario: "Scenario", source: "PhysicsEntity") -> None:
    pieces: list[CircularParticle] = []
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

        vapor = CircularParticle(
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
            icy_sparks = CircularParticle(
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

    scenario.bg_pieces[0:0] = pieces


def lightning_bolts(scenario: "Scenario", source: "PhysicsEntity") -> None:
    pieces: list[Shape] = []

    vel_magnitude = abs(source.velocity)

    _initial_color = RGB(255, 220, 200, 1)
    _ending_color = RGB(0, 0, 100, 1)

    _random_magnitude = (vel_magnitude) + source.radius + (20 if vel_magnitude == 0 else 0)
    _end_point = (
        random_offset_vector(_random_magnitude, _random_magnitude) + source.center + source.velocity
        if vel_magnitude > 0
        else random_offset_vector(_random_magnitude, _random_magnitude) + source.center
    )

    l1 = Lightning(
        source=source,
        end_point=_end_point,
        initial_color=_initial_color,
        ending_color=_ending_color,
        normal_noise=2,
        parallel_noise=3,
        life_time=6,
        num_segments=15,
        thickness=1.5,
        final_thickness=0.001,
    )
    pieces.append(l1)

    # TODO: why eye doesn't look well??
    # eye = CircularParticle(
    #     size=0.75,
    #     initial_velocity=source.velocity,
    #     origin=source.center + 0.15 * source.velocity,
    #     initial_color=RGB(255, 0, 0, 1),
    #     life_time=2,
    # )
    # scenario.fg_pieces.append(eye)

    # for _ in range(3):
    #     # little particles doing particle stuff
    #     sonic_challa = CircularParticle(
    #         origin=(source.center - source.velocity)
    #         - random_offset_vector(source.radius, source.radius),
    #         initial_velocity=(source.velocity * 0.1).as_vector(),
    #         size=(0.2 * vel_magnitude),
    #         size_change_type=TransitionType.EXPONENTIAL_DECREASE,
    #         initial_color=_initial_color,
    #         ending_color=_ending_color,
    #         ending_color_fade_type=TransitionType.LINEAR_DECREASE,
    #         life_time=15,
    #         floating_multi=5,
    #     )
    #     pieces.append(sonic_challa)

    # if vel_magnitude > 0:
    #     l2 = Lightning(
    #         source=source,
    #         start_point=source.center + random_offset_vector(),
    #         end_point=source.center + 2 * source.velocity,
    #         initial_color=RGB(255, 30, 60),
    #         ending_color=RGB(50, 0, 20, 1),
    #         normal_noise=3,
    #         parallel_noise=3,
    #         life_time=5,
    #         num_segments=6,
    #         thickness=1,
    #         final_thickness=0.1,
    #     )
    #     pieces.append(l2)
    # if vel_magnitude > 7:
    #     raise NotImplementedError([f"{a.points[0]} - {a.points[1]}" for a in l1.segments])

    scenario.bg_pieces[0:0] = pieces
