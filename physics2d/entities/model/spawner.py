from dataclasses import dataclass
from typing import TYPE_CHECKING, Callable

if TYPE_CHECKING:
    from physics2d.entities.base import PhysicsEntity
    from physics2d.physics2d import Physics2D


@dataclass
class Spawn[T]:
    spawn_interval: int
    total_num_spawns: int | None
    entity_factory: Callable[["Physics2D", "PhysicsEntity"], None]
    curr_num_spawns: int = 0
