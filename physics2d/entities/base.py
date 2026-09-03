from typing import TYPE_CHECKING, Optional

from model.base import PointF, VectorF
from model.theme import Theme
from physics2d.shapes.shape import Shape

if TYPE_CHECKING:
    from physics2d.scenario.scenario import Scenario


class PhyEntity(Shape):
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
        angle: float = 0,
        affected_by_gravity: bool = False,
        initial_velocity: VectorF = VectorF(0, 0),
        initial_angular_velocity: float = 0,
        own_gravity: float | None = None,
        secondary_theme: Theme | None = None,
        floating_multi: float = 0,
    ):
        Shape.__init__(
            self,
            theme=theme,
            angle=angle,
            secondary_theme=secondary_theme,
            own_gravity=own_gravity,
            initial_angular_velocity=initial_angular_velocity,
            affected_by_gravity=affected_by_gravity,
            floating_multi=floating_multi,
            initial_velocity=initial_velocity,
            center_of_mass=position,
            name="Physics Entity",
        )
        self._scenario = scenario
        self.position = position
        self.velocity = velocity
        self.density = density
        self.name = name

        # volume depends on the type of entity

    def set_scenario(self, scenario: "Scenario") -> None:
        self._scenario = scenario

    def is_same_position(self, shape: Shape) -> bool:
        # TODO implement
        return True
