from abc import abstractmethod
from typing import TYPE_CHECKING

from physics2d.entities.equipment.model.shared import ParticleGenerator
from physics2d.shapes.factories.nozzle import machine_gun
from physics2d.shapes.factories.projectile import bullet

if TYPE_CHECKING:
    from physics2d.scenario.scenario import Scenario


class Weapon:
    name: str
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
        max_ammo: int,
        fire_particle_generator: ParticleGenerator,
        projectile_generator: ParticleGenerator,
        refractory_period: int,
        ammo: int = 0,
    ):
        self._scenario = scenario
        self.name = name
        self._fire_particle_generator = fire_particle_generator
        self._projectile_generator = projectile_generator
        self._max_ammo = max_ammo
        self._refractory_period = refractory_period
        self._ammo = min(ammo, max_ammo)
        self._refractory_limit = scenario.now()

    def fire(self) -> None:
        if self._ammo <= 0 or self._refractory_limit > self._scenario.now():
            return

        self._fire_particle_generator(self._scenario, self._scenario.player)
        self._projectile_generator(self._scenario, self._scenario.player)

        self._spend_ammo()
        self._effect_on_player()

        self._refractory_limit = self._scenario.now() + self._refractory_period

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
            fire_particle_generator=machine_gun,
            projectile_generator=bullet,
            ammo=1000,
        )

    def _spend_ammo(self) -> None:
        self._ammo -= 1

    def secondary_fire(self) -> None:
        ...
        # TODO: todo stuff and bind the key
