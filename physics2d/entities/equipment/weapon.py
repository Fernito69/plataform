import math
from abc import abstractmethod
from typing import TYPE_CHECKING

from model.base import PointF, VectorF
from model.theme import RGB
from physics2d.entities.equipment.model.shared import ParticleGenerator
from physics2d.shapes.factories.nozzle import (
    bfg_nozzle,
    lightning_nozzle,
    machine_gun_nozzle,
    rocket_launcher_nozzle,
    shotgun_nozzle,
)
from physics2d.shapes.factories.projectile import (
    bfg_ball,
    buckshot,
    bullet,
    get_lightning_bolts,
    homing_missile,
    rocket,
)
from physics2d.shapes.model.shared import TransitionType
from physics2d.shapes.particle import CircularParticle

if TYPE_CHECKING:
    from physics2d.scenario.scenario import Scenario


class Weapon:
    name: str
    color: RGB

    _scenario: "Scenario"
    _fire_particle_generator: ParticleGenerator
    _projectile_generator: ParticleGenerator

    # How long it has to wait until next shot
    _refractory_period: int
    _refractory_limit: int

    _ammo: int
    _max_ammo: int

    def __init__(
        self,
        scenario: "Scenario",
        name: str,
        color: RGB,
        max_ammo: int,
        fire_particle_generator: ParticleGenerator,
        projectile_generator: ParticleGenerator,
        refractory_period: int,
        ammo: int = 0,
    ):
        self._scenario = scenario
        self.name = name
        self.color = color
        self._fire_particle_generator = fire_particle_generator
        self._projectile_generator = projectile_generator
        self._max_ammo = max_ammo
        self._refractory_period = refractory_period
        self._ammo = min(ammo, max_ammo)
        self._refractory_limit = scenario.now()

    def fire(self) -> None:
        if (
            self._ammo <= 0
            or self._refractory_limit > self._scenario.now()
            or (
                self._scenario.player.get_last_known_direction().x == 0
                and self._scenario.player.get_last_known_direction().y == 0
            )
        ):
            return

        self._fire_particle_generator(self._scenario, self._scenario.player)
        self._projectile_generator(self._scenario, self._scenario.player)

        self._spend_ammo()
        self._effect_on_player()

        self._refractory_limit = self._scenario.now() + self._refractory_period

    def can_shoot(self) -> bool:
        return self._refractory_limit <= self._scenario.now()

    def do_your_thing(self) -> None:
        """No-op for most weapons"""
        ...

    @abstractmethod
    def secondary_fire(self) -> None:
        ...
        # TODO: implement _secondary_projectile_generator, etc

    @abstractmethod
    def _spend_ammo(self) -> None:
        ...
        """Spend an amount of ammo per shot"""

    @abstractmethod
    def _effect_on_player(self) -> None:
        ...
        """e.g. recoil, etc."""


#################################################################


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
            self._scenario.player.velocity - (self._scenario.player.get_last_known_direction())
        ).as_vector()

    def secondary_fire(self) -> None: ...


#################################################################


class LightningGun(Weapon):
    def __init__(
        self,
        scenario: "Scenario",
    ):
        _START_COLOR = RGB(255, 220, 200, 1)
        _END_COLOR = RGB(0, 0, 100, 1)
        _DAMAGE = 3
        _DAMAGE_RANGE = 50

        super().__init__(
            name="LightningGun",
            scenario=scenario,
            max_ammo=2000,
            refractory_period=0,
            fire_particle_generator=lightning_nozzle,
            projectile_generator=get_lightning_bolts(
                _START_COLOR,
                _END_COLOR,
                _DAMAGE,
                _DAMAGE_RANGE,
            ),
            ammo=2000,
            color=RGB(255, 190, 255, 1),
        )

    def _spend_ammo(self) -> None:
        self._ammo -= 1

    def _effect_on_player(self) -> None: ...

    def secondary_fire(self) -> None: ...


#################################################################


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
        )

    def _spend_ammo(self) -> None:
        self._ammo -= 1

    def _effect_on_player(self) -> None:
        # recoil!
        self._scenario.player.velocity = (
            self._scenario.player.velocity - (self._scenario.player.get_last_known_direction())
        ).as_vector()

    def secondary_fire(self) -> None: ...


#################################################################

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
        )

    def _spend_ammo(self) -> None:
        self._ammo -= 1

    def _effect_on_player(self) -> None:
        # recoil!
        self._scenario.player.velocity = (
            self._scenario.player.velocity - 3 * (self._scenario.player.get_last_known_direction())
        ).as_vector()

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
        if (
            not self._trigger_pressed
            and self._refractory_limit <= self._scenario.now()
            and self._ammo > 0
        ):
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
