from typing import TYPE_CHECKING, Callable

if TYPE_CHECKING:
    from physics2d.entities.base import PhysicsEntity
    from physics2d.entities.enemy import Enemy
    from physics2d.entities.equipment.projectile import Projectile
    from physics2d.entities.three_dee_enemy import ThreeDeeEnemy
    from physics2d.physics2d import Physics2D
    from physics2d.shape.base import Shape


type ParticleGenerator = Callable[[Physics2D, PhysicsEntity], None]
type ParticleGeneratorWithTarget = Callable[[Physics2D, PhysicsEntity, PhysicsEntity | None], None]
type RenderableEntity = "Shape | Projectile | Enemy | ThreeDeeEnemy | PhysicsEntity"
