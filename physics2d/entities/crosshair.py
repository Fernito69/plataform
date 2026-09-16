from typing import TYPE_CHECKING

from model.base import PointF, VectorF
from model.theme import RGB, Theme
from physics2d.constants import X_RESOLUTION_PHYSICS, Y_RESOLUTION_PHYSICS
from physics2d.entities.base import PhysicsEntity
from physics2d.shapes.line import Line
from terminal import consume_mouse_movement

if TYPE_CHECKING:
    from physics2d.physics2d import Physics2D

_CROSSHAIR_THEME = Theme(color=RGB(120, 255, 255))
_DOT_SIZE = 1
_HAIR_SIZE = 4

_MOUSE_SENSITIVITY = 0.2


# TODO: this moves similar to player, should share a base class
class Crosshair(PhysicsEntity):
    def __init__(
        self,
        engine: "Physics2D",
        position: PointF = PointF(X_RESOLUTION_PHYSICS / 2, Y_RESOLUTION_PHYSICS / 2),
        velocity=VectorF(0, 0),
        density: float = 1,
    ):
        super().__init__(
            name="Crosshair",
            position=position,
            initial_velocity=velocity,
            density=density,
            size=_DOT_SIZE,
            theme=_CROSSHAIR_THEME,
        )
        self.engine = engine
        self.center = position
        self.position = position
        self.radius = _DOT_SIZE
        self.theme = _CROSSHAIR_THEME
        self.velocity = velocity
        self.name = "Crosshair"

        # make the cross:
        def _make_line(l: tuple[tuple[float, float], tuple[float, float]]):
            return Line(
                points=(
                    self.center + PointF(l[0][0], l[0][1]),
                    self.center + PointF(l[1][0], l[1][1]),
                ),
                thickness=1,
                theme=_CROSSHAIR_THEME,
            )

        self.extra_shapes = [
            _make_line(((0, 3), (0, 3 + _HAIR_SIZE))),
            _make_line(((3, 0), (3 + _HAIR_SIZE, 0))),
            _make_line(((0, -3), (0, -3 - _HAIR_SIZE))),
            _make_line(((-3, 0), (-3 - _HAIR_SIZE, 0))),
        ]

    ##############
    """MOVEMENT"""
    ##############

    def do_your_thing(self) -> None:
        dx, dy = consume_mouse_movement()

        if dx != 0 or dy != 0:
            self._move_by(
                VectorF(
                    dx * _MOUSE_SENSITIVITY,
                    -dy * _MOUSE_SENSITIVITY,
                )
            )

    def _move_by(self, vector: VectorF) -> None:
        new_center = self.center + vector

        if new_center.y >= Y_RESOLUTION_PHYSICS:
            new_center.y = Y_RESOLUTION_PHYSICS - 1
        if new_center.x >= X_RESOLUTION_PHYSICS:
            new_center.x = X_RESOLUTION_PHYSICS - 1
        if new_center.x < 0:
            new_center.x = 0
        if new_center.y < 0:
            new_center.y = 0

        final_vector = (new_center - self.center).as_vector()

        self.center = new_center
        self.position = new_center

        for p in self.extra_shapes:
            if not isinstance(p, Line):
                continue
            p._move_by(final_vector)
