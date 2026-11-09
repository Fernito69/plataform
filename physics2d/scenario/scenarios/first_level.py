from typing import TYPE_CHECKING

from model.base import PointF
from physics2d.entities.enemy import Enemy
from physics2d.entities.spawner_entity import SpawnerEntity
from physics2d.entities.spawners.enemy import machine_gun_enemy_spawner, super_rocket_enemy_spawner
from physics2d.model.shared import BackgroundGenerator
from physics2d.pickable.health import HealthPickup
from physics2d.pickable.weapon import (
    BFGPickup,
    HeavyMachineGunPickup,
    HeavyRocketLauncherPickup,
    HomingMissilesLauncherPickup,
    LightningGunPickup,
    MicroMissilesLauncherPickup,
    RocketLauncherPickup,
    ShotgunPickup,
    ZapperPickup,
)
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
        ShotgunPickup(engine=engine, position=PointF(100, -20)),
        RocketLauncherPickup(engine=engine, position=PointF(120, -20)),
        MicroMissilesLauncherPickup(engine=engine, position=PointF(160, -20)),
        HomingMissilesLauncherPickup(engine=engine, position=PointF(180, -20)),
        HeavyRocketLauncherPickup(engine=engine, position=PointF(140, -20)),
        LightningGunPickup(engine=engine, position=PointF(80, -20)),
        HeavyMachineGunPickup(engine=engine, position=PointF(60, -20)),
        ZapperPickup(engine=engine, position=PointF(40, -20)),
        BFGPickup(engine=engine, position=PointF(20, -20)),
        ###
        HealthPickup(engine=engine, position=PointF(140, 20), amount=100),
        HealthPickup(engine=engine, position=PointF(160, 20), amount=200),
        HealthPickup(engine=engine, position=PointF(180, 20), amount=500),
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
