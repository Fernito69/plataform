from typing import TYPE_CHECKING, Callable

if TYPE_CHECKING:
    from physics2d.scenario.scenario import Scenario
    from physics2d.shapes.circunference import Circunference

# TODO: this doesn't belong here and shouldn't be circunference
type ParticleGenerator = Callable[[Scenario, Circunference], None]
