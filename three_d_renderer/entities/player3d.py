from typing import TYPE_CHECKING, Optional

from model.keyboard import KeyboardKeys, MovementKeys
from model.player import PlayerStatus
from terminal import on_key_press
from three_d_renderer.constants import PLAYER_3D_MOVING_SPEED_FACTOR
from three_d_renderer.entities.base3d import LivingEntity3D

if TYPE_CHECKING:
    from three_d_renderer.scenario.level_3d import Level3D


# for now a fixed camera
class Player3D(LivingEntity3D):
    status: PlayerStatus
    lives: int
    points: int
    player_number: int

    _curr_level: Optional["Level3D"] = None
    _immune_counter: int

    _pressed_key_map: dict[KeyboardKeys, bool] = {}

    def __init__(self, player_number: int = 1):
        LivingEntity3D.__init__(self, health=100, vertices=[])
        self._immune_counter: int = 0
        self.player_number = player_number
        self.lives: int = 3
        self.points = 0
        self.status = PlayerStatus.PLAYING

    @on_key_press(MovementKeys.UP)
    def _move_forward(self) -> None:
        self._move_by([0, 1 * PLAYER_3D_MOVING_SPEED_FACTOR, 0])

    @on_key_press(MovementKeys.DOWN)
    def _move_backward(self) -> None:
        self._move_by([0, -1 * PLAYER_3D_MOVING_SPEED_FACTOR, 0])

    @on_key_press(MovementKeys.LEFT)
    def _strafe_left(self) -> None:
        self._move_by([-1 * PLAYER_3D_MOVING_SPEED_FACTOR, 0, 0])

    @on_key_press(MovementKeys.RIGHT)
    def _strafe_right(self) -> None:
        self._move_by([1 * PLAYER_3D_MOVING_SPEED_FACTOR, 0, 0])

    @on_key_press(MovementKeys.FLY_UP)
    def _fly_up(self) -> None:
        self._move_by([0, 0, -1 * PLAYER_3D_MOVING_SPEED_FACTOR])

    @on_key_press(MovementKeys.FLY_DOWN)
    def _fly_down(self) -> None:
        self._move_by([0, 0, 1 * PLAYER_3D_MOVING_SPEED_FACTOR])

    def handle_player_input(self):
        self._move_forward()
        self._move_backward()
        self._strafe_left()
        self._strafe_right()
        self._fly_up()
        self._fly_down()

    def set_curr_level(self, level: "Level3D"):
        self._curr_level = level
        self.position = level.player_starting_position
