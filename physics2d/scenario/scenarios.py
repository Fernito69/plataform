from typing import TYPE_CHECKING

from factories.theme import Blue, Cyan, Green, Magenta, MakeColor, Red, Theme, White, Yellow
from physics2d.constants import X_RESOLUTION_PHYSICS, Y_RESOLUTION_PHYSICS
from physics2d.scenario.piece import ScenarioPiece
from physics2d.scenario.pieces.circunference import Circunference
from physics2d.scenario.pieces.line import Line
from physics2d.scenario.pieces.rectangle import Rectangle
from physics2d.scenario.scenario import Scenario

if TYPE_CHECKING:
    from physics2d.physics2d import Physics2D


def default_scenario(engine: "Physics2D") -> Scenario:
    entities = []

    line_1 = Line(
        points=((0, 0), (120, 2)),
        theme=Theme(color=White()),
    )
    line_2 = Line(
        points=((2, 3), (50, 22)),
        theme=Theme(color=Magenta()),
    )
    line_3 = Line(
        points=((4, 52), (40, 1)), theme=Theme(color=Red()), thickness=2, initial_angular_velocity=1
    )
    line_4 = Line(
        points=(
            (4, Y_RESOLUTION_PHYSICS / 2 - 6),
            (X_RESOLUTION_PHYSICS - 4, Y_RESOLUTION_PHYSICS / 2 + 12),
        ),
        theme=Theme(color=MakeColor(1, (12, 250, 23))),
        secondary_theme=Theme(color=MakeColor(1, (26, 1, 255))),
        thickness=4,
        floating_multi=0.02,
        pulsate_freq=0.5,
        pulsate_amplitude=0.5,
    )
    rectangle_1 = Rectangle(
        vertices=((6, 33), (17, 5)),
        theme=Theme(color=MakeColor(1, (255, 140, 160))),
        secondary_theme=Theme(color=MakeColor(1, (80, 80, 250))),
        initial_velocity=(0.3, 0.5),
        own_gravity=0.005,
    )
    rectangle_2 = Rectangle(
        vertices=((110, 0), (115, 3)),
        theme=Theme(color=MakeColor(1, (244, 25, 45))),
        secondary_theme=Theme(color=MakeColor(1, (1, 254, 45))),
        initial_velocity=(-0.5, 0.6),
        own_gravity=0.005,
    )
    rectangle_3 = Rectangle(
        vertices=(
            (X_RESOLUTION_PHYSICS / 2, Y_RESOLUTION_PHYSICS / 2),
            (X_RESOLUTION_PHYSICS / 2 + 4, Y_RESOLUTION_PHYSICS / 2 + 9),
        ),
        theme=Theme(color=MakeColor(1, (244, 250, 22))),
        secondary_theme=Theme(color=MakeColor(1, (255, 0, 56))),
        floating_multi=0.005,
    )
    circle_1 = Circunference(
        center=(40, 40),
        theme=Theme(color=Cyan()),
        radius=6,
        affected_by_gravity=True,
        initial_velocity=(-0.8, 4),
        floating_multi=0.2,
    )
    circle_5 = Circunference(
        center=(1, 1),
        theme=Theme(color=Yellow()),
        radius=1.5,
        affected_by_gravity=True,
        initial_velocity=(2, 5),
        floating_multi=0.8,
    )
    circle_2 = Circunference(
        center=(X_RESOLUTION_PHYSICS / 2, Y_RESOLUTION_PHYSICS / 2),
        theme=Theme(color=Blue()),
        radius=5,
        floating_multi=0.05,
    )
    circle_3 = Circunference(
        center=(30, 21), theme=Theme(color=Green()), radius=15, floating_multi=0.01
    )
    circle_4 = Circunference(
        center=(0, 0),
        theme=Theme(color=MakeColor(1, (134, 89, 177))),
        radius=25,
        floating_multi=0.005,
    )

    pieces: list[ScenarioPiece] = [
        line_1,
        line_3,
        rectangle_3,
        line_4,
        rectangle_2,
        circle_5,
        rectangle_1,
        line_2,
        circle_2,
        circle_1,
        circle_4,
        circle_3,
    ]

    return Scenario(entities=entities, pieces=pieces, engine=engine)
