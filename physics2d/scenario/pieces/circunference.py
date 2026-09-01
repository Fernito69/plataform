from dataclasses import dataclass
from typing import Callable

from model.base import Point2F, Vector2F
from model.theme import Theme
from physics2d.model.shapes import Circunference
from physics2d.scenario.piece import ScenarioPiece


@dataclass
class GetCircunferenceEquationResponse:
    get_ys: Callable[[float], tuple[float, float] | tuple[None, None]]
    get_xs: Callable[[float], tuple[float, float] | tuple[None, None]]


class CircunferencePiece(Circunference, ScenarioPiece):
    center: Point2F
    radius: float

    def __init__(
        self,
        center: Point2F,
        radius: float,
        theme: Theme = Theme(),
        angle: float = 0,
        affected_by_gravity: bool = False,
        initial_velocity: Vector2F = (0, 0),
        own_gravity: float | None = None,
        secondary_theme: Theme | None = None,
        floating_multi: float = 0,
        initial_angular_velocity: float = 0,
    ):
        Circunference.__init__(self, center, radius, theme)
        ScenarioPiece.__init__(
            self,
            name="Circle",
            theme=theme,
            angle=angle,
            initial_velocity=initial_velocity,
            affected_by_gravity=affected_by_gravity,
            own_gravity=own_gravity,
            secondary_theme=secondary_theme,
            floating_multi=floating_multi,
            center_of_mass=center,
            initial_angular_velocity=initial_angular_velocity,
        )

    def _apply_movement(self) -> None:
        self._float_around()

        if not any(a != 0 for a in self.velocity):
            return
        self.center = (self.center[0] + self.velocity[0], self.center[1] + self.velocity[1])
        self.center_of_mass = self.center

    def get_circunference_equations(
        self,
    ) -> GetCircunferenceEquationResponse:
        def get_ys(x: float) -> tuple[float, float] | tuple[None, None]:
            root_arg = self.radius**2 - (x - self.center[0]) ** 2
            if root_arg < 0:
                return (None, None)
            root = root_arg**0.5
            return (self.center[1] - root, self.center[1] + root)

        def get_xs(y: float) -> tuple[float, float] | tuple[None, None]:
            root_arg = self.radius**2 - (y - self.center[1]) ** 2
            if root_arg < 0:
                return (None, None)
            root = root_arg**0.5
            return (self.center[0] - root, self.center[0] + root)

        return GetCircunferenceEquationResponse(get_xs=get_xs, get_ys=get_ys)

    def rotate(self) -> None:
        pass
