from typing import TYPE_CHECKING, Callable

from physics2d.shapes.factories.particle import ln2_vapor, meteor_trail, sonic_wave

if TYPE_CHECKING:
    from physics2d.scenario.scenario import Scenario
    from physics2d.shapes.circunference import Circunference


class Thruster:
    name: str
    scenario: "Scenario"
    particle_generator: Callable[["Scenario", "Circunference"], None]

    def __init__(
        self,
        scenario: "Scenario",
        name: str,
        particle_generator: Callable[["Scenario", "Circunference"], None],
    ):
        self.scenario = scenario
        self.name = name
        self.particle_generator = particle_generator

    def handle_particles(self) -> None:
        self.particle_generator(self.scenario, self.scenario.player)


class IcyThruster(Thruster):
    """Looks like LN2 vapor!"""

    def __init__(self, scenario: "Scenario"):
        super().__init__(
            scenario=scenario,
            particle_generator=ln2_vapor,
            name="IcyThruster",
        )


class MeteorThruster(Thruster):
    """Looks like a meteor!"""

    def __init__(self, scenario: "Scenario"):
        super().__init__(
            scenario=scenario,
            particle_generator=meteor_trail,
            name="MeteorThruster",
        )


class SonicThruster(Thruster):
    """I dunno!"""

    def __init__(self, scenario: "Scenario"):
        super().__init__(
            scenario=scenario,
            particle_generator=sonic_wave,
            name="SonicThruster",
        )


Thrusters = MeteorThruster | IcyThruster
