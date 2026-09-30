from typing import TYPE_CHECKING

from model.theme import RGB, Theme
from physics2d.entities.base import PhysicsEntity
from physics2d.entities.enemies.stalking_enemies.machinegun_enemy import MachineGunEnemy
from physics2d.entities.enemies.stalking_enemies.super_rocket_enemy import SuperRocketEnemy

if TYPE_CHECKING:
    from physics2d.physics2d import Physics2D


def super_rocket_enemy_spawner(
    engine: "Physics2D",
    source: PhysicsEntity,
) -> None:
    enemy = SuperRocketEnemy(
        size=15,
        position=source.position,
        theme=Theme(color=RGB(90, 90, 100)),
        engine=engine,
        color_gradient_exponent=0.1,
        color_gradient_exponent_end=0.5,
        color_gradient_exponent_cycling_factor=4,
        secondary_theme=Theme(color=RGB(255, 20, 255)),
    )
    engine.scenario.enemies.append(enemy)


def machine_gun_enemy_spawner(
    engine: "Physics2D",
    source: PhysicsEntity,
) -> None:
    enemy = MachineGunEnemy(
        size=10,
        health=150,
        position=source.position,
        theme=Theme(color=RGB(190, 90, 100)),
        secondary_theme=Theme(color=RGB(90, 0, 0)),
        engine=engine,
    )
    engine.scenario.enemies.append(enemy)
