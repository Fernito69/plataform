from dataclasses import dataclass
from typing import Callable

from model.base import PointF, VectorF
from model.theme import Theme
from physics2d.scenario.piece import ScenarioPiece
from physics2d.scenario.scenario import Scenario
from physics2d.shapes.circunference import Circunference


@dataclass
class GetCircunferenceEquationResponse:
    get_ys: Callable[[float], tuple[float, float] | tuple[None, None]]
    get_xs: Callable[[float], tuple[float, float] | tuple[None, None]]


class CircunferencePiece(Circunference, ScenarioPiece):
    center: PointF
    radius: float

    def __init__(
        self,
        center: PointF,
        radius: float,
        density: float = 1,
        theme: Theme = Theme(),
        angle: float = 0,
        affected_by_gravity: bool = False,
        initial_velocity: VectorF = VectorF(0, 0),
        own_gravity: float | None = None,
        secondary_theme: Theme | None = None,
        floating_multi: float = 0,
        initial_angular_velocity: float = 0,
    ):
        Circunference.__init__(
            self,
            center=center,
            radius=radius,
            theme=theme,
            angle=angle,
            initial_velocity=initial_velocity,
            affected_by_gravity=affected_by_gravity,
            own_gravity=own_gravity,
            secondary_theme=secondary_theme,
            floating_multi=floating_multi,
            initial_angular_velocity=initial_angular_velocity,
            density=density,
        )
        # TODO: fix this, shuld not require the same params to init
        ScenarioPiece.__init__(
            self,
            name="Circle",
            density=density,
            volume=self.volume,
            theme=theme,
            secondary_theme=secondary_theme,
            angle=angle,
            initial_velocity=initial_velocity,
            affected_by_gravity=affected_by_gravity,
            own_gravity=own_gravity,
            floating_multi=floating_multi,
            initial_angular_velocity=initial_angular_velocity,
        )
        self.center = center
        self.theme = theme
        self.secondary_theme = secondary_theme
        self.radius = radius
        self.initial_angular_velocity = initial_angular_velocity
        self._affected_by_gravity = affected_by_gravity
        self._own_gravity_accel = own_gravity
        self.floating_multi = floating_multi
        self.velocity = initial_velocity
        self.angular_velocity = initial_angular_velocity
        self.weight = self.volume * self.density

    def _apply_movement(self, scenario: "Scenario") -> None:
        self._float_around()
        self.center = self.center + self.velocity
        self.center_of_mass = self.center_of_mass + self.velocity
        self.would_collide_with(scenario.player)
