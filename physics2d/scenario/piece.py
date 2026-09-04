from typing import TYPE_CHECKING

from model.base import PointF, VectorF
from model.theme import Theme
from physics2d.shapes.shape import Shape

if TYPE_CHECKING:
    from physics2d.scenario.scenario import Scenario


class ScenarioPiece(Shape):
    name: str

    def __init__(
        self,
        name: str,
        density: float,
        volume: float,
        theme: Theme = Theme(),
        angle: float = 0,
        affected_by_gravity: bool = False,
        initial_velocity: VectorF = VectorF(0, 0),
        own_gravity: float | None = None,
        secondary_theme: Theme | None = None,
        floating_multi: float = 0,
        initial_angular_velocity: float = 0,
    ):
        super().__init__(
            name=name or self.name,
            theme=theme,
            angle=angle,
            affected_by_gravity=affected_by_gravity,
            initial_velocity=initial_velocity,
            own_gravity=own_gravity,
            secondary_theme=secondary_theme,
            floating_multi=floating_multi,
            center_of_mass=PointF(0, 0),  # TODO: fix this
            initial_angular_velocity=initial_angular_velocity,
            density=density,
            volume=volume,
        )

    def do_your_thing(self, scenario: "Scenario") -> None:
        self._apply_gravity(scenario.gravity_acceleration)
        self._apply_movement(scenario)
