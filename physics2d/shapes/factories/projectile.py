from random import random
from typing import TYPE_CHECKING

from model.base import PointF, VectorF
from model.theme import RGB
from physics2d.entities.equipment.projectile import Projectile
from physics2d.shapes.factories.explosion import (
    bullet_ricochet,
    get_rocket_explosion,
    homing_missile_trail,
    lightning_impact,
    rocket_trail,
)
from physics2d.shapes.line import Line
from physics2d.shapes.model.shared import TransitionType
from physics2d.shapes.particle import Lightning
from utils import get_vector_angle, random_offset, random_offset_vector

if TYPE_CHECKING:
    from physics2d.entities.base import PhysicsEntity
    from physics2d.entities.equipment.model.shared import ParticleGenerator
    from physics2d.scenario.scenario import Scenario


def bullet(scenario: "Scenario", source: "PhysicsEntity") -> None:
    _DAMAGE = 10
    _BULLET_SPEED = 10

    bullet = Projectile(
        owner=source,
        origin=source.center + random_offset_vector(),
        initial_velocity=(
            (_BULLET_SPEED + random_offset()) * source.get_last_known_direction() + source.velocity
        ).as_vector(),
        size=0.7,
        size_change_type=TransitionType.NONE,
        initial_color=RGB(127 + random_offset() * 80, 255 - random() * 60, 255, 1),
        ending_color=RGB(30, 30, 30, 1),
        life_time=50,
        damage=_DAMAGE,
        explosion_generator=bullet_ricochet,
    )
    scenario.projectiles.append(bullet)


############################################################


def buckshot(scenario: "Scenario", source: "PhysicsEntity") -> None:
    _NUM_PELLETS = 10
    _SPREAD = 3
    _DAMAGE = 8
    _BULLET_SPEED = 8

    pellets: list[Projectile] = []

    for _ in range(_NUM_PELLETS):
        pellet = Projectile(
            owner=source,
            origin=source.center + random_offset_vector(),
            initial_velocity=(
                ((_BULLET_SPEED + random_offset()) * source.get_last_known_direction())
                + source.velocity
                + VectorF(0, _SPREAD * random_offset()).rotate(
                    get_vector_angle((-source.velocity).as_vector())
                )
            ).as_vector(),
            size=0.6,
            size_change_type=TransitionType.NONE,
            initial_color=RGB(255, 0, 127),
            ending_color=RGB(30, 30, 30, intensity=1),
            life_time=50,
            damage=_DAMAGE,
            explosion_generator=bullet_ricochet,
        )
        pellets.append(pellet)

    scenario.projectiles[0:0] = pellets


############################################################


def get_lightning_bolts(_initial_color: RGB, _ending_color: RGB) -> "ParticleGenerator":
    def _lightning(scenario: "Scenario", source: "PhysicsEntity") -> None:
        return lightning_bolts(scenario, source, _initial_color, _ending_color)

    return _lightning


def lightning_bolts(
    scenario: "Scenario", source: "PhysicsEntity", _initial_color: RGB, _ending_color: RGB
) -> None:
    _MAX_RANGE = 50
    _DAMAGE = 3

    pieces: list[Line] = []

    possible_victims = [r.enemy for r in scenario.get_enemies_in_range(_MAX_RANGE, source)]

    _end_point: PointF

    if len(possible_victims) > 0:
        _size = possible_victims[0].size / 2
        _end_point = possible_victims[0].center + random_offset_vector(_size, _size)
        # TODO: is it right that the particle gen takes care of this?
        possible_victims[0].receive_damage(_DAMAGE)
        lightning_impact(
            scenario,
            possible_victims[0],
            possible_victims[0].center + random_offset_vector(_size, _size),
        )
    else:
        _end_point = source.center + random_offset_vector(40, 40)

    l1 = Lightning(
        source=source,
        end_point=_end_point,
        initial_color=_initial_color,
        ending_color=_ending_color,
        normal_noise=2,
        parallel_noise=3,
        life_time=4,
        num_segments=12,
        thickness=1,
        final_thickness=0.001,
        render_behind_player=True,
        target=possible_victims[0] if len(possible_victims) > 0 else None,
    )
    pieces.append(l1)

    scenario.fg_pieces.extend(pieces)


############################################################


