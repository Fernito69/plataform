from random import random
from typing import TYPE_CHECKING

from factories.theme import Theme
from model.base import VectorF
from model.theme import RGB
from physics2d.entities.enemy import Enemy
from physics2d.scenario.scenario import Scenario
from physics2d.shape.base import Shape

if TYPE_CHECKING:
    from physics2d.physics2d import Physics2D


def first_level(engine: "Physics2D") -> Scenario:
    # TODO: make factories
    def _random_color():
        floor = 80

        def _val() -> float:
            return floor + (255 - floor) * random()

        return RGB(_val(), _val(), _val())

    def _tiny_enemy(
        position,
        velocity=VectorF(0, 0),
        theme: Theme = Theme(color=_random_color(), bg_color=_random_color()),
    ):
        return Enemy(
            engine=engine,
            size=6,
            health=30,
            name="TinyEnemy",
            position=position,
            theme=theme,
            initial_velocity=velocity,
        )

    def _smoll_enemy(position, velocity=VectorF(0, 0)):
        return Enemy(
            engine=engine,
            size=10,
            health=100,
            name="SmollEnemy",
            position=position,
            theme=Theme(color=_random_color(), bg_color=_random_color()),
            initial_velocity=velocity,
        )

    def _mid_enemy(position, velocity=VectorF(0, 0)):
        return Enemy(
            engine=engine,
            size=20,
            health=400,
            name="MidEnemy",
            position=position,
            theme=Theme(color=_random_color(), bg_color=_random_color()),
            initial_velocity=velocity,
        )

    enemies: list[Enemy] = []

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
