from abc import abstractmethod
from typing import TYPE_CHECKING

from model.theme import RGB
from physics2d.entities.equipment.model.shared import ParticleGenerator
from physics2d.shapes.factories.nozzle import lightning, machine_gun, shotgun
from physics2d.shapes.factories.projectile import buckshot, bullet, lightning_bolts

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
            fire_particle_generator=machine_gun,
            projectile_generator=bullet,
            ammo=1000,
            color=RGB(255, 200, 255, 1),
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
            fire_particle_generator=shotgun,
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
        super().__init__(
            name="LightningGun",
            scenario=scenario,
            max_ammo=2000,
            refractory_period=0,
            fire_particle_generator=lightning,
            projectile_generator=lightning_bolts,
            ammo=2000,
            color=RGB(220, 220, 255, 1),
        )

    def _spend_ammo(self) -> None:
        self._ammo -= 1

    def _effect_on_player(self) -> None: ...

    def secondary_fire(self) -> None: ...
