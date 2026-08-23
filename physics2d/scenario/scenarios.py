from typing import TYPE_CHECKING

from factories.theme import Magenta, Red, Theme, White
from physics2d.scenario.piece import Line, Rectangle, ScenarioPiece
from physics2d.scenario.scenario import Scenario

if TYPE_CHECKING:
    from physics2d.physics2d import Physics2D


def default_scenario(engine: "Physics2D") -> Scenario:
    entities = []

    line_1 = Line(
        vertices=((0, 0), (60, 2)),
        theme=Theme(color=White()),
    )
    line_2 = Line(
        vertices=((1, 3), (50, 22)),
        theme=Theme(color=Magenta()),
    )
    line_3 = Line(
        vertices=((4, 52), (40, 5)),
        theme=Theme(color=Red()),
    )
    rectangle_1 = Rectangle(
        vertices=((6, 33), (17, 5)),
        theme=Theme(color=Red(0.2)),
    )

    pieces: list[ScenarioPiece] = [line_1, line_3, rectangle_1, line_2]

    return Scenario(entities=entities, pieces=pieces, engine=engine)
