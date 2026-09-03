from typing import TYPE_CHECKING, Optional

from model.base import PointF, VectorF
from model.theme import Theme
from physics2d.model.shapes import Shape

if TYPE_CHECKING:
    from physics2d.scenario.scenario import Scenario


class Entity(Shape):
    position: PointF
    velocity: VectorF

    density: float
    volume: float
    name: str | None

    def __init__(
        self,
        scenario: Optional["Scenario"] = None,
        name: str | None = None,
        density: int = 1,
        position: PointF = PointF(0, 0),
        velocity: VectorF = VectorF(0, 0),
        theme: Theme = Theme(),
    ):
        super().__init__(theme=theme)
        self._scenario = scenario
        self.position = position
        self.velocity = velocity
        self.density = density
        self.name = name

        # volume depends on the type of entity

    def set_scenario(self, scenario: "Scenario") -> None:
        self._scenario = scenario
