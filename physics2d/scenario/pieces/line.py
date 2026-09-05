import math
from typing import TYPE_CHECKING

from constants import PI
from model.base import PointF, VectorF
from model.theme import Theme
from physics2d.scenario.piece import ScenarioPiece
from physics2d.shapes.line import Line

if TYPE_CHECKING:
    from physics2d.physics2d import Physics2D


class LinePiece(Line, ScenarioPiece):
    _pulsate_freq: float
    _pulsate_amplitude: float

    def __init__(
        self,
        points: tuple[PointF, PointF],
        theme: Theme = Theme(),
        angle: float = 0,
        thickness: float = 1,
        affected_by_gravity: bool = False,
        initial_velocity: VectorF = VectorF(0, 0),
        own_gravity: float | None = None,
        secondary_theme: Theme | None = None,
        floating_multi: float = 0,
        pulsate_freq: float = 0,
        pulsate_amplitude: float = 0,
        initial_angular_velocity: float = 0,
        density: float = 1,
        name: str = "Line",
    ):
        self._pulsate_freq = pulsate_freq
        self._pulsate_amplitude = pulsate_amplitude

        Line.__init__(
            self,
            points=points,
            thickness=thickness,
            theme=theme,
            secondary_theme=secondary_theme,
            angle=angle,
            affected_by_gravity=affected_by_gravity,
            initial_velocity=initial_velocity,
            own_gravity=own_gravity,
            floating_multi=floating_multi,
            initial_angular_velocity=initial_angular_velocity,
            density=density,
        )
        ScenarioPiece.__init__(
            self,
            name=name,
            density=density,
            volume=self.volume,
        )

        self.theme = theme
        self.secondary_theme = secondary_theme
        self.thickness = thickness
        self.points = points
        self.velocity = initial_velocity
        self.angular_velocity = initial_angular_velocity
        self._own_gravity_accel = own_gravity
        self.floating_multi = floating_multi
        self._affected_by_gravity = affected_by_gravity
        self.update_center_of_mass()

    _counter: float = 0

    def do_your_thing(self, engine: "Physics2D") -> None:
        self._apply_gravity(engine.scenario.gravity_acceleration)
        self._apply_movement(engine)
        self._pulsate()

    def _pulsate(self) -> None:
        if self._pulsate_freq == 0 or self._pulsate_amplitude == 0:
            return

        self._counter = (self._counter + self._pulsate_freq) % (2 * PI)
        self.thickness += math.sin(self._counter) * self._pulsate_amplitude
