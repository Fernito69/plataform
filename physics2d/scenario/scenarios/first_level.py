from typing import TYPE_CHECKING

from model.base import PointF
from model.theme import BR, RGB, Theme
from physics2d.entities.enemy import Enemy

# from physics2d.entities.spawner_entity import SpawnerEntity
from physics2d.entities.spawners.enemy import machine_gun_enemy_spawner, super_rocket_enemy_spawner
from physics2d.entities.spawners.item import (
    health_spawner,
    rocket_launcher_pickup_spawner,
    shotgun_pickup_spawner,
)
from physics2d.entities.spawners.text import wave_started_text
from physics2d.model.shared import BackgroundGenerator

# from physics2d.pickable.health import HealthPickup
# from physics2d.pickable.weapon import (
#     BFGPickup,
#     HeavyMachineGunPickup,
#     HeavyRocketLauncherPickup,
#     HomingMissilesLauncherPickup,
#     LightningGunPickup,
#     MicroMissilesLauncherPickup,
#     RocketLauncherPickup,
#     ShotgunPickup,
#     ZapperPickup,
# )
from physics2d.scenario.model import Event, Milestone
from physics2d.scenario.scenario import Scenario
from physics2d.shape.base import Shape
from physics2d.shape.line import Line

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
        # SpawnerEntity(
        #     engine=engine,
        #     spawn_interval=200,
        #     total_num_spawns=2,
        #     position=PointF(75, 75),
        #     spawner=super_rocket_enemy_spawner,
        #     initial_delay=150,
        #     spawn_effect_size=15,
        # ),
        # SpawnerEntity(
        #     engine=engine,
        #     spawn_interval=80,
        #     total_num_spawns=5,
        #     spawn_effect_size=10,
        #     position=PointF(100, 100),
        #     spawner=machine_gun_enemy_spawner,
        # ),
    ]

    solid_pieces: list[Shape] = [
        Line(
            points=points,
            theme=Theme(color=RGB(255, 255, 255)),
            thickness=3,
            engine=engine,
        )
        for points in [
            (PointF(-100, 100), PointF(100, 100)),
            (PointF(100, 100), PointF(100, -100)),
            (PointF(100, -100), PointF(-100, -100)),
            (PointF(-100, -100), PointF(-100, 100)),
        ]
    ]

    pickables: list["Pickable"] = [
        # ShotgunPickup(engine=engine, position=PointF(0, -20)),
        # RocketLauncherPickup(engine=engine, position=PointF(40, -20)),
        # MicroMissilesLauncherPickup(engine=engine, position=PointF(80, -20)),
        # HomingMissilesLauncherPickup(engine=engine, position=PointF(120, -20)),
        # HeavyRocketLauncherPickup(engine=engine, position=PointF(160, -20)),
        # LightningGunPickup(engine=engine, position=PointF(200, -20)),
        # HeavyMachineGunPickup(engine=engine, position=PointF(240, -20)),
        # ZapperPickup(engine=engine, position=PointF(280, -20)),
        # BFGPickup(engine=engine, position=PointF(300, -20)),
        # ###
        # HealthPickup(engine=engine, position=PointF(90, 20), amount=100),
        # HealthPickup(engine=engine, position=PointF(130, 20), amount=200),
        # HealthPickup(engine=engine, position=PointF(170, 20), amount=500),
        # HealthPickup(engine=engine, position=PointF(210, 20), amount=1000),
    ]

    timeline: list[Milestone] = [
        ##### WAVE 1 #####
        Milestone(
            game_tick=1,
            events=[
                Event(
                    spawner=wave_started_text("WAVE 1"),
                    positions=[PointF(0, 50)],
                ),
                Event(
                    spawner=shotgun_pickup_spawner,
                    positions=[PointF(25, 0)],
                ),
            ],
        ),
        Milestone(
            game_tick=20,
            events=[
                Event(
                    spawner=wave_started_text(
                        "Prepare URANUS for battle!",
                        subtitle=True,
                    ),
                    positions=[PointF(0, 30)],
                ),
            ],
        ),
        *[
            Milestone(
                game_tick=100 + idx * 5,
                events=[
                    Event(
                        spawner=machine_gun_enemy_spawner,
                        positions=[position],
                    ),
                ],
            )
            for idx, position in enumerate(
                [
                    PointF(50, 50),
                    PointF(50, 0),
                    PointF(50, -50),
                    PointF(-50, -50),
                    PointF(-50, 0),
                    PointF(-50, 50),
                ]
            )
        ],
        ##### WAVE 2 #####
        Milestone(
            game_tick=450,
            events=[
                Event(
                    spawner=wave_started_text(f"WAVE 2{BR}Boss ahead!"),
                    positions=[PointF(0, 50)],
                ),
                Event(
                    spawner=rocket_launcher_pickup_spawner,
                    positions=[PointF(-25, 25)],
                ),
                Event(
                    spawner=health_spawner(500),
                    positions=[PointF(0, -25)],
                ),
            ],
        ),
        Milestone(
            game_tick=600,
            events=[
                Event(
                    spawner=super_rocket_enemy_spawner,
                    positions=[
                        PointF(50, 0),
                        PointF(-50, 0),
                    ],
                ),
            ],
        ),
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
        timeline=timeline,
    )
