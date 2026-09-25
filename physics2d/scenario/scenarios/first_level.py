from typing import TYPE_CHECKING

from factories.theme import Theme
from model.base import PointF
from model.theme import RGB
from physics2d.entities.enemies.stalking_enemies.machinegun_enemy import MachineGunEnemy
from physics2d.entities.enemies.stalking_enemies.rocket_enemy import RocketEnemy
from physics2d.entities.enemies.stalking_enemies.super_rocket_enemy import SuperRocketEnemy
from physics2d.entities.enemy import Enemy
from physics2d.entities.model.spawner import Spawner
from physics2d.entities.spawner_entity import SpawnerEntity
from physics2d.entities.spawners.enemy import super_rocket_enemy_spawner
from physics2d.scenario.scenario import Scenario
from physics2d.shape.base import Shape

if TYPE_CHECKING:
    from physics2d.physics2d import Physics2D


def first_level(engine: "Physics2D") -> Scenario:
    enemies: list[Enemy] = [
        # MachineGunEnemy(
        #     size=10,
        #     health=100,
        #     position=PointF(50, 50),
        #     theme=Theme(color=RGB(255, 0, 0)),
        #     engine=engine,
        # ),
        # MachineGunEnemy(
        #     size=10,
        #     health=100,
        #     position=PointF(150, 150),
        #     theme=Theme(color=RGB(255, 250, 0)),
        #     engine=engine,
        # ),
        # MachineGunEnemy(
        #     size=10,sawds
        #     health=100,
        #     position=PointF(150, 200),
        #     theme=Theme(color=RGB(255, 0, 255)),
        #     engine=engine,
        # ),
        # MachineGunEnemy(
        #     size=30,
        #     health=1000,
        #     position=PointF(300, 300),dsaw
        #     engine=engine,
        #     aggressivity=0.1,
        #     max_velocity=1,
        # ),
        # SuperRocketEnemy(
        #     size=15,
        #     health=1000,
        #     position=PointF(50, 50),
        #     theme=Theme(color=RGB(120, 120, 120)),
        #     engine=engine,
        # ),
    ]

    fg_pieces: list[Shape] = []

    # TODO: we are adding it to solid pieces, but maybe it needs its own layer
    solid_pieces: list[Shape] = [
        SpawnerEntity(
            engine=engine,
            size=10,
            spawn_interval=100,
            total_num_spawns=5,
            position=PointF(75, 75),
            spawner=super_rocket_enemy_spawner,
        )
    ]

    bg_pieces: list[Shape] = []

    return Scenario(
        name="First level",
        enemies=enemies,
        three_dee_enemies=[],
        fg_shapes=fg_pieces,
        bg_shapes=bg_pieces,
        solid_shapes=solid_pieces,
        engine=engine,
        player=engine.player,
    )
