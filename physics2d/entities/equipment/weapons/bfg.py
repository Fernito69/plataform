import math
from typing import TYPE_CHECKING

from model.base import PointF, VectorF
from model.theme import RGB
from physics2d.entities.equipment.projectile import Projectile
from physics2d.entities.equipment.weapon import Weapon
from physics2d.shapes.factories.explosion import get_rocket_explosion
from physics2d.shapes.factories.projectile import get_lightning_bolts
from physics2d.shapes.model.shared import TransitionType
from physics2d.shapes.particle import CircularParticle
from utils import random_offset, random_offset_vector

if TYPE_CHECKING:
    from physics2d.entities.base import PhysicsEntity
    from physics2d.scenario.scenario import Scenario

_BFG_BASE_COUNTDOWN = 15
_BFG_READY_LIGHT = RGB(0, 255, 0, 1)
_BFG_DEPLETED_LIGHT = RGB(30, 50, 30, 1)
_BFG_FIRING_LIGHT = RGB(255, 0, 0, 1)


# TODO: handle blast damage
class BFG(Weapon):
    def __init__(
        self,
        scenario: "Scenario",
    ):
        super().__init__(
            name="BFG",
            scenario=scenario,
            max_ammo=5,
            refractory_period=50,
            fire_particle_generator=bfg_nozzle,
            projectile_generator=bfg_ball,
            ammo=5,
            color=_BFG_READY_LIGHT,
            recoil=3,
        )

    def _spend_ammo(self) -> None:
        self._ammo -= 1

    _firing_countdown: int = _BFG_BASE_COUNTDOWN
    _trigger_pressed: bool = False

    def do_your_thing(self) -> None:
        if self._trigger_pressed:
            self._firing_countdown -= 1

        if self._firing_countdown <= 0:
            self.color = _BFG_DEPLETED_LIGHT

            super().fire()
            self._trigger_pressed = False
            self._firing_countdown = _BFG_BASE_COUNTDOWN
        elif not self.can_shoot():
            # charging up
            _target = _BFG_READY_LIGHT.with_intensity(0.5)
            _factor = (self._refractory_limit - self._scenario.now()) / self._refractory_period
            self.color = _BFG_DEPLETED_LIGHT.with_intensity(_factor) + _target.with_intensity(
                1 - _factor
            )

        if self.can_shoot() and not self._trigger_pressed:
            self.color = _BFG_READY_LIGHT

    def fire(self) -> None:
        if not self._trigger_pressed and self.can_shoot():
            self._trigger_pressed = True
            self.color = _BFG_FIRING_LIGHT
            self._trigger_fire_sequence()

    def _trigger_fire_sequence(self) -> None:
        player = self._scenario.player
        _radius = 20
        _size = 3
        _particle_color = RGB(100, 255, 100, 1)

        # Particles, come to me!
        for angle in range(0, 360, 30):
            offset = VectorF(2 * _radius, 0).rotate(math.radians(angle), PointF(0, 0))

            def _particle(s: "Scenario", c) -> None:
                particle = CircularParticle(
                    origin=c,
                    initial_velocity=VectorF.random_offset_vector(),
                    size=0.4,
                    final_radius=0.01,
                    initial_color=_particle_color,
                    ending_color=_particle_color.with_intensity(0.2),
                    life_time=8,
                    floating_multi=1,
                )
                s.fg_pieces.append(particle)

            particle = CircularParticle(
                origin=player.center + offset,
                initial_velocity=(-(1 / _radius) * offset).as_vector(),
                size=_size * 2,
                size_change_type=TransitionType.LINEAR_DECREASE,
                initial_color=_particle_color.with_intensity(0.2),
                ending_color=_particle_color,
                life_time=_BFG_BASE_COUNTDOWN,
                particle_generator=_particle,
            )
            self._scenario.fg_pieces.append(particle)

    def secondary_fire(self) -> None: ...


#################################################################
"""PROJECTILE"""
#################################################################


