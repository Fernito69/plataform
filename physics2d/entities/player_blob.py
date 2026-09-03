from typing import TYPE_CHECKING

from model.base import PointF, VectorF
from model.keyboard import MovementKeys
from model.shared import KeyboardHandler
from model.theme import RGB, Theme
from physics2d.entities.base import Entity
from physics2d.model.shapes import Circunference
from terminal import on_key_press

if TYPE_CHECKING:
    from physics2d.physics2d import Physics2D

_PLAYER_RADIUS = 4
_PLAYER_THEME = Theme(color=RGB(244, 255, 0))
_PLAYER_GRAVITY = 0  # we float freely!

_MAX_MOVING_VELOCITY = 5
_ACCEL_FACTOR = 1
_DECEL_FACTOR = _ACCEL_FACTOR / 2

_MIN_PLAYER_DISTANCE_TO_SCREEN_BORDER = 20


class PlayerBlob(Entity, Circunference, KeyboardHandler):
    def __init__(
        self, engine: "Physics2D", position: PointF = PointF(20, 20), velocity=VectorF(0, 0)
    ):
        Entity().__init__(name="Player", position=position, velocity=velocity)
        Circunference(center=position, radius=_PLAYER_RADIUS, theme=_PLAYER_THEME).__init__(
            center=position, radius=_PLAYER_RADIUS, theme=_PLAYER_THEME
        )
        self.engine = engine
        self.center = position
        self.position = position
        self.radius = _PLAYER_RADIUS
        self.theme = _PLAYER_THEME
        self.velocity = VectorF(0, 0)

    ##############
    """MOVEMENT"""
    ##############

    def do_your_thing(self, gravity_accel: float = _PLAYER_GRAVITY) -> None:
        self.handle_keyboard_input()
        self._apply_gravity(gravity_accel)
        self._apply_movement()
        self._keep_player_in_screen()

    def _move_by(self, vector: VectorF) -> None:
        # TODO: test with +=
        self.center = self.center + vector
        self.position = self.position + vector

    def _apply_gravity(self, gravity_accel: float) -> None:
        # we float freely for now
        pass

    def _apply_movement(self) -> None:
        self._move_by(self.velocity)

    def _keep_player_in_screen(self) -> None:
        """Adjusts the screen position in order to keep the player always visible"""
        x_res = self.engine.screen_buffer_x_res
        y_res = self.engine.screen_buffer_y_res
        player_x, player_y, _ = self.position

        if player_x < self.engine.screen_corner.x + _MIN_PLAYER_DISTANCE_TO_SCREEN_BORDER:
            self.engine.screen_corner = PointF(
                round(player_x - _MIN_PLAYER_DISTANCE_TO_SCREEN_BORDER),
                self.engine.screen_corner.y,
            )
        if player_x > self.engine.screen_corner.x + (x_res - _MIN_PLAYER_DISTANCE_TO_SCREEN_BORDER):
            self.engine.screen_corner = PointF(
                round(player_x + _MIN_PLAYER_DISTANCE_TO_SCREEN_BORDER - x_res),
                self.engine.screen_corner.y,
            )
        if player_y < self.engine.screen_corner.y + _MIN_PLAYER_DISTANCE_TO_SCREEN_BORDER:
            self.engine.screen_corner = PointF(
                self.engine.screen_corner.x,
                round(player_y - _MIN_PLAYER_DISTANCE_TO_SCREEN_BORDER),
            )
        if player_y > self.engine.screen_corner.y + y_res - _MIN_PLAYER_DISTANCE_TO_SCREEN_BORDER:
            self.engine.screen_corner = PointF(
                self.engine.screen_corner.x,
                round(player_y + _MIN_PLAYER_DISTANCE_TO_SCREEN_BORDER - y_res),
            )

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
        if self.velocity.y > 0 and not self._is_pressed(MovementKeys.UP):
            self.velocity = (self.velocity + VectorF(0, -_DECEL_FACTOR)).as_vector()
        if self.velocity.y < 0 and not self._is_pressed(MovementKeys.DOWN):
            self.velocity = (self.velocity + VectorF(0, _DECEL_FACTOR)).as_vector()
        if self.velocity.x > 0 and not self._is_pressed(MovementKeys.RIGHT):
            self.velocity = (self.velocity + VectorF(-_DECEL_FACTOR, 0)).as_vector()
        if self.velocity.x < 0 and not self._is_pressed(MovementKeys.LEFT):
            self.velocity = (self.velocity + VectorF(_DECEL_FACTOR, 0)).as_vector()

    @on_key_press(MovementKeys.UP)
    def _move_up(self) -> None:
        if self.velocity.y >= _MAX_MOVING_VELOCITY:
            return

        self.velocity = (self.velocity + VectorF(0, _ACCEL_FACTOR)).as_vector()

    @on_key_press(MovementKeys.DOWN)
    def _move_down(self) -> None:
        if self.velocity.y <= -_MAX_MOVING_VELOCITY:
            return

        self.velocity = (self.velocity + VectorF(0, -_ACCEL_FACTOR)).as_vector()

    @on_key_press(MovementKeys.LEFT)
    def _move_left(self) -> None:
        if self.velocity.x <= -_MAX_MOVING_VELOCITY:
            return

        self.velocity = (self.velocity + VectorF(-_ACCEL_FACTOR, 0)).as_vector()

    @on_key_press(MovementKeys.RIGHT)
    def _move_right(self) -> None:
        if self.velocity.x >= _MAX_MOVING_VELOCITY:
            return

        self.velocity = (self.velocity + VectorF(_ACCEL_FACTOR, 0)).as_vector()
