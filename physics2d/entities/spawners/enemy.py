from typing import TYPE_CHECKING

from model.base import PointF, VectorF
from model.theme import RGB, Theme
from physics2d.entities.base import PhysicsEntity
from physics2d.entities.enemies.stalking_enemies.machinegun_enemy import MachineGunEnemy
from physics2d.entities.enemies.stalking_enemies.super_rocket_enemy import SuperRocketEnemy
from physics2d.entities.spawners.item import health_spawner
from physics2d.entities.spawners.utils import get_position
from physics2d.shape.factories.effects import teleport_in_particles

if TYPE_CHECKING:
    from physics2d.physics2d import Physics2D


def super_rocket_enemy_spawner(
    engine: "Physics2D",
    source: PhysicsEntity | PointF,
) -> None:
    position = get_position(source)
    enemy = SuperRocketEnemy(
        size=15,
        position=position,
        theme=Theme(color=RGB(90, 90, 100)),
        engine=engine,
        color_gradient_exponent=0.1,
        color_gradient_exponent_end=0.5,
        color_gradient_exponent_cycling_factor=4,
        secondary_theme=Theme(color=RGB(255, 20, 255)),
        spawner_on_death=health_spawner(100, velocity=VectorF.random_offset_vector(2)),
    )
    teleport_in_particles(engine, position)
    engine.scenario.enemies.append(enemy)


def machine_gun_enemy_spawner(
    engine: "Physics2D",
    source: PhysicsEntity | PointF,
) -> None:
    position = get_position(source)
    enemy = MachineGunEnemy(
        size=10,
        health=150,
        position=position,
        theme=Theme(color=RGB(190, 90, 100)),
        secondary_theme=Theme(color=RGB(90, 0, 0)),
        engine=engine,
    )
    teleport_in_particles(engine, position)
    engine.scenario.enemies.append(enemy)
