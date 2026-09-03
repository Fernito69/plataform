from typing import TYPE_CHECKING

from constants import ALMOST_ZERO
from factories.theme import Blue, Cyan, Green, Magenta, MakeColor, Red, Theme, White, Yellow
from model.base import PointF, VectorF
from physics2d.constants import X_RESOLUTION_PHYSICS, Y_RESOLUTION_PHYSICS
from physics2d.scenario.piece import ScenarioPiece
from physics2d.scenario.pieces.circunference import CircunferencePiece
from physics2d.scenario.pieces.line import Line
from physics2d.scenario.pieces.rectangle import Rectangle
from physics2d.scenario.scenario import Scenario

if TYPE_CHECKING:
    from physics2d.physics2d import Physics2D


def default_scenario(engine: "Physics2D") -> Scenario:
    entities = []

    line_1 = Line(
        points=(PointF(0, 0), PointF(120, 2)),
        theme=Theme(color=White()),
    )
    line_2 = Line(
        points=(PointF(2, 3), PointF(50, 22)),
        theme=Theme(color=Magenta()),
    )
    line_3 = Line(
        points=(PointF(4, 52), PointF(40, 1)),
        theme=Theme(color=Red()),
        thickness=2,
        initial_angular_velocity=10,
        name="LINEA MIA",
    )
    line_4 = Line(
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
    rectangle_1 = Rectangle(
        vertices=(PointF(6, 33), PointF(17, 5)),
        theme=Theme(color=MakeColor(1, (255, 140, 160))),
        secondary_theme=Theme(color=MakeColor(1, (80, 80, 250))),
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
    circle_1 = CircunferencePiece(
        center=PointF(40, 40),
        theme=Theme(color=Cyan()),
        radius=6,
        affected_by_gravity=True,
        initial_velocity=VectorF(-0.8, 4),
        floating_multi=0.2,
    )
    circle_5 = CircunferencePiece(
        center=PointF(1, 1),
        theme=Theme(color=Yellow()),
        radius=1.5,
        affected_by_gravity=True,
        initial_velocity=VectorF(2, 5),
        floating_multi=0.8,
    )
    circle_2 = CircunferencePiece(
        center=PointF(X_RESOLUTION_PHYSICS / 2, Y_RESOLUTION_PHYSICS / 2),
        theme=Theme(color=Blue()),
        radius=5,
        floating_multi=0.05,
    )
    circle_3 = CircunferencePiece(
        center=PointF(30, 21), theme=Theme(color=Green()), radius=15, floating_multi=ALMOST_ZERO
    )
    circle_4 = CircunferencePiece(
        center=PointF(0, 0),
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

    return Scenario(entities=entities, pieces=pieces, engine=engine, player=engine.player)
