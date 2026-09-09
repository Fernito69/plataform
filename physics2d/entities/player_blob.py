from typing import TYPE_CHECKING

from model.base import PointF, VectorF
from model.keyboard import ActionKeys, MovementKeys
from model.shared import KeyboardHandler
from model.theme import RGB, Theme
from physics2d.entities.base import PhyEntity
from physics2d.entities.equipment.thruster import (
    PlasmaBallThruster,
    MeteorThruster,
    SoapyThruster,
    SonicThruster,
    Thruster,
)
from physics2d.shapes.circunference import Circunference
from terminal import on_key_press

if TYPE_CHECKING:
    from physics2d.physics2d import Physics2D
    from physics2d.scenario.scenario import Scenario

_PLAYER_RADIUS = 4

_PLAYER_THEME = Theme(color=RGB(122, 23, 255))
_PLAYER_GRAVITY = 0  # we float freely!

# _MAX_MOVING_VELOCITY = 7

_MIN_PLAYER_DISTANCE_TO_SCREEN_BORDER = 20


class PlayerBlob(PhyEntity, Circunference, KeyboardHandler):
    _thrusters: list[Thruster]
    _curr_thruster_index: int

    def __init__(
        self,
        engine: "Physics2D",
        position: PointF = PointF(200, 200),
        velocity=VectorF(0, 0),
        density: float = 1,
    ):
        Circunference.__init__(
            self,
            center=position,
            radius=_PLAYER_RADIUS,
            theme=_PLAYER_THEME,
        )
        PhyEntity.__init__(
            self,
            name="PlayerBlob",
            position=position,
            velocity=velocity,
            density=density,
            volume=self.volume,
        )
        self.engine = engine
        self.center = position
        self.position = position
        self.radius = _PLAYER_RADIUS
        self.theme = _PLAYER_THEME
        self.velocity = VectorF(0, 0)
        self.is_collideable = True
        self.name = "PlayerBlob"

    ##############
    """MOVEMENT"""
    ##############

    def do_your_thing(self) -> None:
        self._get_curr_thruster().handle_particles()

        self.handle_keyboard_input()
        self._apply_gravity(self.engine.scenario.gravity_acceleration)
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
        # only solid pieces can interact with the player
        # TODO: we should filter by those that are visible on ecreen
        for piece in self.engine.scenario.solid_pieces:
            self.would_collide_with(piece, self.engine)

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
        self._switch_thruster()
        self._move_up()
        self._move_left()
        self._move_right()
        self._move_down()

        self._decelerate_if_not_pressing()

        # TODO: fix this
        # if abs(self.velocity) >= _MAX_MOVING_VELOCITY:
        #     return

    def _decelerate_if_not_pressing(self) -> None:
        _decel_amount = self._get_decel()
        _max_speed = self._get_max_speed()
        if (
            self.velocity.y > 0 and not self._is_pressed(MovementKeys.UP)
        ) or self.velocity.y > _max_speed:
            self.velocity = (
                self.velocity + VectorF(0, -min(_decel_amount, self.velocity.y))
            ).as_vector()
        if (
            self.velocity.y < 0 and not self._is_pressed(MovementKeys.DOWN)
        ) or self.velocity.y < -_max_speed:
            self.velocity = (
                self.velocity + VectorF(0, max(_decel_amount, self.velocity.y))
            ).as_vector()
        if (
            self.velocity.x > 0 and not self._is_pressed(MovementKeys.RIGHT)
        ) or self.velocity.x > _max_speed:
            self.velocity = (
                self.velocity + VectorF(-min(_decel_amount, self.velocity.x), 0)
            ).as_vector()
        if (
            self.velocity.x < 0 and not self._is_pressed(MovementKeys.LEFT)
        ) or self.velocity.x < -_max_speed:
            self.velocity = (
                self.velocity + VectorF(max(_decel_amount, self.velocity.x), 0)
            ).as_vector()

    @on_key_press(ActionKeys.SWITCH_THRUSTER, act_once_per_press=True)
    def _switch_thruster(self) -> None:
        self._curr_thruster_index = (
            self._curr_thruster_index + 1
            if len(self._thrusters) > self._curr_thruster_index + 1
            else 0
        )
        self.theme = self._get_curr_thruster().player_theme

    @on_key_press(MovementKeys.UP)
    def _move_up(self) -> None:
        if self.velocity.y >= self._get_max_speed():
            return

        self.velocity = (self.velocity + VectorF(0, self._get_accel())).as_vector()

    @on_key_press(MovementKeys.DOWN)
    def _move_down(self) -> None:
        if self.velocity.y <= -self._get_max_speed():
            return

        self.velocity = (self.velocity + VectorF(0, -self._get_accel())).as_vector()

    @on_key_press(MovementKeys.LEFT)
    def _move_left(self) -> None:
        if self.velocity.x <= -self._get_max_speed():
            return

        self.velocity = (self.velocity + VectorF(-self._get_accel(), 0)).as_vector()

    @on_key_press(MovementKeys.RIGHT)
    def _move_right(self) -> None:
        if self.velocity.x >= self._get_max_speed():
            return

        self.velocity = (self.velocity + VectorF(self._get_accel(), 0)).as_vector()

    def _get_curr_thruster(self) -> Thruster:
        return self._thrusters[self._curr_thruster_index]

    def _get_max_speed(self) -> float:
        return self._get_curr_thruster().max_speed

    def _get_accel(self) -> float:
        return self._get_curr_thruster().accel

    def _get_decel(self) -> float:
        return self._get_curr_thruster().decel

    def set_scenario(self, scenario: "Scenario") -> None:
        self._scenario = scenario
        self._thrusters = [
            MeteorThruster(self.engine.scenario),
            SoapyThruster(self.engine.scenario),
            SonicThruster(self.engine.scenario),
            PlasmaBallThruster(self.engine.scenario),
        ]
        self._curr_thruster_index = 0
        self.theme = self._get_curr_thruster().player_theme
