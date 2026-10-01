from typing import TYPE_CHECKING

from factories.theme import Theme
from model.base import PointF
from model.theme import RGB
from physics2d.entities.enemy import Enemy
from physics2d.entities.model.shared import BackgroundGenerator
from physics2d.scenario.scenario import Scenario
from physics2d.shape.base import Shape

if TYPE_CHECKING:
    from physics2d.physics2d import Physics2D

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
            theme=Theme(RGB(255, 50, 50, opacity=0.3)),
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
            size=16,
            health=400,
            name="MidEnemy",
            position=PointF(132, 30),
            theme=Theme(RGB(255, 50, 50, opacity=0.6)),
        ),
        Enemy(
            engine=engine,
            size=24,
            health=400,
            name="MidEnemy",
            position=PointF(120, 30),
            theme=Theme(RGB(0, 0, 255, opacity=1)),
            secondary_theme=Theme(RGB(0, 255, 0, opacity=1)),
            color_cycling_factor=10,
        ),
        Enemy(
            engine=engine,
            size=16,
            health=400,
            name="MidEnemy",
            position=PointF(144, 30),
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
        ###
        Enemy(
            engine=engine,
            size=24,
            health=400,
            name="MidEnemy",
            position=PointF(100, 60),
            theme=Theme(RGB(255, 50, 50, opacity=1)),
            secondary_theme=Theme(RGB(127, 50, 255, opacity=1)),
            color_cycling_factor=10,
        ),
        Enemy(
            engine=engine,
            size=24,
            health=400,
            name="MidEnemy",
            position=PointF(110, 60),
            theme=Theme(
                RGB(50, 255, 50, opacity=1),
            ),
            secondary_theme=Theme(RGB(255, 127, 50, opacity=1)),
            color_cycling_factor=9,
        ),
        Enemy(
            engine=engine,
            size=24,
            health=400,
            name="MidEnemy",
            position=PointF(120, 60),
            theme=Theme(RGB(50, 50, 255, opacity=1)),
            secondary_theme=Theme(RGB(0, 127, 255, opacity=1)),
            color_cycling_factor=8,
        ),
        ############################################################
        Enemy(
            engine=engine,
            size=18,
            health=400,
            name="MidEnemy",
            position=PointF(100, -34),
            theme=Theme(RGB(255, 50, 50, opacity=0.1)),
        ),
        Enemy(
            engine=engine,
            size=18,
            health=400,
            name="MidEnemy",
            position=PointF(110, -32),
            theme=Theme(
                RGB(50, 255, 50, opacity=1),
            ),
        ),
        Enemy(
            engine=engine,
            size=18,
            health=400,
            name="MidEnemy",
            position=PointF(120, -30),
            theme=Theme(RGB(50, 50, 255, opacity=0)),
        ),
        Enemy(
            engine=engine,
            size=18,
            health=400,
            name="MidEnemy",
            position=PointF(100, -64),
            theme=Theme(RGB(50, 50, 255, opacity=0.1)),
        ),
        Enemy(
            engine=engine,
            size=18,
            health=400,
            name="MidEnemy",
            position=PointF(110, -62),
            theme=Theme(
                RGB(255, 50, 50, opacity=1),
            ),
        ),
        Enemy(
            engine=engine,
            size=18,
            health=400,
            name="MidEnemy",
            position=PointF(120, -60),
            theme=Theme(RGB(50, 255, 0, opacity=0)),
        ),
        Enemy(
            engine=engine,
            size=18,
            health=400,
            name="MidEnemy",
            position=PointF(100, -94),
            theme=Theme(RGB(50, 255, 50, opacity=0.1)),
        ),
        Enemy(
            engine=engine,
            size=18,
            health=400,
            name="MidEnemy",
            position=PointF(110, -92),
            theme=Theme(
                RGB(50, 50, 255, opacity=1),
            ),
        ),
        Enemy(
            engine=engine,
            size=18,
            health=400,
            name="MidEnemy",
            position=PointF(120, -90),
            theme=Theme(RGB(255, 50, 50, opacity=0)),
        ),
    ]

    fg_pieces: list[Shape] = []
    solid_pieces: list[Shape] = []
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
