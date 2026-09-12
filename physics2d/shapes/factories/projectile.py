from random import random
from typing import TYPE_CHECKING

from model.base import PointF, VectorF
from model.theme import RGB
from physics2d.entities.equipment.projectile import Projectile
from physics2d.shapes.factories.explosion import bullet_ricochet, lightning_impact
from physics2d.shapes.line import Line
from physics2d.shapes.model.shared import TransitionType
from physics2d.shapes.particle import Lightning
from utils import get_vector_angle, random_offset, random_offset_vector

if TYPE_CHECKING:
    from physics2d.entities.base import PhysicsEntity
    from physics2d.entities.enemy import Enemy
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


def lightning_bolts(scenario: "Scenario", source: "PhysicsEntity") -> None:
    _MAX_RANGE = 50
    _DAMAGE = 3

    pieces: list[Line] = []

    possible_victims: list["Enemy"] = [
        enemy
        for enemy, distance in sorted(
            [(e, abs(source.position - e.position)) for e in scenario.enemies], key=lambda v: v[1]
        )
        if distance < _MAX_RANGE
    ]

    vel_magnitude = abs(source.velocity)
    _initial_color = RGB(255, 220, 200, 1)
    _ending_color = RGB(0, 0, 100, 1)
    _end_point: PointF

    if len(possible_victims) > 0:
        _end_point = possible_victims[0].position
        # TODO: is it right that the particle gen takes care of this?
        possible_victims[0].receive_damage(_DAMAGE)
        lightning_impact(scenario, possible_victims[0])
    else:
        _random_magnitude = (vel_magnitude) + source.radius + (20 if vel_magnitude == 0 else 0)
        _end_point = (
            random_offset_vector(_random_magnitude, _random_magnitude)
            + source.center
            + source.velocity
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
        life_time=3,
        num_segments=7,
        thickness=1,
        final_thickness=0.001,
    )
    pieces.append(l1)

    scenario.bg_pieces[0:0] = pieces
