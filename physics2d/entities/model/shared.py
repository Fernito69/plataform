from typing import TYPE_CHECKING, Callable

if TYPE_CHECKING:
    from physics2d.entities.base import PhysicsEntity
    from physics2d.scenario.scenario import Scenario

type ParticleGenerator = Callable[[Scenario, PhysicsEntity], None]
type ParticleGeneratorWithTarget = Callable[[Scenario, PhysicsEntity, PhysicsEntity | None], None]