def rocket(scenario: "Scenario", source: "PhysicsEntity") -> None:
    _DAMAGE = 100
    _ROCKET_SPEED = 8
    _LIFE_TIME = 100
    _BLAST_RADIUS = 15
    _MAX_BLAST_DAMAGE = 100

    rocket = Projectile(
        owner=source,
        origin=source.center + random_offset_vector(),
        initial_velocity=(
            (_ROCKET_SPEED + random_offset()) * source.get_last_known_direction() + source.velocity
        ).as_vector(),
        size=1.2,
        size_change_type=TransitionType.NONE,
        ending_color_fade_type=TransitionType.NONE,
        initial_color=RGB(127, 127, 127, 1),
        # ending_color=RGB(30, 30, 30, 1),
        life_time=_LIFE_TIME,
        damage=_DAMAGE,
        explosion_generator=get_rocket_explosion(_DAMAGE, _BLAST_RADIUS, _MAX_BLAST_DAMAGE),
        trail_generator=rocket_trail,
        density=3,
        explode_on_life_time_over=True,
    )
    scenario.projectiles.append(rocket)


############################################################


def homing_missile(scenario: "Scenario", source: "PhysicsEntity") -> None:
    _DAMAGE = 70
    _ROCKET_SPEED = 3.5
    _TRIGGER_DISTANCE = 50
    _HOMING_FACTOR = 1.2
    _HOMING_KICK_IN_TIME = 6
    _LIFE_TIME = 200
    _BLAST_RADIUS = 12
    _MAX_BLAST_DAMAGE = 80

    rocket = Projectile(
        owner=source,
        origin=source.center + random_offset_vector(),
        initial_velocity=(
            (_ROCKET_SPEED + random_offset()) * source.get_last_known_direction() + source.velocity
        ).as_vector(),
        size=1.2,
        size_change_type=TransitionType.NONE,
        ending_color_fade_type=TransitionType.NONE,
        initial_color=RGB(127, 127, 255, 1),
        # ending_color=RGB(30, 30, 30, 1),
        life_time=_LIFE_TIME,
        damage=_DAMAGE,
        explosion_generator=get_rocket_explosion(_DAMAGE, _BLAST_RADIUS, _MAX_BLAST_DAMAGE),
        trail_generator=homing_missile_trail,
        density=3,
        explode_on_life_time_over=True,
        target_acquire_threshold=_TRIGGER_DISTANCE,
        homing_factor=_HOMING_FACTOR,
        homing_kick_in_time=_HOMING_KICK_IN_TIME,
    )
    scenario.projectiles.append(rocket)


############################################################


def bfg_ball(scenario: "Scenario", source: "PhysicsEntity") -> None:
    _DAMAGE = 500
    _ROCKET_SPEED = 2
    _LIFE_TIME = 100
    _BLAST_RADIUS = 75
    _MAX_BLAST_DAMAGE = 200

    _COLOR = RGB(127, 255, 127, 1)
    _COLOR_2 = RGB(180, 255, 90, 1)
    _COLOR_3 = RGB(200, 255, 60, 1)
    _MINI_EXPLOSION_COLOR = RGB(220, 255, 127, 1)

    _explosion_generator = get_rocket_explosion(
        _DAMAGE,
        _BLAST_RADIUS,
        _MAX_BLAST_DAMAGE,
        throw_sparks=False,
        main_color=_COLOR,
        secondary_color=_COLOR_2,
        tertiary_color=_COLOR_3,
        little_explosions_color=_MINI_EXPLOSION_COLOR,
    )

    bfg_ball = Projectile(
        owner=source,
        origin=source.center + random_offset_vector(),
        initial_velocity=(
            (_ROCKET_SPEED + random_offset()) * source.get_last_known_direction() + source.velocity
        ).as_vector(),
        size=3.5,
        size_change_type=TransitionType.NONE,
        ending_color_fade_type=TransitionType.NONE,
        initial_color=_COLOR,
        # ending_color=RGB(30, 30, 30, 1),
        life_time=_LIFE_TIME,
        damage=_DAMAGE,
        explosion_generator=_explosion_generator,
        # TODO: SAME AS WEAPON, make its own
        particle_generator=get_lightning_bolts(_COLOR, _COLOR.with_intensity(0.2)),
        density=3,
        explode_on_life_time_over=True,
    )
    scenario.projectiles.append(bfg_ball)
