from random import random
from typing import TYPE_CHECKING

from model.base import VectorF
from model.theme import RGB
from physics2d.entities.equipment.projectile import Projectile
from physics2d.entities.equipment.weapon import Weapon
from physics2d.shapes.factories.explosion import bullet_ricochet
from physics2d.shapes.model.shared import TransitionType
from physics2d.shapes.particle import CircularParticle
from utils import get_vector_angle, random_offset, random_offset_vector

if TYPE_CHECKING:
    from physics2d.entities.base import PhysicsEntity
    from physics2d.scenario.scenario import Scenario


class MachineGun(Weapon):
    def __init__(
        self,
        scenario: "Scenario",
    ):
        super().__init__(
            name="MachineGun",
            scenario=scenario,
            max_ammo=1000,
            refractory_period=2,
            fire_particle_generator=machine_gun_nozzle,
            projectile_generator=bullet,
            ammo=1000,
            color=RGB(127, 127, 127, 1),
        )

    def _spend_ammo(self) -> None:
        self._ammo -= 1

    def secondary_fire(self) -> None:
        ...
        # TODO: todo stuff and bind the key


#################################################################
"""PROJECTILE"""
#################################################################


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


#################################################################
"""NOZZLE"""
#################################################################


def machine_gun_nozzle(scenario: "Scenario", source: "PhysicsEntity") -> None:
    _offset = 6.5

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
        origin=source.center
        + (_offset + 0.5) * (source.get_last_known_direction())
        + random_offset_vector(),
        initial_velocity=source.velocity,
        size=4,
        size_change_type=TransitionType.EXPONENTIAL_DECREASE,
        initial_color=_fire_1_color,
        ending_color=RGB(150, 120, 30, intensity=1),
        life_time=5,
    )
    fire_2 = CircularParticle(
        origin=source.center
        + (_offset + 3) * (source.get_last_known_direction())
        + random_offset_vector(),
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
        + (_offset + 5.5) * (source.get_last_known_direction())
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
        origin=source.center
        + (_offset) * (source.get_last_known_direction())
        + random_offset_vector(),
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
            + (_offset) * (source.get_last_known_direction() + random_offset_vector()),
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
