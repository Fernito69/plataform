from typing import TYPE_CHECKING

from model.base import PointF
from physics2d.entities.enemy import Enemy
from physics2d.entities.spawner_entity import SpawnerEntity
from physics2d.entities.spawners.enemy import machine_gun_enemy_spawner, super_rocket_enemy_spawner
from physics2d.model.shared import BackgroundGenerator
from physics2d.pickable.health import HealthPickup
from physics2d.scenario.scenario import Scenario
from physics2d.shape.base import Shape

if TYPE_CHECKING:
    from physics2d.physics2d import Physics2D
    from physics2d.pickable.base import Pickable


_STARTING_POSITION = PointF(0, 0)


def first_level(
    engine: "Physics2D",
    background_gen: BackgroundGenerator,
) -> Scenario:
    enemies: list[Enemy] = []

    fg_pieces: list[Shape] = []

    # TODO: we are adding it as shapes, but maybe SpawnerEntity should be Enemy
    bg_pieces: list[Shape] = [
        SpawnerEntity(
            engine=engine,
            spawn_interval=200,
            total_num_spawns=2,
            position=PointF(75, 75),
            spawner=super_rocket_enemy_spawner,
            initial_delay=150,
            spawn_effect_size=15,
        ),
        SpawnerEntity(
            engine=engine,
            spawn_interval=80,
            total_num_spawns=5,
            spawn_effect_size=10,
            position=PointF(100, 100),
            spawner=machine_gun_enemy_spawner,
        ),
    ]

    solid_pieces: list[Shape] = []
    pickables: list["Pickable"] = [
        HealthPickup(engine=engine, position=PointF(180, 80), amount=500),
    ]

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
        pickables=pickables,
    )
