from typing import TYPE_CHECKING, Callable

if TYPE_CHECKING:
    from physics2d.entities.base import PhysicsEntity
    from physics2d.physics2d import Physics2D


type Spawner = Callable[["Physics2D", "PhysicsEntity"], None]
