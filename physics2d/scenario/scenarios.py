from random import random
from typing import TYPE_CHECKING

from constants import ALMOST_ZERO
from factories.theme import Blue, Cyan, Green, Magenta, MakeColor, Red, Theme, White, Yellow
from model.base import PointF, VectorF
from model.theme import RGB
from physics2d.constants import X_RESOLUTION_PHYSICS, Y_RESOLUTION_PHYSICS
from physics2d.entities.enemy import Enemy
from physics2d.entities.three_dee_enemy import ThreeDeeEnemy
from physics2d.scenario.scenario import Scenario
from physics2d.shape.base import Shape
from physics2d.shape.circunference import Circunference
from physics2d.shape.line import Line
from physics2d.shape.rectangle import Rectangle
from three_d_renderer.entities.polyhedra import Dodeca

if TYPE_CHECKING:
    from physics2d.physics2d import Physics2D


def default_scenario(engine: "Physics2D") -> Scenario:
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
            size=6,
            health=30,
            name="TinyEnemy",
            position=position,
            theme=theme,
            initial_velocity=velocity,
        )

    def _smoll_enemy(position, velocity=VectorF(0, 0)):
        return Enemy(
            size=10,
            health=100,
            name="SmollEnemy",
            position=position,
            theme=Theme(color=_random_color(), bg_color=_random_color()),
            initial_velocity=velocity,
        )

    def _mid_enemy(position, velocity=VectorF(0, 0)):
        return Enemy(
            size=20,
            health=400,
            name="MidEnemy",
            position=position,
            theme=Theme(color=_random_color(), bg_color=_random_color()),
            initial_velocity=velocity,
        )

    enemies: list[Enemy] = [
        _smoll_enemy(PointF(150, 200)),
        _smoll_enemy(PointF(170, 210)),
        _smoll_enemy(PointF(160, 190)),
        _smoll_enemy(PointF(120, 200)),
        _smoll_enemy(PointF(199, 256)),
        _smoll_enemy(PointF(152, 180)),
        _smoll_enemy(PointF(250, 300)),
        _smoll_enemy(PointF(256, 312)),
        _smoll_enemy(PointF(312, 256)),
        _smoll_enemy(PointF(384, 322)),
        _smoll_enemy(PointF(350, 290)),
        _smoll_enemy(PointF(384, 322)),
        _smoll_enemy(PointF(484, 312)),
        _smoll_enemy(PointF(494, 322)),
        _smoll_enemy(PointF(474, 332)),
        _smoll_enemy(PointF(464, 342)),
        _smoll_enemy(PointF(454, 352)),
        _smoll_enemy(PointF(444, 362)),
        _mid_enemy(PointF(150, 150)),
        _mid_enemy(PointF(250, 150)),
        _mid_enemy(PointF(230, 180)),
        _mid_enemy(PointF(230, 290), VectorF.random_offset_vector(0.1, 0.1)),
        _mid_enemy(PointF(230, 500), VectorF.random_offset_vector(0.1, 0.1)),
        Enemy(
            size=30,
            health=600,
            name="BigEnemy",
            position=PointF(150, 100),
            theme=Theme(color=RGB(170, 0, 0, 1)),
        ),
        Enemy(
            size=35,
            health=600,
            name="BigEnemy",
            position=PointF(300, 100),
            theme=Theme(color=RGB(170, 122, 0, 1)),
        ),
    ]

    for a in range(15):
        enemies.append(_smoll_enemy(PointF(484 - a * 15, 312 - a * 15)))
        enemies.append(_smoll_enemy(PointF(380 - a * 15, 280)))

    _spacing = 10
    _cube_side = 10
    for y in range(_cube_side):
        for x in range(_cube_side):
            enemies.append(
                _tiny_enemy(
                    PointF(200 + y * _spacing, 100 + x * _spacing)
                    + VectorF.random_offset_vector(3, 3),
                    theme=Theme(
                        color=RGB(
                            255 - (255 / _cube_side) * x,
                            (255 / _cube_side) * abs(x - y),
                            255 - (255 / _cube_side) * abs(y - x),
                        )
                    ),
                )
            )

    line_1 = Line(points=(PointF(0, 0), PointF(60, 2)), theme=Theme(color=White()), thickness=2)
    line_1_1 = Line(
        points=(PointF(60, 2), PointF(120, 50)), theme=Theme(color=White()), thickness=2
    )
    line_1_2 = Line(
        points=(PointF(120, 50), PointF(60, 100)), theme=Theme(color=White()), thickness=2
    )
    line_1_3 = Line(
        points=(PointF(60, 100), PointF(0, 80)), theme=Theme(color=White()), thickness=2
    )
    line_1_4 = Line(
        points=(PointF(0, 80), PointF(-10, 30)), theme=Theme(color=White()), thickness=2
    )
    line_1_5 = Line(points=(PointF(-10, 30), PointF(0, 0)), theme=Theme(color=White()), thickness=2)
    line_2 = Line(
        points=(PointF(2, 3), PointF(50, 22)),
        theme=Theme(color=Magenta()),
    )
    red_rotating_line_3 = Line(
        points=(PointF(4, 52), PointF(40, 1)),
        theme=Theme(color=Red()),
        thickness=2,
        initial_angular_velocity=10,
        name="LINEA MIA",
    )
    fancy_rotating_line = Line(
        points=(
            PointF(4, Y_RESOLUTION_PHYSICS / 2 - 6),
            PointF(X_RESOLUTION_PHYSICS - 4, Y_RESOLUTION_PHYSICS / 2 + 12),
        ),
        theme=Theme(color=MakeColor(1, (12, 25, 230))),
        secondary_theme=Theme(color=MakeColor(1, (255, 1, 25))),
        thickness=4,
        floating_multi=0.02,
        pulsate_freq=0.5,
        pulsate_amplitude=0.5,
        initial_angular_velocity=200,
    )
    bg_rectangle_1 = Rectangle(
        vertices=(PointF(6, 33), PointF(17, 5)),
        theme=Theme(color=MakeColor(0.5, (255, 140, 160))),
        secondary_theme=Theme(color=MakeColor(0.5, (80, 80, 250))),
        initial_velocity=VectorF(0.3, 0.5),
        own_gravity=0.005,
    )
    rectangle_2 = Rectangle(
        vertices=(PointF(110, 0), PointF(115, 3)),
        theme=Theme(color=MakeColor(1, (244, 25, 45))),
        secondary_theme=Theme(color=MakeColor(1, (1, 254, 45))),
        initial_velocity=VectorF(-0.5, 0.6),
        own_gravity=0.005,
    )
    rectangle_3 = Rectangle(
        vertices=(
            PointF(X_RESOLUTION_PHYSICS / 2, Y_RESOLUTION_PHYSICS / 2),
            PointF(X_RESOLUTION_PHYSICS / 2 + 4, Y_RESOLUTION_PHYSICS / 2 + 9),
        ),
        theme=Theme(color=MakeColor(1, (244, 250, 22))),
        secondary_theme=Theme(color=MakeColor(1, (255, 0, 56))),
        floating_multi=0.005,
    )
    bg_circle_1 = Circunference(
        center=PointF(40, 40),
        theme=Theme(color=Cyan().with_intensity(0.3)),
        radius=6,
        affected_by_gravity=True,
        initial_velocity=VectorF(-0.8, 4),
        floating_multi=0.2,
    )
    bg_circle_5 = Circunference(
        center=PointF(1, 1),
        theme=Theme(color=Yellow().with_intensity(0.3)),
        radius=1.5,
        affected_by_gravity=True,
        initial_velocity=VectorF(2, 5),
        floating_multi=0.8,
    )
    bg_circle_2 = Circunference(
        center=PointF(X_RESOLUTION_PHYSICS / 2, Y_RESOLUTION_PHYSICS / 2),
        theme=Theme(color=Blue().with_intensity(0.3)),
        radius=5,
        floating_multi=0.05,
    )
    bg_circle_3 = Circunference(
        center=PointF(30, 21),
        theme=Theme(color=Green().with_intensity(0.3)),
        radius=15,
        floating_multi=ALMOST_ZERO,
    )
    bg_circle_4 = Circunference(
        center=PointF(0, 0),
        theme=Theme(color=MakeColor(0.3, (134, 89, 177))),
        radius=25,
        floating_multi=0.005,
    )

    fg_pieces: list[Shape] = [
        line_1,
        # line_3,
        rectangle_3,
        # line_4,
        rectangle_2,
    ]

    solid_pieces: list[Shape] = [
        Circunference(
            center=PointF(50, 50),
            theme=Theme(color=MakeColor(1, (255, 200, 255))),
            radius=15,
            initial_velocity=VectorF(0, -0.1),
        ),
        # red_rotating_line_3,
        # line_1,
        # line_1_1,
        line_1_2,
        line_1_3,
        line_1_4,
        line_1_5,
        # fancy_rotating_line
    ]

    bg_pieces: list[Shape] = [
        bg_circle_5,
        bg_rectangle_1,
        # line_2,
        bg_circle_2,
        bg_circle_1,
        bg_circle_4,
        bg_circle_3,
    ]
    three_dee_enemies: list[ThreeDeeEnemy] = [
        ThreeDeeEnemy(
            engine=engine,
            health=100,
            position=PointF(100, 0),
            polyhedron=Dodeca(
                position=PointF(0, 100, 20),
                size=15,
                angle=VectorF(0, 30, 0),
                mov_vector=VectorF(0, 0, 0),
                rot_vector=VectorF(-1, 2, 0),
            ),
            theme=Theme(RGB(255, 100, 255)),
        )
    ]

    return Scenario(
        enemies=enemies,
        three_dee_enemies=three_dee_enemies,
        fg_shapes=fg_pieces,
        bg_shapes=bg_pieces,
        solid_shapes=solid_pieces,
        engine=engine,
        player=engine.player,
    )
