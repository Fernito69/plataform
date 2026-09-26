from random import random
from typing import TYPE_CHECKING

from factories.theme import Theme
from model.base import PointF
from model.theme import RGB
from physics2d.entities.enemy import Enemy
from physics2d.scenario.scenario import Scenario
from physics2d.shape.base import Shape

if TYPE_CHECKING:
    from physics2d.physics2d import Physics2D


def _random_color():
    floor = 80

    def _val() -> float:
        return floor + (255 - floor) * random()

    return RGB(_val(), _val(), _val())


def first_level(engine: "Physics2D") -> Scenario:
    enemies: list[Enemy] = [
        Enemy(
            engine=engine,
            size=24,
            health=400,
            name="MidEnemy",
            position=PointF(100, 0),
            theme=Theme(RGB(255, 50, 50, opacity=0.6)),
        ),
        Enemy(
            engine=engine,
            size=24,
            health=400,
            name="MidEnemy",
            position=PointF(110, 0),
            theme=Theme(
                RGB(50, 255, 50, opacity=0.5),
            ),
        ),
        Enemy(
            engine=engine,
            size=24,
            health=400,
            name="MidEnemy",
            position=PointF(120, 0),
            theme=Theme(RGB(50, 50, 255, opacity=1)),
        ),
        ###
        Enemy(
            engine=engine,
            size=12,
            health=400,
            name="MidEnemy",
            position=PointF(120, 30),
            theme=Theme(RGB(255, 50, 50, opacity=0.6)),
        ),
        Enemy(
            engine=engine,
            size=24,
            health=400,
            name="MidEnemy",
            position=PointF(120, 30),
            theme=Theme(RGB(0, 0, 255, opacity=1)),
        ),
        Enemy(
            engine=engine,
            size=12,
            health=400,
            name="MidEnemy",
            position=PointF(140, 30),
            theme=Theme(
                RGB(50, 255, 50, opacity=0.5),
            ),
        ),
        Enemy(
            engine=engine,
            size=12,
            health=400,
            name="MidEnemy",
            position=PointF(160, 30),
            theme=Theme(RGB(50, 50, 255, opacity=0.6)),
        ),
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
        # SpawnerEntity(
        #     engine=engine,
        #     size=10,
        #     spawn_interval=200,
        #     total_num_spawns=5,
        #     position=PointF(75, 75),
        #     spawner=super_rocket_enemy_spawner,
        #     initial_delay=150,
        # ),
        # SpawnerEntity(
        #     engine=engine,
        #     size=10,
        #     spawn_interval=80,
        #     total_num_spawns=5,
        #     position=PointF(100, 100),
        #     spawner=machine_gun_enemy_spawner,
        # ),
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
