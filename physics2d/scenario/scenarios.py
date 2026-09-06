from typing import TYPE_CHECKING

from constants import ALMOST_ZERO
from factories.theme import Blue, Cyan, Green, Magenta, MakeColor, Red, Theme, White, Yellow
from model.base import PointF, VectorF
from physics2d.constants import X_RESOLUTION_PHYSICS, Y_RESOLUTION_PHYSICS
from physics2d.scenario.piece import ScenarioPiece
from physics2d.scenario.pieces.circunference import CircunferencePiece
from physics2d.scenario.pieces.line import LinePiece
from physics2d.scenario.pieces.rectangle import RectanglePiece
from physics2d.scenario.scenario import Scenario

if TYPE_CHECKING:
    from physics2d.physics2d import Physics2D


def default_scenario(engine: "Physics2D") -> Scenario:
    entities = []

    line_1 = LinePiece(
        points=(PointF(0, 0), PointF(60, 2)), theme=Theme(color=White()), thickness=2
    )
    line_1_1 = LinePiece(
        points=(PointF(60, 2), PointF(120, 50)), theme=Theme(color=White()), thickness=2
    )
    line_1_2 = LinePiece(
        points=(PointF(120, 50), PointF(60, 100)), theme=Theme(color=White()), thickness=2
    )
    line_1_3 = LinePiece(
        points=(PointF(60, 100), PointF(0, 80)), theme=Theme(color=White()), thickness=2
    )
    line_1_4 = LinePiece(
        points=(PointF(0, 80), PointF(-10, 30)), theme=Theme(color=White()), thickness=2
    )
    line_1_5 = LinePiece(
        points=(PointF(-10, 30), PointF(0, 0)), theme=Theme(color=White()), thickness=2
    )
    line_2 = LinePiece(
        points=(PointF(2, 3), PointF(50, 22)),
        theme=Theme(color=Magenta()),
    )
    red_rotating_line_3 = LinePiece(
        points=(PointF(4, 52), PointF(40, 1)),
        theme=Theme(color=Red()),
        thickness=2,
        initial_angular_velocity=10,
        name="LINEA MIA",
    )
    fancy_rotating_line = LinePiece(
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
    bg_rectangle_1 = RectanglePiece(
        vertices=(PointF(6, 33), PointF(17, 5)),
        theme=Theme(color=MakeColor(0.5, (255, 140, 160))),
        secondary_theme=Theme(color=MakeColor(0.5, (80, 80, 250))),
        initial_velocity=VectorF(0.3, 0.5),
        own_gravity=0.005,
    )
    rectangle_2 = RectanglePiece(
        vertices=(PointF(110, 0), PointF(115, 3)),
        theme=Theme(color=MakeColor(1, (244, 25, 45))),
        secondary_theme=Theme(color=MakeColor(1, (1, 254, 45))),
        initial_velocity=VectorF(-0.5, 0.6),
        own_gravity=0.005,
    )
    rectangle_3 = RectanglePiece(
        vertices=(
            PointF(X_RESOLUTION_PHYSICS / 2, Y_RESOLUTION_PHYSICS / 2),
            PointF(X_RESOLUTION_PHYSICS / 2 + 4, Y_RESOLUTION_PHYSICS / 2 + 9),
        ),
        theme=Theme(color=MakeColor(1, (244, 250, 22))),
        secondary_theme=Theme(color=MakeColor(1, (255, 0, 56))),
        floating_multi=0.005,
    )
    bg_circle_1 = CircunferencePiece(
        center=PointF(40, 40),
        theme=Theme(color=Cyan().with_intensity(0.3)),
        radius=6,
        affected_by_gravity=True,
        initial_velocity=VectorF(-0.8, 4),
        floating_multi=0.2,
    )
    bg_circle_5 = CircunferencePiece(
        center=PointF(1, 1),
        theme=Theme(color=Yellow().with_intensity(0.3)),
        radius=1.5,
        affected_by_gravity=True,
        initial_velocity=VectorF(2, 5),
        floating_multi=0.8,
    )
    bg_circle_2 = CircunferencePiece(
        center=PointF(X_RESOLUTION_PHYSICS / 2, Y_RESOLUTION_PHYSICS / 2),
        theme=Theme(color=Blue().with_intensity(0.3)),
        radius=5,
        floating_multi=0.05,
    )
    bg_circle_3 = CircunferencePiece(
        center=PointF(30, 21),
        theme=Theme(color=Green().with_intensity(0.3)),
        radius=15,
        floating_multi=ALMOST_ZERO,
    )
    bg_circle_4 = CircunferencePiece(
        center=PointF(0, 0),
        theme=Theme(color=MakeColor(0.3, (134, 89, 177))),
        radius=25,
        floating_multi=0.005,
    )

    fg_pieces: list[ScenarioPiece] = [
        line_1,
        # line_3,
        rectangle_3,
        # line_4,
        rectangle_2,
    ]

    solid_pieces: list[ScenarioPiece] = [
        CircunferencePiece(
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

    bg_pieces: list[ScenarioPiece] = [
        bg_circle_5,
        bg_rectangle_1,
        # line_2,
        bg_circle_2,
        bg_circle_1,
        bg_circle_4,
        bg_circle_3,
    ]

    return Scenario(
        entities=entities,
        fg_pieces=fg_pieces,
        bg_pieces=bg_pieces,
        solid_pieces=solid_pieces,
        engine=engine,
        player=engine.player,
    )
