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


class Shotgun(Weapon):
    def __init__(
        self,
        scenario: "Scenario",
    ):
        super().__init__(
            name="Shotgun",
            scenario=scenario,
            max_ammo=100,
            refractory_period=18,
            fire_particle_generator=shotgun_nozzle,
            projectile_generator=buckshot,
            ammo=100,
            color=RGB(255, 0, 127, 1),
        )

    def _spend_ammo(self) -> None:
        self._ammo -= 1

    def _effect_on_player(self) -> None:
        # recoil!
        self._scenario.player.velocity = (
            self._scenario.player.velocity - (self._scenario.player.get_aiming_direction())
        ).as_vector()

    def secondary_fire(self) -> None: ...


#################################################################
"""PROJECTILE"""
#################################################################


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
                ((_BULLET_SPEED + random_offset()) * source.get_aiming_direction())
                + VectorF(0, _SPREAD * random_offset()).rotate(
                    get_vector_angle((-source.get_aiming_direction()).as_vector())
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


#################################################################
"""NOZZLE"""
#################################################################


def shotgun_nozzle(scenario: "Scenario", source: "PhysicsEntity") -> None:
    direction = source.get_aiming_direction()

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
        origin=source.center + 7 * (direction) + random_offset_vector(),
        initial_velocity=source.velocity,
        size=6,
        size_change_type=TransitionType.EXPONENTIAL_DECREASE,
        initial_color=_fire_1_color,
        ending_color=RGB(150, 120, 30, intensity=1),
        life_time=7,
    )
    fire_2 = CircularParticle(
        origin=source.center + 9 * (direction) + random_offset_vector(),
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
        origin=source.center + 13 * (direction) + 2 * random_offset_vector(),
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
        origin=source.center + 6 * (direction) + random_offset_vector(),
        initial_velocity=source.velocity,
        size=6,
        size_change_type=TransitionType.EXPONENTIAL_DECREASE,
        initial_color=RGB(255, 200, 255, 1),
        ending_color=RGB(200, 150, 200, 1),
        life_time=5,
    )
    sparks: list[CircularParticle] = []

    spark = CircularParticle(
        origin=source.center + 6 * (direction + random_offset_vector()),
        initial_velocity=(
            source.velocity
            + 5 * (direction + VectorF(0, random_offset() * 2).rotate(get_vector_angle(direction)))
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
