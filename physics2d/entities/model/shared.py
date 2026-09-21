from typing import TYPE_CHECKING, Callable

if TYPE_CHECKING:
    from physics2d.entities.base import PhysicsEntity
    from physics2d.physics2d import Physics2D
    from physics2d.scenario.scenario import Scenario

type ParticleGenerator = Callable[[Physics2D, PhysicsEntity], None]
type ParticleGeneratorWithTarget = Callable[[Physics2D, PhysicsEntity, PhysicsEntity | None], None]

type ScenarioGenerator = Callable[["Physics2D"], "Scenario"]
