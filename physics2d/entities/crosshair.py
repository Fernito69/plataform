from typing import TYPE_CHECKING

from model.base import PointF, VectorF
from model.keyboard import ActionKeys
from model.shared import KeyboardHandler
from model.theme import RGB, Theme
from physics2d.constants import X_RESOLUTION_PHYSICS, Y_RESOLUTION_PHYSICS
from physics2d.entities.base import PhysicsEntity
from physics2d.shapes.line import Line
from terminal import on_key_press

if TYPE_CHECKING:
    from physics2d.physics2d import Physics2D

_CROSSHAIR_THEME = Theme(color=RGB(255, 0, 0))
_DOT_SIZE = 1
_HAIR_SIZE = 4

_CROSSHAIR_ACCEL_AMOUNT = 6.4
_CROSSHAIR_MAX_SPEED = 15


# TODO: this moves similar to player, should share a base class
class Crosshair(PhysicsEntity, KeyboardHandler):
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
        self.handle_keyboard_input()
        self._apply_movement()

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

    def _apply_gravity(self, _: float) -> None: ...

    def _apply_movement(self) -> None:
        self._move_by(self.velocity)

    ##############
    """KEYBOARD"""
    ##############

    def handle_keyboard_input(self):
        self._move_up()
        self._move_left()
        self._move_right()
        self._move_down()

        self._decelerate_if_not_pressing()

    def _decelerate_if_not_pressing(self) -> None:
        _decel_amount = _CROSSHAIR_ACCEL_AMOUNT
        _max_speed = _CROSSHAIR_MAX_SPEED
        if (
            self.velocity.y > 0 and not self._is_pressed(ActionKeys.MOVE_CROSSHAIR_UP)
        ) or self.velocity.y > _max_speed:
            self.velocity = (
                self.velocity + VectorF(0, -min(_decel_amount, self.velocity.y))
            ).as_vector()
        if (
            self.velocity.y < 0 and not self._is_pressed(ActionKeys.MOVE_CROSSHAIR_DOWN)
        ) or self.velocity.y < -_max_speed:
            self.velocity = (
                self.velocity + VectorF(0, max(_decel_amount, self.velocity.y))
            ).as_vector()
        if (
            self.velocity.x > 0 and not self._is_pressed(ActionKeys.MOVE_CROSSHAIR_RIGHT)
        ) or self.velocity.x > _max_speed:
            self.velocity = (
                self.velocity + VectorF(-min(_decel_amount, self.velocity.x), 0)
            ).as_vector()
        if (
            self.velocity.x < 0 and not self._is_pressed(ActionKeys.MOVE_CROSSHAIR_LEFT)
        ) or self.velocity.x < -_max_speed:
            self.velocity = (
                self.velocity + VectorF(max(_decel_amount, self.velocity.x), 0)
            ).as_vector()

    @on_key_press(ActionKeys.MOVE_CROSSHAIR_UP)
    def _move_up(self) -> None:
        if self.velocity.y >= _CROSSHAIR_MAX_SPEED:
            return

        self.velocity = (self.velocity + VectorF(0, _CROSSHAIR_ACCEL_AMOUNT)).as_vector()

    @on_key_press(ActionKeys.MOVE_CROSSHAIR_DOWN)
    def _move_down(self) -> None:
        if self.velocity.y <= -_CROSSHAIR_MAX_SPEED:
            return

        self.velocity = (self.velocity + VectorF(0, -_CROSSHAIR_ACCEL_AMOUNT)).as_vector()

    @on_key_press(ActionKeys.MOVE_CROSSHAIR_LEFT)
    def _move_left(self) -> None:
        if self.velocity.x <= -_CROSSHAIR_MAX_SPEED:
            return

        self.velocity = (self.velocity + VectorF(-_CROSSHAIR_ACCEL_AMOUNT, 0)).as_vector()

    @on_key_press(ActionKeys.MOVE_CROSSHAIR_RIGHT)
    def _move_right(self) -> None:
        if self.velocity.x >= _CROSSHAIR_MAX_SPEED:
            return

        self.velocity = (self.velocity + VectorF(_CROSSHAIR_ACCEL_AMOUNT, 0)).as_vector()
