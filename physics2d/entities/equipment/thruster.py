from typing import TYPE_CHECKING

from model.theme import Theme
from physics2d.entities.model.shared import ParticleGenerator

if TYPE_CHECKING:
    from physics2d.physics2d import Physics2D


class Thruster:
    name: str
    _engine: "Physics2D"
    particle_generator: ParticleGenerator
    player_theme: Theme
    max_speed: float
    accel: float
    decel: float

    def __init__(
        self,
        engine: "Physics2D",
        name: str,
        particle_generator: ParticleGenerator,
        player_theme: Theme,
        max_speed: float,
        accel: float,
        decel: float,
    ):
        self._engine = engine
        self.name = name
        self.particle_generator = particle_generator
        self.player_theme = player_theme
        self.max_speed = max_speed
        self.accel = accel
        self.decel = decel

    def handle_particles(self) -> None:
        self.particle_generator(self._engine, self._engine.scenario.player)
