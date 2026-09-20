from random import random
from typing import TYPE_CHECKING

from model.base import VectorF
from model.theme import RGB
from physics2d.entities.equipment.projectile import Projectile
from physics2d.entities.equipment.weapon import Weapon
from physics2d.shape.factories.explosion import bullet_ricochet
from physics2d.shape.model.shared import TransitionType
from physics2d.shape.particle.circular_particle import CircularParticle
from utils import get_vector_angle, random_offset, random_offset_vector

if TYPE_CHECKING:
    from physics2d.entities.base import PhysicsEntity
    from physics2d.physics2d import Physics2D


class MachineGun(Weapon):
    def __init__(self, engine: "Physics2D"):
        super().__init__(
            name="MachineGun",
            engine=engine,
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


class HeavyMachineGun(Weapon):
    _ammo_per_gametick: int

    def __init__(self, engine: "Physics2D", ammo_per_gametick: int = 2):
        self._ammo_per_gametick = ammo_per_gametick

        def _bullets(engine: "Physics2D", source: "PhysicsEntity"):
            return gatling_bullets(engine, source, ammo_per_gametick)

        super().__init__(
            recoil=0.1,
            name="HeavyMachineGun",
            max_ammo=4000,
            refractory_period=0,
            fire_particle_generator=heavy_machine_gun_nozzle,
            projectile_generator=_bullets,
            ammo=4000,
            color=RGB(90, 90, 90, 1),
            engine=engine,
        )

    def _spend_ammo(self) -> None:
        self._ammo -= self._ammo_per_gametick

    def secondary_fire(self) -> None:
        ...
        # TODO: todo stuff and bind the key


#################################################################
"""PROJECTILE"""
#################################################################


def bullet(engine: "Physics2D", source: "PhysicsEntity") -> None:
    _DAMAGE = 10
    _BULLET_SPEED = 10

    velocity = ((_BULLET_SPEED + random_offset()) * source.get_aiming_direction()).as_vector()

    bullet = Projectile(
        owner=source,
        offset_from_origin=random_offset_vector(),
        initial_velocity=velocity,
        size=0.7,
        size_change_type=TransitionType.NONE,
        initial_color=RGB(127 + random_offset() * 80, 255 - random() * 60, 255, 1),
        ending_color=RGB(30, 30, 30, 1),
        life_time=50,
        damage=_DAMAGE,
        explosion_generator=bullet_ricochet,
        engine=engine,
    )
    engine.scenario.projectiles.append(bullet)


def gatling_bullets(engine: "Physics2D", source: "PhysicsEntity", bullets_per_frame: int) -> None:
    _DAMAGE = 5
    _BULLET_SPEED = 9

    velocity = ((_BULLET_SPEED + random_offset()) * source.get_aiming_direction()).as_vector()
    angle = get_vector_angle(velocity)

    bullets = []

    for i in range(bullets_per_frame):
        factor = 10 * i / bullets_per_frame

        bullet = Projectile(
            owner=source,
            initial_velocity=velocity,
            size=0.7,
            size_change_type=TransitionType.NONE,
            initial_color=RGB(255 - random() * 80, 255 - random() * 60, 0, 1),
            ending_color=RGB(30, 30, 30, 1),
            life_time=50,
            damage=_DAMAGE,
            explosion_generator=bullet_ricochet,
            offset_from_origin=VectorF(factor, random_offset() * 4).rotate(angle).as_vector(),
            engine=engine,
        )
        bullets.append(bullet)

    engine.scenario.projectiles.extend(bullets)


#################################################################
"""NOZZLE"""
#################################################################


def machine_gun_nozzle(engine: "Physics2D", source: "PhysicsEntity") -> None:
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
    direction = source.get_aiming_direction()
    fire_1 = CircularParticle(
        origin=source.center + (_offset + 0.5) * direction + random_offset_vector(),
        initial_velocity=source.velocity,
        size=4,
        size_change_type=TransitionType.EXPONENTIAL_DECREASE,
        initial_color=_fire_1_color,
        ending_color=RGB(150, 120, 30, intensity=1),
        life_time=5,
        engine=engine,
    )
    fire_2 = CircularParticle(
        origin=source.center + (_offset + 3) * direction + random_offset_vector(),
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
        engine=engine,
    )
    fire_3 = CircularParticle(
        origin=source.center + (_offset + 5.5) * direction + 2 * random_offset_vector(),
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
        engine=engine,
    )
    fire_white = CircularParticle(
        origin=source.center + (_offset) * direction + random_offset_vector(),
        initial_velocity=source.velocity,
        size=3,
        size_change_type=TransitionType.EXPONENTIAL_DECREASE,
        initial_color=RGB(255, 200, 255, 1),
        ending_color=RGB(200, 150, 200, 1),
        life_time=4,
        engine=engine,
    )
    sparks: list[CircularParticle] = []
    if engine.scenario.now() % 3 == 0:
        spark = CircularParticle(
            origin=source.center + (_offset) * (direction + random_offset_vector()),
            initial_velocity=(
                source.velocity
                + 5
                * (direction + VectorF(0, random_offset() * 2).rotate(get_vector_angle(direction)))
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


def heavy_machine_gun_nozzle(engine: "Physics2D", source: "PhysicsEntity") -> None:
    _offset = 8.5
    _base_size = 4

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
    direction = source.get_aiming_direction()
    fire_1 = CircularParticle(
        origin=source.center + (_offset + 1) * direction + random_offset_vector(),
        initial_velocity=(1.2 * source.velocity).as_vector(),
        size=_base_size + 2,
        size_change_type=TransitionType.EXPONENTIAL_DECREASE,
        initial_color=_fire_1_color,
        ending_color=RGB(150, 120, 30, intensity=1),
        life_time=5,
        engine=engine,
    )
    fire_2 = CircularParticle(
        origin=source.center + (_offset + 6) * direction + random_offset_vector(),
        initial_velocity=(1.4 * source.velocity).as_vector(),
        size=_base_size + 1.5,
        size_change_type=TransitionType.EXPONENTIAL_DECREASE,
        initial_color=RGB(
            255,
            120,
            20,
        ).with_intensity(1),
        ending_color=RGB(150, 90, 30, intensity=1),
        life_time=5,
        engine=engine,
    )
    fire_3 = CircularParticle(
        origin=source.center + (_offset + 11) * direction + 2 * random_offset_vector(),
        initial_velocity=(1.7 * source.velocity).as_vector(),
        size=_base_size,
        size_change_type=TransitionType.EXPONENTIAL_DECREASE,
        initial_color=RGB(
            255,
            80,
            20,
        ).with_intensity(1),
        engine=engine,
        ending_color=RGB(120, 60, 20, intensity=1),
        life_time=5,
    )
    fire_4 = CircularParticle(
        origin=source.center + (_offset + 14) * direction + 2 * random_offset_vector(),
        initial_velocity=(2 * source.velocity).as_vector(),
        size=_base_size * 0.75,
        size_change_type=TransitionType.LINEAR_DECREASE,
        initial_color=RGB(
            255,
            50,
            10,
        ).with_intensity(1),
        ending_color=RGB(100, 40, 10, intensity=1),
        life_time=4,
        engine=engine,
        floating_multi=0.5,
    )
    fire_white = CircularParticle(
        origin=source.center + (_offset) * direction + random_offset_vector(),
        initial_velocity=(2.3 * source.velocity).as_vector(),
        size=_base_size + 1,
        size_change_type=TransitionType.EXPONENTIAL_DECREASE,
        initial_color=RGB(255, 200, 255, 1),
        ending_color=RGB(200, 150, 200, 1),
        life_time=4,
        engine=engine,
    )

    sparks: list[CircularParticle] = []
    spark = CircularParticle(
        origin=source.center + (_offset) * (direction + random_offset_vector()),
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
        engine=engine,
    )
    sparks.append(spark)

    engine.scenario.fg_shapes.extend(sparks + [fire_white, fire_1, fire_2, fire_3, fire_4])
