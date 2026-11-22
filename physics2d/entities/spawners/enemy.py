from typing import TYPE_CHECKING

from model.base import PointF
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
        spawner_on_death=health_spawner(amount=250),
    )
    teleport_in_particles(engine, position)
    engine.scenario.enemies.append(enemy)
    # TODO: this is just a hardcoded test for now
    engine.scenario.set_objective(enemy)


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


"""
Originally it meant to me the labyrinth in which I felt trapped, but wanted to resignify it as the labyrinth of life. Why black? Because that's life! Sometimes it might appear as if you were in a dead end from certain angle, until at some point something happens and new ways open (and also because that was part of the challenge withe the Misou black xd) which unexpectedly lead you to meeting amazing people like you. Thanks for existing!
"""
