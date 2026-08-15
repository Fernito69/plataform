from typing import TYPE_CHECKING, Optional

from model.keyboard import MovementKeys
from model.player import PlayerStatus
from terminal import is_pressed
from three_d_renderer.constants import PLAYER_3D_MOVING_SPEED
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

    def __init__(self, player_number: int = 1):
        LivingEntity3D.__init__(self, health=100, objVertexes=[])
        self._immune_counter: int = 0
        # self._char_frames = _PLAYER_FRAMES
        # self._default_char_frames = _PLAYER_FRAMES

        self.player_number = player_number
        self.lives: int = 3
        self.points = 0
        # self.theme = Theme(color=_PLAYER_COLOR)
        self.status = PlayerStatus.PLAYING

    def handle_player_input(self):
        ############
        # MOVEMENT #
        ############
        if is_pressed(MovementKeys.UP):
            self._move_by([0, 1 * PLAYER_3D_MOVING_SPEED, 0])

        if is_pressed(MovementKeys.DOWN):
            self._move_by([0, -1 * PLAYER_3D_MOVING_SPEED, 0])

        if is_pressed(MovementKeys.LEFT):
            self._move_by([-1 * PLAYER_3D_MOVING_SPEED, 0, 0])

        if is_pressed(MovementKeys.RIGHT):
            self._move_by([1 * PLAYER_3D_MOVING_SPEED, 0, 0])

        if is_pressed(MovementKeys.FLY_UP):
            self._move_by([0, 0, -1 * PLAYER_3D_MOVING_SPEED])

        if is_pressed(MovementKeys.FLY_DOWN):
            self._move_by([0, 0, 1 * PLAYER_3D_MOVING_SPEED])

    # def do_your_thing(self):
    #     self._apply_gravity()
    #     self._calc_collision()
    #     self._advance_character_frame()

    # # checks collision with everything
    # def _calc_collision(self):
    #     self._collision_enemies()
    #     self._collision_things()
    #     self._collision_jump()

    # # checks collision with everything
    # def _collision_things(self):
    #     if self._curr_level is None:
    #         return

    #     for exit in self._curr_level.exits:
    #         if self.is_same_position(exit):
    #             self.status = PlayerStatus.EXIT

    # # checks collision with enemies
    # def _collision_enemies(self):
    #     if self._curr_level is None:
    #         return

    #     if self._immune_counter > 0:
    #         self.theme.color = Cyan() if self._immune_counter % 2 == 0 else White()
    #         self.theme.bg_color = White() if self._immune_counter % 2 == 0 else None

    #         self._set_char_frames(_PLAYER_FLASHING_FRAMES)
    #         self._immune_counter -= 1
    #         return
    #     elif self._immune_counter == 0 and self._char_frames != _PLAYER_FRAMES:
    #         self._set_char_frames()
    #         self._character_frame_index = 0
    #         self.theme.color = _PLAYER_COLOR

    #     if any(
    #         self.is_same_position(enemy) for enemy in self._curr_level.enemies
    #     ):  # player loses health and gains immunity!
    #         self.health -= 20
    #         self._immune_counter = IMMUNE_TIME

    #         if self.health <= 0:
    #             self.character = "🥴"
    #             self.status = PlayerStatus.DEAD

    # def handle_player_input(self):
    #     ########
    #     # MENU #
    #     ########
    #     if is_pressed(MenuKeys.QUIT):
    #         self.status = PlayerStatus.QUIT

    #     ############
    #     # MOVEMENT #
    #     ############
    #     if is_pressed(MovementKeys.JUMP) and self.y_distance().distance == 0:
    #         self.falling_velocity = -1
    #         self._move_by((0, -1))
    #         self._calc_collision()

    #     # These are a bit dumb, refactor
    #     if is_pressed(MovementKeys.LEFT):
    #         old_position = (self.position[0], self.position[1])
    #         self._move_by((-1, 0))

    #         self._collision_landscape(old_position)
    #         self._calc_collision()

    #     if is_pressed(MovementKeys.RIGHT):
    #         old_position = (self.position[0], self.position[1])
    #         self._move_by((1, 0))

    #         self._collision_landscape(old_position)
    #         self._calc_collision()

    #     if is_pressed(MovementKeys.DOWN):
    #         old_position = (self.position[0], self.position[1])
    #         self._move_by((0, 1))

    #         self._collision_landscape(old_position)
    #         self._calc_collision()

    def set_curr_level(self, level: "Level3D"):
        self._curr_level = level
        self.position = level.player_starting_position
