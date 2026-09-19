from typing import TYPE_CHECKING

from model.base import VectorF
from model.theme import RGB
from physics2d.entities.equipment.projectile import Projectile
from physics2d.entities.equipment.weapon import Weapon
from physics2d.shape.factories.explosion import (
    get_rocket_explosion,
    get_smoke_generator,
    rocket_trail,
)
from physics2d.shape.model.shared import TransitionType
from physics2d.shape.particle.circular_particle import CircularParticle
from utils import get_vector_angle, random_offset, random_offset_vector

if TYPE_CHECKING:
    from physics2d.entities.base import PhysicsEntity
    from physics2d.entities.model.shared import ParticleGenerator
    from physics2d.scenario.scenario import Scenario


class RocketLauncher(Weapon):
    def __init__(
        self,
        scenario: "Scenario",
        recoil: float = 1.5,
        max_ammo: int = 50,
        refractory_period: int = 15,
        fire_particle_generator: "ParticleGenerator | None" = None,
        projectile_generator: "ParticleGenerator | None" = None,
        ammo=50,
        color=RGB(220, 32, 12, 1),
        name="RocketLauncher",
    ):
        super().__init__(
            name=name,
            scenario=scenario,
            max_ammo=max_ammo,
            refractory_period=refractory_period,
            fire_particle_generator=fire_particle_generator or rocket_launcher_nozzle,
            projectile_generator=projectile_generator or rocket,
            ammo=ammo,
            color=color,
            recoil=recoil,
        )

    def _spend_ammo(self) -> None:
        self._ammo -= 1

    def secondary_fire(self) -> None: ...


class HeavyRocketLauncher(RocketLauncher):
    def __init__(
        self,
        scenario: "Scenario",
    ):
        super().__init__(
            scenario=scenario,
            max_ammo=10,
            refractory_period=25,
            ammo=10,
            color=RGB(160, 10, 4, 1),
            recoil=2,
            projectile_generator=heavy_rocket,
            name="HeavyRocketLauncher",
        )

    def _spend_ammo(self) -> None:
        self._ammo -= 1

    def secondary_fire(self) -> None: ...


#################################################################
"""PROJECTILE"""
#################################################################


def _rocket_factory(
    source: "PhysicsEntity",
    rocket_speed: float,
    life_time: int,
    damage: float,
    blast_radius: float,
    max_blast_damage: float,
    size: float,
    color: RGB = RGB(127, 127, 127, 1),
):
    return Projectile(
        owner=source,
        offset_from_origin=random_offset_vector(),
        initial_velocity=(
            (rocket_speed + random_offset()) * source.get_aiming_direction()
        ).as_vector(),
        size=size,
        size_change_type=TransitionType.NONE,
        ending_color_fade_type=TransitionType.NONE,
        initial_color=color,
        life_time=life_time,
        damage=damage,
        explosion_generator=get_rocket_explosion(damage, blast_radius, max_blast_damage),
        trail_generator=rocket_trail,
        density=3,
        explode_on_life_time_over=True,
    )


def heavy_rocket(scenario: "Scenario", source: "PhysicsEntity") -> None:
    _DAMAGE = 250
    _ROCKET_SPEED = 5
    _LIFE_TIME = 120
    _BLAST_RADIUS = 60
    _MAX_BLAST_DAMAGE = 110
    _SIZE = 1.7

    # rocket = Projectile(
    #     owner=source,
    #     origin=source.center + random_offset_vector(),
    #     initial_velocity=(
    #         (_ROCKET_SPEED + random_offset()) * source.get_aiming_direction()
    #     ).as_vector(),
    #     size=1.2,
    #     size_change_type=TransitionType.NONE,
    #     ending_color_fade_type=TransitionType.NONE,
    #     initial_color=RGB(127, 127, 127, 1),
    #     # ending_color=RGB(30, 30, 30, 1),
    #     life_time=_LIFE_TIME,
    #     damage=_DAMAGE,
    #     explosion_generator=get_rocket_explosion(_DAMAGE, _BLAST_RADIUS, _MAX_BLAST_DAMAGE),
    #     trail_generator=rocket_trail,
    #     density=3,
    #     explode_on_life_time_over=True,
    # )
    rocket = _rocket_factory(
        source,
        damage=_DAMAGE,
        rocket_speed=_ROCKET_SPEED,
        life_time=_LIFE_TIME,
        blast_radius=_BLAST_RADIUS,
        max_blast_damage=_MAX_BLAST_DAMAGE,
        size=_SIZE,
        color=RGB(255, 100, 100),
    )
    scenario.projectiles.append(rocket)


def rocket(scenario: "Scenario", source: "PhysicsEntity") -> None:
    _DAMAGE = 100
    _ROCKET_SPEED = 8
    _LIFE_TIME = 100
    _BLAST_RADIUS = 20
    _MAX_BLAST_DAMAGE = 100
    _SIZE = 1.2

    rocket = _rocket_factory(
        source,
        damage=_DAMAGE,
        rocket_speed=_ROCKET_SPEED,
        life_time=_LIFE_TIME,
        blast_radius=_BLAST_RADIUS,
        max_blast_damage=_MAX_BLAST_DAMAGE,
        size=_SIZE,
    )
    scenario.projectiles.append(rocket)


#################################################################
"""NOZZLE"""
#################################################################


def rocket_launcher_nozzle(scenario: "Scenario", source: "PhysicsEntity") -> None:
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
        particle_generator=get_smoke_generator(
            life_time=15,
            random_offset_threshold=-0.25,
            initial_velocity=(0.2 * scenario.player.get_aiming_direction()).as_vector(),
        ),
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

    scenario.fg_shapes.extend(sparks + [fire_white, fire_1, fire_2, fire_3])
