from random import random
from typing import TYPE_CHECKING

from model.base import PointF, VectorF
from model.theme import RGB
from physics2d.shape.factories.utils import is_out_of_sight
from physics2d.shape.model.shared import TransitionType
from physics2d.shape.particle.circular_particle import CircularParticle
from utils import get_vector_angle, random_offset, random_offset_vector

if TYPE_CHECKING:
    from physics2d.entities.base import PhysicsEntity
    from physics2d.entities.model.shared import ParticleGenerator
    from physics2d.physics2d import Physics2D


def enemy_explosion(engine: "Physics2D", source: "PhysicsEntity", size: float) -> None:
    if is_out_of_sight(engine, source):
        return

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
        engine=engine,
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
        engine=engine,
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
        engine=engine,
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
            engine=engine,
            particle_generator=_smoke_generator,
        )
        secondary_explosions.append(sec_explosion)

    engine.scenario.fg_shapes[0:0] = secondary_explosions

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
    #     engine.scenario.bg_pieces[0:0] = smoke_trails
    # else:
    #     engine.scenario.fg_pieces[0:0] = smoke_trails

    for _ in range(round(size * 3)):
        # TODO: make these sparks and other useful things into their own class
        sparks = CircularParticle(
            origin=PointF(
                x=eye_x + random_offset() * source.radius * 2,
                y=eye_y + random_offset() * source.radius * 2,
            ),
            engine=engine,
            initial_velocity=(
                VectorF(x=random_offset() * 5, y=random_offset() * 5) + 1 * -source.velocity
            ).as_vector(),
            size=0.3,
            initial_color=RGB(255, 255, 200, 1),  # almost white hot
            ending_color=RGB(40, 5, 0, 1),  # dark orange
            life_time=70,
            gravity=0.1,
        )
        particles.append(sparks)

    engine.scenario.bg_shapes[0:0] = particles


#################################################################


def get_smoke_generator(
    life_time: int = 30,
    random_offset_threshold: float = 0.25,
    initial_velocity: VectorF | None = None,
    floating_multi: float = 0,
    only_fg: bool = False,
    gravity: float = 0.05,
    size_factor: float = 0.5,
) -> "ParticleGenerator":
    def _gen(engine: "Physics2D", source: "PhysicsEntity") -> None:
        if is_out_of_sight(engine, source):
            return

        _smoke_generator(
            engine=engine,
            source=source,
            life_time=life_time,
            random_offset_threshold=random_offset_threshold,
            initial_velocity=initial_velocity,
            floating_multi=floating_multi,
            only_fg=only_fg,
            gravity=gravity,
            size_factor=size_factor,
        )

    return _gen


def _smoke_generator(
    engine: "Physics2D",
    source: "PhysicsEntity",
    life_time: int = 30,
    random_offset_threshold: float = 0.25,
    initial_velocity: VectorF | None = None,
    floating_multi: float = 0,
    only_fg: bool = False,
    gravity: float = 0.05,
    size_factor: float = 0.5,
) -> None:
    if random_offset() < random_offset_threshold:
        return

    smokes: list[CircularParticle] = []
    main_smoke = CircularParticle(
        origin=source.center,
        engine=engine,
        initial_velocity=(3 * (initial_velocity or source.velocity)).as_vector(),
        size=source.radius * size_factor,
        size_change_type=TransitionType.LINEAR_DECREASE,
        initial_color=RGB(110, 90, 90, 1),
        ending_color=RGB(30, 30, 30, 1),  # smokelike
        life_time=life_time,
        gravity=gravity,
        floating_multi=floating_multi,
    )
    smokes.append(main_smoke)

    if random_offset() > 0 or only_fg:
        engine.scenario.fg_shapes[0:0] = smokes
    else:
        engine.scenario.bg_shapes[0:0] = smokes


#################################################################


