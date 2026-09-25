from typing import TYPE_CHECKING

from model.base import VectorF
from model.theme import RGB, Theme
from physics2d.entities.base import PhysicsEntity
from physics2d.entities.enemies.stalking_enemies.super_rocket_enemy import SuperRocketEnemy

if TYPE_CHECKING:
    from physics2d.physics2d import Physics2D


def super_rocket_enemy_spawner(
    engine: "Physics2D",
    source: PhysicsEntity,
    _: VectorF | None = None,
) -> None:
    enemy = SuperRocketEnemy(
        size=15,
        health=1000,
        position=source.position,
        theme=Theme(color=RGB(120, 120, 120)),
        engine=engine,
    )
    engine.scenario.enemies.append(enemy)
