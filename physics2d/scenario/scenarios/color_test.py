from typing import TYPE_CHECKING

from factories.theme import Theme
from model.base import PointF
from model.theme import RGB
from physics2d.entities.enemy import Enemy
from physics2d.model.shared import BackgroundGenerator
from physics2d.pickable.health import HealthPickup
from physics2d.pickable.weapon import (
    HeavyRocketLauncherPickup,
    HomingMissilesLauncherPickup,
    MicroMissilesLauncherPickup,
    RocketLauncherPickup,
    ShotgunPickup,
)
from physics2d.scenario.scenario import Scenario
from physics2d.shape.base import Shape
from physics2d.shape.bitmap import Bitmap

if TYPE_CHECKING:
    from physics2d.physics2d import Physics2D
    from physics2d.pickable.base import Pickable

_STARTING_POSITION = PointF(0, 0)


def color_test(
    engine: "Physics2D",
    background_gen: BackgroundGenerator,
) -> Scenario:
    enemies: list[Enemy] = [
        Enemy(
            engine=engine,
            size=24,
            health=400,
            name="MidEnemy",
            position=PointF(100, 0),
            theme=Theme(RGB(255, 50, 50)),
            secondary_theme=Theme(RGB(0, 255, 0)),
            # color_gradient_exponent=0.1,
            x_stretching_factor=0.2,
            y_stretching_factor=1,
            final_x_stretching_factor=1,
            x_elliptical_oscillation_frequency=1,
            initial_angular_velocity=0.01,
        ),
        # Enemy(
        #     engine=engine,
        #     size=24,
        #     health=400,
        #     name="MidEnemy",
        #     position=PointF(110, 0),
        #     theme=Theme(
        #         RGB(50, 255, 50, opacity=0.5),
        #     ),
        # ),
        Enemy(
            engine=engine,
            size=36,
            health=400,
            name="MidEnemy",
            position=PointF(180, 0),
            theme=Theme(RGB(50, 50, 255, opacity=1)),
            secondary_theme=Theme(RGB(60, 0, 50, opacity=0.1)),
            x_stretching_factor=1.7,
            initial_angular_velocity=0.005,
        ),
        ###
        # Enemy(
        #     engine=engine,
        #     size=16,
        #     health=400,
        #     name="MidEnemy",
        #     position=PointF(132, 30),
        #     theme=Theme(RGB(255, 50, 50, opacity=0.6)),
        # ),
        # Enemy(
        #     engine=engine,
        #     size=24,
        #     health=400,
        #     name="MidEnemy",
        #     position=PointF(120, 30),
        #     theme=Theme(RGB(0, 0, 255, opacity=1)),
        #     secondary_theme=Theme(RGB(0, 255, 0, opacity=1)),
        #     color_cycling_factor=10,
        # ),
        # Enemy(
        #     engine=engine,
        #     size=16,
        #     health=400,
        #     name="MidEnemy",
        #     position=PointF(144, 30),
        #     theme=Theme(
        #         RGB(50, 255, 50, opacity=0.5),
        #     ),
        # ),
        # Enemy(
        #     engine=engine,
        #     size=12,
        #     health=400,
        #     name="MidEnemy",
        #     position=PointF(160, 30),
        #     theme=Theme(RGB(50, 50, 255, opacity=0.6)),
        # ),
        # ###
        # Enemy(
        #     engine=engine,
        #     size=24,
        #     health=400,
        #     name="MidEnemy",
        #     position=PointF(100, 60),
        #     theme=Theme(RGB(255, 50, 50, opacity=1)),
        #     secondary_theme=Theme(RGB(127, 50, 255, opacity=1)),
        #     color_cycling_factor=10,
        # ),
        # Enemy(
        #     engine=engine,
        #     size=24,
        #     health=400,
        #     name="MidEnemy",
        #     position=PointF(110, 60),
        #     theme=Theme(
        #         RGB(50, 255, 50, opacity=1),
        #     ),
        #     secondary_theme=Theme(RGB(255, 127, 50, opacity=1)),
        #     color_cycling_factor=9,
        # ),
        # Enemy(
        #     engine=engine,
        #     size=24,
        #     health=400,
        #     name="MidEnemy",
        #     position=PointF(120, 60),
        #     theme=Theme(RGB(50, 50, 255, opacity=1)),
        #     secondary_theme=Theme(RGB(0, 127, 255, opacity=1)),
        #     color_cycling_factor=8,
        # ),
        # ############################################################
        # Enemy(
        #     engine=engine,
        #     size=18,
        #     health=400,
        #     name="MidEnemy",
        #     position=PointF(100, -34),
        #     theme=Theme(RGB(255, 50, 50, opacity=0.1)),
        # ),
        # Enemy(
        #     engine=engine,
        #     size=18,
        #     health=400,
        #     name="MidEnemy",
        #     position=PointF(110, -32),
        #     theme=Theme(
        #         RGB(50, 255, 50, opacity=1),
        #     ),
        # ),
        # Enemy(
        #     engine=engine,
        #     size=18,
        #     health=400,
        #     name="MidEnemy",
        #     position=PointF(120, -30),
        #     theme=Theme(RGB(50, 50, 255, opacity=0)),
        # ),
        # Enemy(
        #     engine=engine,
        #     size=18,
        #     health=400,
        #     name="MidEnemy",
        #     position=PointF(100, -64),
        #     theme=Theme(RGB(50, 50, 255, opacity=0.1)),
        # ),
        # Enemy(
        #     engine=engine,
        #     size=18,
        #     health=400,
        #     name="MidEnemy",
        #     position=PointF(110, -62),
        #     theme=Theme(
        #         RGB(255, 50, 50, opacity=1),
        #     ),
        # ),
        # Enemy(
        #     engine=engine,
        #     size=18,
        #     health=400,
        #     name="MidEnemy",
        #     position=PointF(120, -60),
        #     theme=Theme(RGB(50, 255, 0, opacity=0)),
        # ),
        # Enemy(
        #     engine=engine,
        #     size=18,
        #     health=400,
        #     name="MidEnemy",
        #     position=PointF(100, -94),
        #     theme=Theme(RGB(50, 255, 50, opacity=0.1)),
        # ),
        # Enemy(
        #     engine=engine,
        #     size=18,
        #     health=400,
        #     name="MidEnemy",
        #     position=PointF(110, -92),
        #     theme=Theme(
        #         RGB(50, 50, 255, opacity=1),
        #     ),
        # ),
        # Enemy(
        #     engine=engine,
        #     size=18,
        #     health=400,
        #     name="MidEnemy",
        #     position=PointF(120, -90),
        #     theme=Theme(RGB(255, 50, 50, opacity=0)),
        # ),
    ]

    fg_pieces: list[Shape] = []
    solid_pieces: list[Shape] = []
    bg_pieces: list[Shape] = [
        Bitmap(
            engine=engine,
            origin=PointF(-20, -20),
            bitmap=_bitmap,
            initial_velocity=PointF(0.01, 0.02).as_vector(),
        )
    ]
    pickables: list["Pickable"] = [
        ShotgunPickup(engine=engine, position=PointF(100, 120)),
        RocketLauncherPickup(engine=engine, position=PointF(140, 60)),
        MicroMissilesLauncherPickup(engine=engine, position=PointF(160, 100)),
        HomingMissilesLauncherPickup(engine=engine, position=PointF(180, 100)),
        HeavyRocketLauncherPickup(engine=engine, position=PointF(140, 100)),
        HealthPickup(engine=engine, position=PointF(140, 80), amount=100),
        HealthPickup(engine=engine, position=PointF(160, 80), amount=200),
        HealthPickup(engine=engine, position=PointF(180, 80), amount=500),
    ]

    return Scenario(
        name="First level",
        enemies=enemies,
        three_dee_enemies=[],
        fg_shapes=fg_pieces,
        bg_shapes=bg_pieces,
        solid_shapes=solid_pieces,
        pickables=pickables,
        engine=engine,
        player=engine.player,
        background_gen=background_gen,
        player_initial_position=_STARTING_POSITION,
    )


r = RGB(255, 0, 0)
R = RGB(127, 0, 0)
y = RGB(255, 255, 0)
Y = RGB(127, 127, 0)
b = RGB(0, 0, 255)
B = RGB(0, 0, 127)
g = RGB(0, 255, 0)
G = RGB(0, 127, 0)


_bitmap: list[list[RGB | None]] = [
    [R, R, R, Y, Y, Y],
    [R, R, R, Y, Y, Y],
    [R, R, R, Y, Y, Y],
    [G, G, G, B, B, B],
    [G, G, G, B, B, B],
    [G, G, G, B, B, B],
]

# _bitmap: list[list[RGB]] = [
#     [R, R, R, R, Y, Y, Y],
#     [R, r, r, r, Y, y, y],
#     [R, r, r, r, Y, y, y],
# ]
