from abc import abstractmethod
from typing import TYPE_CHECKING

from model.theme import RGB
from physics2d.entities.model.shared import ParticleGenerator

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
        if not self.can_shoot() or (
            self._scenario.player.get_last_known_direction().x == 0
            and self._scenario.player.get_last_known_direction().y == 0
        ):
            return

        self._fire_particle_generator(self._scenario, self._scenario.player)
        self._projectile_generator(self._scenario, self._scenario.player)

        self._spend_ammo()
        self._effect_on_player()

        self._refractory_limit = self._scenario.now() + self._refractory_period

    def can_shoot(self) -> bool:
        # TODO: self._ammo should be >= the amount of ammo per shot
        return self._refractory_limit <= self._scenario.now() and self._ammo > 0

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
