from typing import TYPE_CHECKING, Callable

if TYPE_CHECKING:
    from physics2d.entities.base import PhysicsEntity
    from physics2d.scenario.scenario import Scenario

# TODO: this doesn't belong here
type ParticleGenerator = Callable[[Scenario, PhysicsEntity], None]