def bfg_ball(scenario: "Scenario", source: "PhysicsEntity") -> None:
    _DAMAGE = 500
    _ROCKET_SPEED = 2
    _LIFE_TIME = 100
    _BLAST_RADIUS = 75
    _MAX_BLAST_DAMAGE = 200
    _TENDRILS_DAMAGE = 4

    _COLOR = RGB(127, 255, 127, 1)
    _COLOR_2 = RGB(180, 255, 90, 1)
    _COLOR_3 = RGB(200, 255, 60, 1)
    _MINI_EXPLOSION_COLOR = RGB(220, 255, 127, 1)

    _explosion = get_rocket_explosion(
        damage=_DAMAGE,
        blast_radius=_BLAST_RADIUS,
        blast_damage_at_ground_zero=_MAX_BLAST_DAMAGE,
        main_color=_COLOR,
        secondary_color=_COLOR_2,
        tertiary_color=_COLOR_3,
        little_explosions_color=_MINI_EXPLOSION_COLOR,
        with_smoke=False,
        throw_sparks=True,
        bfg_sparks=True,
    )

    bfg_ball = Projectile(
        owner=source,
        offset_from_origin=random_offset_vector(),
        initial_velocity=(
            (_ROCKET_SPEED + random_offset()) * source.get_aiming_direction()
        ).as_vector(),
        size=3.5,
        size_change_type=TransitionType.NONE,
        ending_color_fade_type=TransitionType.NONE,
        initial_color=_COLOR,
        # ending_color=RGB(30, 30, 30, 1),
        life_time=_LIFE_TIME,
        damage=_DAMAGE,
        explosion_generator=_explosion,
        particle_generator=get_lightning_bolts(
            _COLOR,
            _COLOR.with_intensity(0.2),
            _TENDRILS_DAMAGE,
            damage_range=40,
        ),
        density=3,
        explode_on_life_time_over=True,
    )
    scenario.projectiles.append(bfg_ball)


#################################################################
"""NOZZLE"""
#################################################################


def bfg_nozzle(scenario: "Scenario", source: "PhysicsEntity") -> None:
    direction = source.get_aiming_direction()
    # TODO: this is copy/paste, generalize
    _bfg_color = RGB(100, 255, 100)

    bfg_1 = CircularParticle(
        origin=source.center + 7 * (direction) + random_offset_vector(),
        initial_velocity=source.velocity,
        size=9,
        size_change_type=TransitionType.EXPONENTIAL_DECREASE,
        initial_color=_bfg_color,
        ending_color=RGB(90, 120, 30, intensity=1),
        life_time=12,
    )

    bfg_2 = CircularParticle(
        origin=source.center + 9 * (direction) + random_offset_vector(),
        initial_velocity=source.velocity,
        size=7,
        size_change_type=TransitionType.EXPONENTIAL_DECREASE,
        initial_color=RGB(220, 255, 20),
        ending_color=RGB(110, 150, 30),
        life_time=10,
    )
    bfg_3 = CircularParticle(
        origin=source.center + 13 * (direction) + 2 * random_offset_vector(),
        initial_velocity=source.velocity,
        size=6,
        size_change_type=TransitionType.EXPONENTIAL_DECREASE,
        initial_color=RGB(170, 255, 20),
        ending_color=RGB(60, 120, 20),
        life_time=9,
    )
    fire_white = CircularParticle(
        origin=source.center + 6 * (direction) + random_offset_vector(),
        initial_velocity=source.velocity,
        size=6,
        size_change_type=TransitionType.EXPONENTIAL_DECREASE,
        initial_color=RGB(230, 255, 230, 1),
        ending_color=RGB(150, 200, 150, 1),
        life_time=8,
    )

    # sparks: list[CircularParticle] = []

    # spark = CircularParticle(
    #     origin=source.center + 6 * (direction + random_offset_vector()),
    #     initial_velocity=(
    #         source.velocity
    #         + 5 * (direction + VectorF(0, random_offset() * 2).rotate(get_vector_angle(direction)))
    #     ).as_vector(),
    #     size=0.5,
    #     size_change_type=TransitionType.NONE,
    #     initial_color=RGB(255, 255, 200, 1),  # almost white hot
    #     ending_color=RGB(80, 10, 0, 1),  # dark orange
    #     life_time=5,
    #     floating_multi=0.4,
    # )
    # sparks.append(spark)

    scenario.fg_pieces.extend([fire_white, bfg_1, bfg_2, bfg_3])


########

################


########
