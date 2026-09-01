from model.base import Point2F, Vector2F
from model.keyboard import MovementKeys
from model.shared import KeyboardHandler
from model.theme import RGB, Theme
from physics2d.entities.base import Entity
from physics2d.model.shapes import Circunference
from terminal import on_key_press
from utils import add_tuple

_PLAYER_RADIUS = 2
_PLAYER_THEME = Theme(color=RGB(0, 255, 0))
_PLAYER_GRAVITY = 0  # we fly freely!

_MAX_MOVING_VELOCITY = 5
_ACCEL_FACTOR = 1
_DECEL_FACTOR = _ACCEL_FACTOR / 2


class PlayerBlob(Entity, Circunference, KeyboardHandler):
    def __init__(self, position: Point2F):
        Entity().__init__(name="Player", position=position, velocity=(0, 0))
        Circunference(center=position, radius=_PLAYER_RADIUS, theme=_PLAYER_THEME).__init__(
            center=position, radius=_PLAYER_RADIUS, theme=_PLAYER_THEME
        )
        self.center = position
        self.position = position
        self.radius = _PLAYER_RADIUS
        self.theme = _PLAYER_THEME
        self.velocity = (0, 0)

    ##############
    """MOVEMENT"""
    ##############

    def do_your_thing(self, gravity_accel: float = _PLAYER_GRAVITY) -> None:
        self._apply_gravity(gravity_accel)
        self.handle_keyboard_input()
        self._apply_movement()

    def _move_by(self, vector: Vector2F) -> None:
        self.center = add_tuple(self.center, vector)
        self.position = add_tuple(self.position, vector)

    def _apply_gravity(self, gravity_accel: float) -> None:
        # we float for now
        pass

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

        self._decelerate_if_key_unpressed()

    def _decelerate_if_key_unpressed(self) -> None:
        # TODO: unify?
        if self.velocity[1] > 0 and not self._is_pressed(MovementKeys.UP):
            self.velocity = add_tuple(self.velocity, (0, -_DECEL_FACTOR))
        if self.velocity[1] < 0 and not self._is_pressed(MovementKeys.DOWN):
            self.velocity = add_tuple(self.velocity, (0, _DECEL_FACTOR))
        if self.velocity[0] > 0 and not self._is_pressed(MovementKeys.RIGHT):
            self.velocity = add_tuple(self.velocity, (-_DECEL_FACTOR, 0))
        if self.velocity[0] < 0 and not self._is_pressed(MovementKeys.LEFT):
            self.velocity = add_tuple(self.velocity, (_DECEL_FACTOR, 0))

    # TODO: generalize all these?
    @on_key_press(MovementKeys.UP)
    def _move_up(self) -> None:
        if self.velocity[1] >= _MAX_MOVING_VELOCITY:
            return

        self.velocity = add_tuple(
            self.velocity,
            (0, _ACCEL_FACTOR),
        )

    @on_key_press(MovementKeys.DOWN)
    def _move_down(self) -> None:
        if self.velocity[1] <= -_MAX_MOVING_VELOCITY:
            return

        self.velocity = add_tuple(
            self.velocity,
            (0, -_ACCEL_FACTOR),
        )

    @on_key_press(MovementKeys.LEFT)
    def _move_left(self) -> None:
        if self.velocity[0] <= -_MAX_MOVING_VELOCITY:
            return

        self.velocity = add_tuple(
            self.velocity,
            (-_ACCEL_FACTOR, 0),
        )

    @on_key_press(MovementKeys.RIGHT)
    def _move_right(self) -> None:
        if self.velocity[0] >= _MAX_MOVING_VELOCITY:
            return

        self.velocity = add_tuple(
            self.velocity,
            (_ACCEL_FACTOR, 0),
        )
