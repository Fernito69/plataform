from typing import TYPE_CHECKING, Callable

from model.theme import RGB, Theme
from physics2d.shapes.factories.particle import lightning_bolts, ln2_vapor, meteor_trail, sonic_wave

if TYPE_CHECKING:
    from physics2d.scenario.scenario import Scenario
    from physics2d.shapes.circunference import Circunference


class Thruster:
    name: str
    scenario: "Scenario"
    particle_generator: Callable[["Scenario", "Circunference"], None]
    player_theme: Theme
    max_speed: float
    accel: float
    decel: float

    def __init__(
        self,
        scenario: "Scenario",
        name: str,
        particle_generator: Callable[["Scenario", "Circunference"], None],
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


class SoapyThruster(Thruster):
    """Looks like SOAP bubbles!"""

    def __init__(self, scenario: "Scenario"):
        super().__init__(
            scenario=scenario,
            particle_generator=ln2_vapor,
            name="SoapyThruster",
            player_theme=Theme(
                color=RGB(0, 0, 255),
            ),
            max_speed=5,
            accel=0.4,
            decel=0.2,
        )


class MeteorThruster(Thruster):
    """Looks like a meteor!"""

    def __init__(self, scenario: "Scenario"):
        super().__init__(
            scenario=scenario,
            particle_generator=meteor_trail,
            name="MeteorThruster",
            player_theme=Theme(
                color=RGB(255, 50, 50),
            ),
            max_speed=6,
            accel=1.3,
            decel=0.3,
        )


class SonicThruster(Thruster):
    """I dunno!"""

    def __init__(self, scenario: "Scenario"):
        super().__init__(
            scenario=scenario,
            particle_generator=sonic_wave,
            name="SonicThruster",
            player_theme=Theme(
                color=RGB(122, 23, 255),
            ),
            max_speed=7,
            accel=2,
            decel=1.5,
        )


class LightningThruster(Thruster):
    """I dunno!"""

    def __init__(self, scenario: "Scenario"):
        super().__init__(
            scenario=scenario,
            particle_generator=lightning_bolts,
            name="LightningThruster",
            player_theme=Theme(
                color=RGB(255, 255, 190),
            ),
            max_speed=8,
            accel=3,
            decel=1.5,
        )


Thrusters = MeteorThruster | SoapyThruster | SonicThruster | LightningThruster
