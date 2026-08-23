from typing import TYPE_CHECKING

from model.base import Point2, Vector2
from model.theme import Theme

if TYPE_CHECKING:
    from physics2d.scenario.scenario import Scenario


class Entity:
    position: Point2
    velocity: Vector2

    theme: Theme

    density: float
    volume: float

    def __init__(
        self,
        scenario: "Scenario",
        density: int = 1,
        position: Point2 = (0, 0),
        velocity: Vector2 = (0, 0),
        theme: Theme = Theme(),
    ):
        self.scenario = scenario
        self.position = position
        self.velocity = velocity
        self.theme = theme
        self.density = density  

        # volume depends on the type of entity
