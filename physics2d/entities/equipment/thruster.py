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

    """Full fuel = 1 = 100%"""
    fuel: float = 1
    _fuel_usage_factor: float

    def __init__(
        self,
        engine: "Physics2D",
        name: str,
        particle_generator: ParticleGenerator,
        player_theme: Theme,
        max_speed: float,
        accel: float,
        decel: float,
        fuel_usage_factor: float,
    ):
        self._engine = engine
        self.name = name
        self.particle_generator = particle_generator
        self.player_theme = player_theme
        self.max_speed = max_speed
        self.accel = accel
        self.decel = decel
        self._fuel_usage_factor = fuel_usage_factor

    def has_fuel(self) -> bool:
        return self.fuel > 0

    def do_your_thing(self) -> None:
        if self.has_fuel():
            self.particle_generator(self._engine, self._engine.scenario.player)

        player_vel = self._engine.player.velocity
        if (player_vel.x or player_vel.y) and self.has_fuel():
            self._spend_fuel()

    def _spend_fuel(self) -> None:
        self.fuel = max(0, self.fuel - self._fuel_usage_factor)