def bullet_ricochet(engine: "Physics2D", source: "PhysicsEntity") -> None:
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
        origin=source.center + VectorF.random_offset_vector(),
        initial_velocity=VectorF(0, 0),
        engine=engine,
        size=2,
        size_change_type=TransitionType.LINEAR_DECREASE,
        initial_color=_main_explosion_color,
        ending_color=RGB(30, 30, 30, intensity=1),  # smokelike
        life_time=15,
        gravity=-0.02,
    )
    engine.scenario.fg_shapes.append(explosion)

    if engine.scenario.now() % 5 < 1:
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
        engine=engine,
        gravity=0.1,
    )
    engine.scenario.bg_shapes.append(ricochet)


################################################################


def lightning_impact(
    engine: "Physics2D", source: "PhysicsEntity", origin: PointF | None = None
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
        engine=engine,
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
        engine=engine,
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
            engine=engine,
            life_time=8,
            floating_multi=6,
        )
        pieces.append(sonic_challa)

    if engine.scenario.now() % 2 == 0:
        # TODO: make Spark factory
        blue_spark = CircularParticle(
            origin=_origin,
            initial_velocity=random_offset_vector(7, 7),
            size=0.5,
            initial_color=RGB(230, 230, 255, 1),
            ending_color=RGB(0, 0, 200, 1),
            engine=engine,
            life_time=8,
            gravity=0.05,
        )
        engine.scenario.fg_shapes.append(blue_spark)

    engine.scenario.fg_shapes[0:0] = pieces


#####################################################


def get_rocket_explosion(
    damage: float,
    blast_radius: float,
    blast_damage_at_ground_zero: float,
    throw_sparks: bool = True,
    bfg_sparks: bool = False,
    with_smoke: bool = True,
    main_color: RGB | None = None,
    secondary_color: RGB | None = None,
    tertiary_color: RGB | None = None,
    little_explosions_color: RGB | None = None,
) -> "ParticleGenerator":
    def _explosion(engine: "Physics2D", source: "PhysicsEntity") -> None:
        return _rocket_explosion(
            engine=engine,
            rocket=source,
            damage=damage,
            blast_radius=blast_radius,
            blast_damage_at_ground_zero=blast_damage_at_ground_zero,
            throw_sparks=throw_sparks,
            main_color=main_color,
            secondary_color=secondary_color,
            tertiary_color=tertiary_color,
            little_explosions_color=little_explosions_color,
            bfg_sparks=bfg_sparks,
            with_smoke=with_smoke,
        )

    return _explosion


