from typing import TYPE_CHECKING

from model.base import VectorF
from model.theme import RGB
from physics2d.entities.equipment.projectile import Projectile
from physics2d.entities.equipment.weapon import Weapon
from physics2d.shapes.factories.explosion import get_rocket_explosion, rocket_trail, smoke_generator
from physics2d.shapes.model.shared import TransitionType
from physics2d.shapes.particle import CircularParticle
from utils import get_vector_angle, random_offset, random_offset_vector

if TYPE_CHECKING:
    from physics2d.entities.base import PhysicsEntity
    from physics2d.scenario.scenario import Scenario


class RocketLauncher(Weapon):
    def __init__(
        self,
        scenario: "Scenario",
    ):
        super().__init__(
            name="RocketLauncher",
            scenario=scenario,
            max_ammo=50,
            refractory_period=15,
            fire_particle_generator=rocket_launcher_nozzle,
            projectile_generator=rocket,
            ammo=50,
            color=RGB(220, 32, 12, 1),
        )

    def _spend_ammo(self) -> None:
        self._ammo -= 1

    def _effect_on_player(self) -> None:
        # recoil!
        self._scenario.player.velocity = (
            self._scenario.player.velocity
            - 1.5 * (self._scenario.player.get_last_known_direction())
        ).as_vector()

    def secondary_fire(self) -> None: ...


#################################################################
"""PROJECTILE"""
#################################################################


def rocket(scenario: "Scenario", source: "PhysicsEntity") -> None:
    _DAMAGE = 100
    _ROCKET_SPEED = 8
    _LIFE_TIME = 100
    _BLAST_RADIUS = 20
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


#################################################################
"""NOZZLE"""
#################################################################


def rocket_launcher_nozzle(scenario: "Scenario", source: "PhysicsEntity") -> None:
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
        origin=source.center + 7 * (source.get_last_known_direction()) + random_offset_vector(),
        initial_velocity=source.velocity,
        size=6,
        size_change_type=TransitionType.EXPONENTIAL_DECREASE,
        initial_color=_fire_1_color,
        ending_color=RGB(150, 120, 30, intensity=1),
        life_time=7,
    )

    def _smoke(engine, source: "PhysicsEntity") -> None:
        return smoke_generator(
            engine,
            source,
            life_time=15,
            random_offset_threshold=-0.25,
            initial_velocity=scenario.player.get_last_known_direction(0.2),
        )

    fire_2 = CircularParticle(
        origin=source.center + 9 * (source.get_last_known_direction()) + random_offset_vector(),
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
        particle_generator=_smoke,
    )
    fire_3 = CircularParticle(
        origin=source.center
        + 13 * (source.get_last_known_direction())
        + 2 * random_offset_vector(),
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
        origin=source.center + 6 * (source.get_last_known_direction()) + random_offset_vector(),
        initial_velocity=source.velocity,
        size=6,
        size_change_type=TransitionType.EXPONENTIAL_DECREASE,
        initial_color=RGB(255, 200, 255, 1),
        ending_color=RGB(200, 150, 200, 1),
        life_time=5,
    )
    sparks: list[CircularParticle] = []

    spark = CircularParticle(
        origin=source.center + 6 * (source.get_last_known_direction() + random_offset_vector()),
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
