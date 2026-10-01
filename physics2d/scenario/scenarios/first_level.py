from typing import TYPE_CHECKING

from model.base import PointF
from physics2d.entities.enemy import Enemy
from physics2d.entities.model.shared import BackgroundGenerator
from physics2d.entities.spawner_entity import SpawnerEntity
from physics2d.entities.spawners.enemy import machine_gun_enemy_spawner, super_rocket_enemy_spawner
from physics2d.scenario.scenario import Scenario
from physics2d.shape.base import Shape

if TYPE_CHECKING:
    from physics2d.physics2d import Physics2D

_STARTING_POSITION = PointF(0, 0)


def first_level(
    engine: "Physics2D",
    background_gen: BackgroundGenerator,
) -> Scenario:
    enemies: list[Enemy] = []

    fg_pieces: list[Shape] = []

    # TODO: we are adding it to solid pieces, but maybe SpawnerEntity should be Enemy
    solid_pieces: list[Shape] = [
        SpawnerEntity(
            engine=engine,
            spawn_interval=200,
            total_num_spawns=2,
            position=PointF(75, 75),
            spawner=super_rocket_enemy_spawner,
            initial_delay=150,
        ),
        SpawnerEntity(
            engine=engine,
            spawn_interval=80,
            total_num_spawns=5,
            position=PointF(100, 100),
            spawner=machine_gun_enemy_spawner,
        ),
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
        background_gen=background_gen,
        player_initial_position=_STARTING_POSITION,
    )
