from typing import TYPE_CHECKING, Optional

from factories.theme import Cyan, Green, White
from model.keyboard import KeyboardKeys, MovementKeys
from model.player import PlayerStatus
from model.theme import Theme
from terminal import on_key_press
from two_dee_renderer.constants import PLAYER_IMMUNE_TIME
from two_dee_renderer.entities.base import LivingEntity2D

if TYPE_CHECKING:
    from two_dee_renderer.level_2d import Level2D

_PLAYER_COLOR = Green()
_PLAYER_FRAMES = ["☺"]
_PLAYER_FLASHING_FRAMES = ["☻"]


class Player2D(LivingEntity2D):
    status: PlayerStatus
    lives: int
    points: int
    player_number: int

    _curr_level: Optional["Level2D"] = None
    _immune_counter: int

    _pressed_key_map: dict[KeyboardKeys, bool] = {}

    def __init__(self, player_number: int):
        LivingEntity2D.__init__(self, health=100)
        self._immune_counter: int = 0
        self._char_frames = _PLAYER_FRAMES
        self._default_char_frames = _PLAYER_FRAMES

        self.player_number = player_number
        self.lives: int = 3
        self.points = 0
        self.theme = Theme(color=_PLAYER_COLOR)
        self.status = PlayerStatus.PLAYING

    def do_your_thing(self):
        self._apply_gravity()
        self._calc_collision()
        self._advance_character_frame()

    # checks collision with everything
    def _calc_collision(self):
        self._collision_enemies()
        self._collision_things()
        self._collision_jump()

    # checks collision with everything
    def _collision_things(self):
        if self._curr_level is None:
            return

        for exit in self._curr_level.exits:
            if self.is_same_position(exit):
                self.status = PlayerStatus.END_LEVEL_2D

    # checks collision with enemies
    def _collision_enemies(self):
        if self._curr_level is None:
            return

        if self._immune_counter > 0:
            self.theme.color = Cyan() if self._immune_counter % 2 == 0 else White()
            self.theme.bg_color = White() if self._immune_counter % 2 == 0 else None

            self._set_char_frames(_PLAYER_FLASHING_FRAMES)
            self._immune_counter -= 1
            return
        elif self._immune_counter == 0 and self._char_frames != _PLAYER_FRAMES:
            self._set_char_frames()
            self._character_frame_index = 0
            self.theme.color = _PLAYER_COLOR

        if any(
            self.is_same_position(enemy) for enemy in self._curr_level.enemies
        ):  # player loses health and gains immunity!
            self.health -= 20
            self._immune_counter = PLAYER_IMMUNE_TIME

            if self.health <= 0:
                self.character = "🥴"
                self.status = PlayerStatus.DEAD

    @on_key_press(MovementKeys.UP)
    def _jump(self) -> None:
        if self.y_distance().distance > 0:
            return
        self.falling_velocity = -1
        self._move_by((0, -1))
        self._calc_collision()

    @on_key_press(MovementKeys.LEFT)
    def _move_left(self) -> None:
        old_position = (self.position[0], self.position[1])
        self._move_by((-1, 0))
        self._collision_landscape(old_position)
        self._calc_collision()

    @on_key_press(MovementKeys.RIGHT)
    def _move_right(self) -> None:
        old_position = (self.position[0], self.position[1])
        self._move_by((1, 0))
        self._collision_landscape(old_position)
        self._calc_collision()

    def handle_player_input(self):
        self._jump()
        self._move_left()
        self._move_right()

    def set_curr_level(self, level: "Level2D"):
        self._curr_level = level
        self.position = level.player_starting_position
