from abc import abstractmethod
from typing import TYPE_CHECKING

from model.theme import RGB, Theme
from physics2d.entities.equipment.model.shared import ParticleGenerator
from physics2d.shapes.factories.particle import lightning_bolts, ln2_vapor, meteor_trail, sonic_wave
from physics2d.shapes.factories.projectile import bullet

if TYPE_CHECKING:
    from physics2d.scenario.scenario import Scenario


class Weapon:
    name: str
    scenario: "Scenario"
    fire_particle_generator: ParticleGenerator
    projectile_generator: ParticleGenerator
    refractory_period: int

    ammo: int
    max_ammo: int

    def __init__(
        self,
        scenario: "Scenario",
        name: str,
        max_ammo: int,
        fire_particle_generator: ParticleGenerator,
        projectile_generator: ParticleGenerator,
        refractory_period: int,
    ):
        self.scenario = scenario
        self.name = name
        self.fire_particle_generator = fire_particle_generator
        self.projectile_generator = projectile_generator
        self.max_ammo = max_ammo
        self.refractory_period = refractory_period
        self.ammo = 0

    def fire(self) -> None:
        self.fire_particle_generator(self.scenario, self.scenario.player)
        self.projectile_generator(self.scenario, self.scenario.player)


class MachineGun(Weapon):
    def __init__(
        self,
        scenario: "Scenario",
    ):
        super().__init__(
            name="MachineGun",
            scenario=scenario,
            max_ammo=1000,
            refractory_period=1,
            fire_particle_generator=meteor_trail,
            projectile_generator=bullet,
        )

