from typing import TYPE_CHECKING

from model.theme import RGB
from physics2d.entities.equipment.projectile import Projectile
from physics2d.entities.equipment.weapon import Weapon
from physics2d.entities.equipment.weapons.rocket_launcher import rocket_launcher_nozzle
from physics2d.shapes.factories.explosion import get_rocket_explosion, homing_missile_trail
from physics2d.shapes.model.shared import TransitionType
from utils import random_offset, random_offset_vector

if TYPE_CHECKING:
    from physics2d.entities.base import PhysicsEntity
    from physics2d.scenario.scenario import Scenario


class HomingMissileLauncher(Weapon):
    def __init__(
        self,
        scenario: "Scenario",
    ):
        super().__init__(
            name="HomingMissileLauncher",
            scenario=scenario,
            max_ammo=30,
            refractory_period=20,
            fire_particle_generator=rocket_launcher_nozzle,
            projectile_generator=homing_missile,
            ammo=30,
            color=RGB(180, 90, 255, 1),
            recoil=1,
        )

    def _spend_ammo(self) -> None:
        self._ammo -= 1

    def secondary_fire(self) -> None: ...


#################################################################
"""PROJECTILE"""
#################################################################


def homing_missile(scenario: "Scenario", source: "PhysicsEntity") -> None:
    _DAMAGE = 70
    _ROCKET_SPEED = 3.5
    _TRIGGER_DISTANCE = 50
    _HOMING_FACTOR = 1.2
    _HOMING_KICK_IN_TIME = 10
    _LIFE_TIME = 200
    _BLAST_RADIUS = 15
    _MAX_BLAST_DAMAGE = 60

    rocket = Projectile(
        owner=source,
        origin=source.center + random_offset_vector(),
        initial_velocity=(
            (_ROCKET_SPEED + random_offset()) * source.get_aiming_direction()
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
