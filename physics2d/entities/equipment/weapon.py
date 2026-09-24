from abc import abstractmethod
from typing import TYPE_CHECKING

from model.theme import RGB
from physics2d.entities.model.shared import ParticleGenerator

if TYPE_CHECKING:
    from physics2d.physics2d import Physics2D


class Weapon:
    name: str
    color: RGB

    _original_color: RGB

    _engine: "Physics2D"
    _fire_particle_generator: ParticleGenerator
    _projectile_generator: ParticleGenerator

    # How long it has to wait until next shot
    _refractory_period: int
    _refractory_limit: int

    _ammo: int
    _max_ammo: int

    _recoil: float

    def __init__(
        self,
        engine: "Physics2D",
        name: str,
        color: RGB,
        max_ammo: int,
        fire_particle_generator: ParticleGenerator,
        projectile_generator: ParticleGenerator,
        refractory_period: int,
        ammo: int = 0,
        recoil: float = 0,
    ):
        self._engine = engine
        self.name = name
        self.color = color
        self._original_color = color
        self._fire_particle_generator = fire_particle_generator
        self._projectile_generator = projectile_generator
        self._max_ammo = max_ammo
        self._refractory_period = refractory_period
        self._ammo = min(ammo, max_ammo)
        self._refractory_limit = engine.scenario.now()
        self._recoil = recoil

    def fire(self) -> None:
        if not self.can_shoot():
            return

        self._fire_particle_generator(self._engine, self._engine.scenario.player)
        self._projectile_generator(self._engine, self._engine.scenario.player)

        self._spend_ammo()
        self._effect_on_player()

        self._refractory_limit = self._engine.scenario.now() + self._refractory_period

    def can_shoot(self) -> bool:
        # TODO: self._ammo should be >= the amount of ammo per shot
        return self._refractory_limit <= self._engine.scenario.now() and self._ammo > 0

    def do_your_thing(self) -> None:
        self._handle_color()

    def get_life_time_ellapsed_ratio(self) -> float:
        return (self._refractory_limit - self._engine.scenario.now()) / self._refractory_period

    def _handle_color(self) -> None:
        if not self.can_shoot():
            # charging up
            _factor = self.get_life_time_ellapsed_ratio()
            _target_color = self._original_color.with_intensity(0.7)
            self.color = self._original_color.with_intensity(0.2).with_intensity(
                _factor
            ) + _target_color.with_intensity(1 - _factor)
        else:
            self.color = self._original_color.with_intensity(1)

    @abstractmethod
    def secondary_fire(self) -> None:
        ...
        # TODO: implement _secondary_projectile_generator, etc

    @abstractmethod
    def _spend_ammo(self) -> None:
        ...
        """Spend an amount of ammo per shot"""

    def _effect_on_player(self) -> None:
        if self._recoil <= 0:
            return

        # recoil!
        self._engine.scenario.player.velocity = (
            self._engine.scenario.player.velocity
            - self._recoil * (self._engine.scenario.player.get_aiming_direction())
        ).as_vector()
