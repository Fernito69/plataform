from typing import TYPE_CHECKING

from factories.theme import Theme
from model.base import PointF
from model.theme import RGB
from physics2d.entities.enemies.small_enemy import SmallEnemy
from physics2d.entities.enemy import Enemy
from physics2d.scenario.scenario import Scenario
from physics2d.shape.base import Shape

if TYPE_CHECKING:
    from physics2d.physics2d import Physics2D


def first_level(engine: "Physics2D") -> Scenario:
    enemies: list[Enemy] = [
        SmallEnemy(
            size=10,
            health=100,
            position=PointF(50, 50),
            theme=Theme(color=RGB(255, 0, 0)),
            engine=engine,
        ),
        SmallEnemy(
            size=10,
            health=100,
            position=PointF(150, 150),
            theme=Theme(color=RGB(255, 250, 0)),
            engine=engine,
        ),
        SmallEnemy(
            size=10,
            health=100,
            position=PointF(150, 200),
            theme=Theme(color=RGB(255, 0, 255)),
            engine=engine,
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
    )
