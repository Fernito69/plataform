from typing import TYPE_CHECKING

from model.theme import Theme
from physics2d.entities.model.shared import ParticleGenerator

if TYPE_CHECKING:
    from physics2d.scenario.scenario import Scenario


class Thruster:
    name: str
    scenario: "Scenario"
    particle_generator: ParticleGenerator
    player_theme: Theme
    max_speed: float
    accel: float
    decel: float

    def __init__(
        self,
        scenario: "Scenario",
        name: str,
        particle_generator: ParticleGenerator,
        player_theme: Theme,
        max_speed: float,
        accel: float,
        decel: float,
    ):
        self.scenario = scenario
        self.name = name
        self.particle_generator = particle_generator
        self.player_theme = player_theme
        self.max_speed = max_speed
        self.accel = accel
        self.decel = decel

    def handle_particles(self) -> None:
        self.particle_generator(self.scenario, self.scenario.player)


#################################################################


#################################################################


#################################################################


#################################################################


#################################################################
