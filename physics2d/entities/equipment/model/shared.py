from typing import TYPE_CHECKING, Callable

if TYPE_CHECKING:
    from physics2d.scenario.scenario import Scenario
    from physics2d.shapes.circunference import Circunference

type ParticleGenerator = Callable[[Scenario, Circunference], None]
