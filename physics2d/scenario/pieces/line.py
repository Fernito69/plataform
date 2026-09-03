import math

from constants import PI
from model.base import PointF, VectorF
from model.theme import Theme
from physics2d.constants import DEFAULT_GRAVITY_ACCELERATION
from physics2d.model.shapes import Line
from physics2d.scenario.piece import ScenarioPiece


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
        )
        ScenarioPiece.__init__(
            self,
            name=name,
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

    def do_your_thing(self, gravity_accel: float = DEFAULT_GRAVITY_ACCELERATION) -> None:
        self._apply_gravity(gravity_accel)
        self._apply_movement()
        self._pulsate()


    def _pulsate(self) -> None:
        if self._pulsate_freq == 0 or self._pulsate_amplitude == 0:
            return

        self._counter = (self._counter + self._pulsate_freq) % (2 * PI)
        self.thickness += math.sin(self._counter) * self._pulsate_amplitude

    # def _get_color(self, x: int | None = None, y: int | None = None) -> RGB:
    #     if not self.secondary_theme:
    #         return self.theme.color or White()

    #     # check which direction is the widest (literally the same as rectangle)
    #     vertex_1, vertex_2 = self.points
    #     width = abs(vertex_1.x - vertex_2.x)
    #     height = abs(vertex_1.y - vertex_2.y)

    #     apply_gradient_horizontally: bool = width >= height
    #     if (
    #         apply_gradient_horizontally
    #         and x is None
    #         or not apply_gradient_horizontally
    #         and y is None
    #     ):
    #         raise IndexError("What's wrong with you?")

    #     color_ratio: float = (
    #         abs(vertex_1.x - x) / width
    #         if apply_gradient_horizontally and x is not None
    #         else abs(vertex_1.y - y) / height
    #         if y is not None
    #         else 0
    #     )

    #     color: RGB = mix_colors(
    #         [
    #             (self.theme.color or White()).with_intensity(color_ratio),
    #             (self.secondary_theme.color or White()).with_intensity(1 - color_ratio),
    #         ]
    #     )

    #     return color
