from typing import TYPE_CHECKING

from model.base import VectorF
from model.theme import RGB
from physics2d.entities.equipment.weapon import Weapon
from physics2d.shape.factories.explosion import get_smoke_generator
from physics2d.shape.factories.projectile import rocket
from physics2d.shape.model.shared import TransitionType
from physics2d.shape.particle.circular_particle import CircularParticle
from utils import random_offset

if TYPE_CHECKING:
    from physics2d.entities.base import PhysicsEntity
    from physics2d.entities.model.shared import ParticleGenerator
    from physics2d.physics2d import Physics2D


class RocketLauncher(Weapon):
    def __init__(
        self,
        engine: "Physics2D",
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
            engine=engine,
            max_ammo=max_ammo,
            refractory_period=refractory_period,
            fire_particle_generator=fire_particle_generator or rocket_launcher_nozzle,
            projectile_generator=projectile_generator or _rocket,
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
        engine: "Physics2D",
    ):
        super().__init__(
            max_ammo=10,
            refractory_period=25,
            ammo=10,
            color=RGB(160, 10, 4, 1),
            recoil=2,
            projectile_generator=heavy_rocket,
            name="HeavyRocketLauncher",
            engine=engine,
        )

    def _spend_ammo(self) -> None:
        self._ammo -= 1

    def secondary_fire(self) -> None: ...


#################################################################
"""PROJECTILE"""
#################################################################


# TODO: refactor these two with get_rocket factory
def heavy_rocket(engine: "Physics2D", source: "PhysicsEntity") -> None:
    _DAMAGE = 250
    _ROCKET_SPEED = 5
    _LIFE_TIME = 120
    _BLAST_RADIUS = 60
    _MAX_BLAST_DAMAGE = 110
    _SIZE = 1.7

    _rocket = rocket(
        engine=engine,
        source=source,
        damage=_DAMAGE,
        rocket_speed=_ROCKET_SPEED,
        life_time=_LIFE_TIME,
        blast_radius=_BLAST_RADIUS,
        max_blast_damage=_MAX_BLAST_DAMAGE,
        size=_SIZE,
        color=RGB(255, 100, 100),
    )
    engine.scenario.projectiles.append(_rocket)


def _rocket(engine: "Physics2D", source: "PhysicsEntity") -> None:
    _DAMAGE = 100
    _ROCKET_SPEED = 8
    _LIFE_TIME = 100
    _BLAST_RADIUS = 20
    _MAX_BLAST_DAMAGE = 100
    _SIZE = 1.2

    _rocket = rocket(
        engine=engine,
        source=source,
        damage=_DAMAGE,
        rocket_speed=_ROCKET_SPEED,
        life_time=_LIFE_TIME,
        blast_radius=_BLAST_RADIUS,
        max_blast_damage=_MAX_BLAST_DAMAGE,
        size=_SIZE,
    )
    engine.scenario.projectiles.append(_rocket)


#################################################################
"""NOZZLE"""
#################################################################


def rocket_launcher_nozzle(engine: "Physics2D", source: "PhysicsEntity") -> None:
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
        origin=source.center + 7 * (direction) + VectorF.random_offset_vector(),
        initial_velocity=source.velocity,
        size=6,
        size_change_type=TransitionType.EXPONENTIAL_DECREASE,
        initial_color=_fire_1_color,
        ending_color=RGB(150, 120, 30, intensity=1),
        life_time=7,
        engine=engine,
    )

    fire_2 = CircularParticle(
        origin=source.center + 9 * (direction) + VectorF.random_offset_vector(),
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
        engine=engine,
        particle_generator=get_smoke_generator(
            life_time=15,
            random_offset_threshold=-0.25,
            initial_velocity=(0.2 * engine.scenario.player.get_aiming_direction()).as_vector(),
        ),
    )
    fire_3 = CircularParticle(
        origin=source.center + 13 * (direction) + 2 * VectorF.random_offset_vector(),
        initial_velocity=source.velocity,
        size=4,
        engine=engine,
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
        origin=source.center + 6 * (direction) + VectorF.random_offset_vector(),
        initial_velocity=source.velocity,
        size=6,
        engine=engine,
        size_change_type=TransitionType.EXPONENTIAL_DECREASE,
        initial_color=RGB(255, 200, 255, 1),
        ending_color=RGB(200, 150, 200, 1),
        life_time=5,
    )
    sparks: list[CircularParticle] = []

    spark = CircularParticle(
        origin=source.center + 6 * (direction + VectorF.random_offset_vector()),
        initial_velocity=(
            source.velocity
            + 5 * (direction + VectorF(0, random_offset() * 2).rotate(direction.get_angle()))
        ).as_vector(),
        size=0.5,
        size_change_type=TransitionType.NONE,
        initial_color=RGB(255, 255, 200, 1),  # almost white hot
        ending_color=RGB(80, 10, 0, 1),  # dark orange
        life_time=5,
        gravity=0.1,
        engine=engine,
    )
    sparks.append(spark)

    engine.scenario.fg_shapes.extend(sparks + [fire_white, fire_1, fire_2, fire_3])