def _rocket_explosion(
    engine: "Physics2D",
    rocket: "PhysicsEntity",
    damage: float,
    blast_radius: float,
    blast_damage_at_ground_zero: float,
    throw_sparks: bool = True,
    main_color: RGB | None = None,
    secondary_color: RGB | None = None,
    tertiary_color: RGB | None = None,
    little_explosions_color: RGB | None = None,
    bfg_sparks: bool = False,
    with_smoke: bool = True,
) -> None:
    _SIZE = damage / 10
    _VELOCITY = (-0.1 * rocket.velocity).as_vector()

    particles: list[CircularParticle] = []

    eye_x = rocket.center.x - rocket.velocity.x
    eye_y = rocket.center.y - rocket.velocity.y

    color_2 = secondary_color or RGB(255, 255, 255, 1)
    end_color_2 = secondary_color.with_intensity(0.2) if secondary_color else RGB(180, 180, 120, 1)
    core_explosion_1 = CircularParticle(
        origin=PointF(x=eye_x + random_offset(), y=eye_y + random_offset()),
        initial_velocity=_VELOCITY,
        size=_SIZE * 0.5,
        engine=engine,
        size_change_type=TransitionType.LINEAR_DECREASE,
        initial_color=color_2,
        ending_color=end_color_2,
        life_time=20,
        gravity=-0.08,
    )

    color_3 = tertiary_color or RGB(255, 255, 80, 1)
    end_color_3 = (
        tertiary_color.with_intensity(0.2) if tertiary_color else RGB(140, 140, 30, intensity=1)
    )
    core_explosion_2 = CircularParticle(
        origin=PointF(x=eye_x + random_offset(), y=eye_y + random_offset()),
        initial_velocity=_VELOCITY,
        size=_SIZE * 0.75,
        engine=engine,
        size_change_type=TransitionType.LINEAR_DECREASE,
        initial_color=color_3,
        ending_color=end_color_3,  # smokelike
        life_time=25,
        gravity=-0.075,
    )
    particles.append(core_explosion_1)
    particles.append(core_explosion_2)

    _main_explosion_color = main_color or (
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
    _main_explosion_ending = (
        main_color.with_intensity(0.2) if main_color else RGB(30, 30, 30, intensity=1)
    )

    main_explosion = CircularParticle(
        origin=PointF(x=eye_x + random_offset(), y=eye_y + random_offset()),
        initial_velocity=_VELOCITY,
        size=_SIZE,
        size_change_type=TransitionType.LINEAR_DECREASE,
        initial_color=_main_explosion_color,
        ending_color=_main_explosion_ending,
        life_time=30,
        engine=engine,
        gravity=-0.07,
    )
    particles.append(main_explosion)

    secondary_explosions: list[CircularParticle] = []
    _sec_size = _SIZE**0.5

    for _ in range(round(_SIZE)):
        _sec_explosion_color = little_explosions_color or (
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
        _ending_color_4 = (
            little_explosions_color.with_intensity(0.2)
            if little_explosions_color
            else RGB(30, 30, 30, intensity=1)
        )

        _factor = _SIZE * 1.5
        sec_explosion = CircularParticle(
            origin=PointF(x=eye_x + _factor * random_offset(), y=eye_y + _factor * random_offset()),
            initial_velocity=(0.2 * _VELOCITY + 0.1 * random_offset_vector()).as_vector(),
            size=_sec_size,
            engine=engine,
            size_change_type=TransitionType.LINEAR_DECREASE,
            initial_color=_sec_explosion_color,
            ending_color=_ending_color_4,  # smokelike
            life_time=15,
            gravity=-0.05,
            particle_generator=_smoke_generator if with_smoke else None,
        )
        secondary_explosions.append(sec_explosion)

    engine.scenario.fg_shapes[0:0] = secondary_explosions

    if throw_sparks:
        for _ in range(round(_SIZE)):
            # TODO: make these sparks and other useful things into their own class
            # TODO: see why custom_sparks can't be passed into get_explosion()
            sparks = (
                CircularParticle(
                    origin=(
                        rocket.center + VectorF.random_offset_vector(blast_radius, blast_radius)
                    ).as_point(),
                    initial_velocity=(10 * random_offset_vector()).as_vector(),
                    size=1.5,
                    size_change_type=TransitionType.LINEAR_DECREASE,
                    initial_color=RGB(200, 255, 200),
                    ending_color=RGB(0, 60, 0),
                    life_time=35,
                    engine=engine,
                    floating_multi=1,
                    gravity=-0.01,
                )
                if bfg_sparks
                else CircularParticle(
                    origin=PointF(
                        x=eye_x + random_offset() * rocket.radius * 2,
                        y=eye_y + random_offset() * rocket.radius * 2,
                    ),
                    initial_velocity=(
                        VectorF(x=random_offset() * 5, y=random_offset() * 5) + _VELOCITY
                    ).as_vector(),
                    size=0.5,
                    initial_color=RGB(255, 255, 200, 1),  # almost white hot
                    ending_color=RGB(40, 5, 0, 1),  # dark orange
                    life_time=70,
                    engine=engine,
                    gravity=0.1,
                )
                # CircularParticle(
                #     origin=(
                #         rocket.center + VectorF.random_offset_vector(blast_radius, blast_radius)
                #     ).as_point(),
                #     initial_velocity=(10 * random_offset_vector()).as_vector(),
                #     size=1.5,
                #     size_change_type=TransitionType.LINEAR_DECREASE,
                #     initial_color=RGB(200, 255, 200),
                #     ending_color=RGB(0, 60, 0),
                #     life_time=35,
                #     floating_multi=1,
                #     gravity=-0.01,
                # )
            )
            particles.append(sparks)

    engine.scenario.bg_shapes[0:0] = particles

    # Render shock wave and calc blast damage
    # TODO: I don't like the particle generator taking care of damage (same with Lightning).
    # Needs to be refactored
    shock_wave = CircularParticle(
        origin=PointF(x=eye_x + random_offset(), y=eye_y + random_offset()),
        size=blast_radius / 3,
        engine=engine,
        size_change_type=TransitionType.LINEAR_INCREASE,
        final_radius=blast_radius / 1.75,
        initial_color=RGB(255, 255, 255, 1),
        ending_color=RGB(0, 0, 0, intensity=1),
        life_time=15,
    )
    engine.scenario.bg_shapes.append(shock_wave)

    # TODO: rename
    _PUSH_FACTOR = 1.2
    blast_radius_victims = engine.scenario.get_enemies_in_range(
        _PUSH_FACTOR * blast_radius, rocket, calc_distance_to_border=True
    )

    # TODO: this should damage the player as well
    for res in blast_radius_victims:
        damage_factor = 1 - (max(0, res.distance) / blast_radius)
        push_factor = 1 - (max(0, res.distance) / (_PUSH_FACTOR * blast_radius))
        # TODO: show damage in screen!
        damage = damage_factor * blast_damage_at_ground_zero
        vector_magnitude = push_factor * blast_damage_at_ground_zero / res.enemy.weight

        # Semd ememy flying away
        # TODO: Make receive_damage take care of pushing back
        res.enemy.velocity = (
            res.enemy.velocity
            + ((res.enemy.center - rocket.center).as_vector().unit_vector(vector_magnitude))
        ).as_vector()
        res.enemy.receive_damage(damage)


#################################


def rocket_trail(engine: "Physics2D", source: "PhysicsEntity", _: "PhysicsEntity | None") -> None:
    if is_out_of_sight(engine, source):
        return

    pieces: list[CircularParticle] = []

    vel_magnitude = abs(source.velocity)

    for _i in range(1, 3):
        i = _i / 2
        distance_factor = (source.radius - i) * 1
        eye_x = source.center.x - source.velocity.x * distance_factor
        eye_y = source.center.y - source.velocity.y * distance_factor

        is_odd = _i % 2 == 1
        _randomness_multi = random() * 2
        _radius_factor = random() * 1.2

        # METEOR KINDA TRAIL
        _meteor_color = (
            RGB(
                255,
                190 - (i * 10),
                50,
            ).with_intensity(1)
            if is_odd
            else RGB(
                255,
                255 - (i - 1) * 12,
                (i - 1) * 1,
            ).with_intensity(1)
        )

        _THRUST_FIRE_SPAWN_RANDOMNESS_FACTOR = 2

        def _smoke(engine: "Physics2D", source) -> None:
            return _smoke_generator(engine, source, life_time=5, floating_multi=0.1)

        thrust_fire = CircularParticle(
            origin=PointF(
                x=eye_x
                + random_offset() * _THRUST_FIRE_SPAWN_RANDOMNESS_FACTOR * _randomness_multi
                + random_offset() * 0.5,
                y=eye_y
                + random_offset() * _THRUST_FIRE_SPAWN_RANDOMNESS_FACTOR * _randomness_multi
                + random_offset() * 0.5,
            ),
            engine=engine,
            initial_velocity=VectorF(
                x=source.velocity.x * _THRUST_FIRE_SPAWN_RANDOMNESS_FACTOR * _randomness_multi * 0.1
                + random_offset() * 0.5,
                y=source.velocity.y * _THRUST_FIRE_SPAWN_RANDOMNESS_FACTOR * _randomness_multi * 0.1
                + random_offset() * 0.5,
            ),
            size=i * _radius_factor * (1 + vel_magnitude / 5),
            size_change_type=TransitionType.LINEAR_DECREASE,
            ending_color_fade_type=TransitionType.LINEAR_DECREASE,
            initial_color=_meteor_color,
            ending_color=RGB(30, 30, 30, intensity=1),  # smokelike
            life_time=15,
            gravity=-0.07,
            floating_multi=0.1,
            particle_generator=_smoke,
        )
        pieces.append(thrust_fire)

    if engine.scenario.now() % 7 == 0:
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
            size=0.3,
            initial_color=RGB(255, 255, 200, 1),  # almost white hot
            ending_color=RGB(40, 5, 0, 1),  # dark orange
            life_time=70,
            gravity=0.1,
            engine=engine,
        )
        pieces.append(sparks)

    pieces = sorted(pieces, key=random_offset)

    engine.scenario.bg_shapes[0:0] = pieces


#################################


def homing_missile_trail(
    engine: "Physics2D", source: "PhysicsEntity", target: "PhysicsEntity | None"
) -> None:
    if is_out_of_sight(engine, source):
        return

    pieces: list[CircularParticle] = []

    if target:
        vel_magnitude = abs(source.velocity)

        for _i in range(1, 3):
            i = _i / 2
            distance_factor = (source.radius - i) * 1
            eye_x = source.center.x - source.velocity.x * distance_factor
            eye_y = source.center.y - source.velocity.y * distance_factor

            is_odd = _i % 2 == 1
            _randomness_multi = random() * 2
            _radius_factor = random() * 1.2

            # METEOR KINDA TRAIL
            _meteor_color = (
                RGB(
                    255,
                    190 - (i * 10),
                    50,
                ).with_intensity(1)
                if is_odd
                else RGB(
                    255,
                    255 - (i - 1) * 12,
                    (i - 1) * 1,
                ).with_intensity(1)
            )

            _THRUST_FIRE_SPAWN_RANDOMNESS_FACTOR = 2

            def _smoke(engine: "Physics2D", source) -> None:
                return _smoke_generator(engine, source, 5)

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
                    x=source.velocity.x
                    * _THRUST_FIRE_SPAWN_RANDOMNESS_FACTOR
                    * _randomness_multi
                    * 0.1
                    + random_offset() * 0.5,
                    y=source.velocity.y
                    * _THRUST_FIRE_SPAWN_RANDOMNESS_FACTOR
                    * _randomness_multi
                    * 0.1
                    + random_offset() * 0.5,
                ),
                size=i * _radius_factor * (1 + vel_magnitude / 5),
                size_change_type=TransitionType.LINEAR_DECREASE,
                ending_color_fade_type=TransitionType.LINEAR_DECREASE,
                initial_color=_meteor_color,
                ending_color=RGB(30, 30, 30, intensity=1),  # smokelike
                life_time=15,
                gravity=-0.07,
                engine=engine,
                floating_multi=0.1,
                particle_generator=_smoke,
            )
            pieces.append(thrust_fire)

        if engine.scenario.now() % 7 == 0:
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
                size=0.3,
                initial_color=RGB(255, 255, 200, 1),  # almost white hot
                ending_color=RGB(40, 5, 0, 1),  # dark orange
                life_time=70,
                gravity=0.1,
                engine=engine,
            )
            pieces.append(sparks)

        pieces = sorted(pieces, key=random_offset)

    # If target exists, we show a red light!
    frequency = 7 if target else 12

    if engine.scenario.now() % frequency == 0:
        _initial_color = RGB(255, 120, 120, 1) if target else RGB(255, 255, 255, 1)
        _ending_color = RGB(255, 0, 0, 1) if target else RGB(80, 80, 80, 1)
        _lift_time = 3 if target else 6
        _final_radius = 10 if target else 15

        light = CircularParticle(
            origin=source,
            initial_velocity=source.velocity,
            size=0.3,
            size_change_type=TransitionType.LINEAR_INCREASE,
            initial_color=_initial_color,
            ending_color=_ending_color,
            life_time=_lift_time,
            final_radius=_final_radius,
            engine=engine,
        )
        engine.scenario.bg_shapes.append(light)

    engine.scenario.bg_shapes[0:0] = pieces
