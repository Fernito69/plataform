import math
from typing import TYPE_CHECKING

from model.base import VectorF
from model.keyboard import MovementKeys
from model.player import PlayerStatus
from model.shared import KeyboardHandler
from terminal import on_key_press
from three_d_renderer.constants import PLAYER_3D_MOVING_SPEED_FACTOR
from three_d_renderer.entities.base3d import LivingEntity3D
from three_d_renderer.scenario.levels_3d import build_3d_levels

if TYPE_CHECKING:
    from three_d_renderer.scenario.level_3d import Level3D


# for now a fixed camera
class Player3D(KeyboardHandler, LivingEntity3D):
    status: PlayerStatus
    lives: int
    points: int
    player_number: int

    curr_level: "Level3D"
    _immune_counter: int

    def __init__(self, player_number: int = 1):
        LivingEntity3D.__init__(self, health=100, vertices=[], angle=VectorF(0, 0, 0))
        self._immune_counter: int = 0
        self.player_number = player_number
        self.lives: int = 3
        self.points = 0
        self.status = PlayerStatus.PLAYING
        self.set_curr_level(build_3d_levels()[0])

    def _normalize_by_angle(self) -> None:
        return

    @on_key_press(MovementKeys.UP)
    def _move_forward(self) -> None:
        # TODO: unify logic "normatlize by angle" ^
        a_x = math.radians(self.angle.x)
        self.move_by(
            VectorF(
                -PLAYER_3D_MOVING_SPEED_FACTOR * math.sin(a_x),
                PLAYER_3D_MOVING_SPEED_FACTOR * math.cos(a_x),
                0,
            )
        )

    @on_key_press(MovementKeys.DOWN)
    def _move_backward(self) -> None:
        a_x = math.radians(self.angle.x)
        self.move_by(
            VectorF(
                PLAYER_3D_MOVING_SPEED_FACTOR * math.sin(a_x),
                -PLAYER_3D_MOVING_SPEED_FACTOR * math.cos(a_x),
                0,
            )
        )

    @on_key_press(MovementKeys.STRAFE_LEFT)
    def _strafe_left(self) -> None:
        a_x = math.radians(self.angle.x)
        self.move_by(
            VectorF(
                -PLAYER_3D_MOVING_SPEED_FACTOR * math.cos(a_x),
                -PLAYER_3D_MOVING_SPEED_FACTOR * math.sin(a_x),
                0,
            )
        )

    @on_key_press(MovementKeys.STRAFE_RIGHT)
    def _strafe_right(self) -> None:
        a_x = math.radians(self.angle.x)
        self.move_by(
            VectorF(
                PLAYER_3D_MOVING_SPEED_FACTOR * math.cos(a_x),
                PLAYER_3D_MOVING_SPEED_FACTOR * math.sin(a_x),
                0,
            )
        )

    @on_key_press(MovementKeys.ROTATE_RIGHT)
    def _rotate_right(self) -> None:
        self.set_angle((self.angle - VectorF(PLAYER_3D_MOVING_SPEED_FACTOR, 0, 0)).as_vector())

    @on_key_press(MovementKeys.ROTATE_LEFT)
    def _rotate_left(self) -> None:
        self.set_angle((self.angle - VectorF(-PLAYER_3D_MOVING_SPEED_FACTOR, 0, 0)).as_vector())

    @on_key_press(MovementKeys.FLY_UP)
    def _fly_up(self) -> None:
        self.move_by(VectorF(0, 0, -1 * PLAYER_3D_MOVING_SPEED_FACTOR))

    @on_key_press(MovementKeys.FLY_DOWN)
    def _fly_down(self) -> None:
        self.move_by(VectorF(0, 0, 1 * PLAYER_3D_MOVING_SPEED_FACTOR))

    def handle_keyboard_input(self):
        self._move_forward()
        self._move_backward()
        self._strafe_left()
        self._strafe_right()
        self._fly_up()
        self._fly_down()
        self._rotate_left()
        self._rotate_right()

    def set_curr_level(self, level: "Level3D"):
        self.curr_level = level
        self.position = level.player_starting_position
