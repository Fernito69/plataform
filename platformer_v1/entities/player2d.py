from typing import TYPE_CHECKING

from factories.theme import Cyan, Green, Red, White, Yellow
from model.base import PointF, VectorF
from model.keyboard import MovementKeys
from model.player import PlayerStatus
from model.shared import KeyboardHandler
from model.theme import Theme
from platformer_v1.constants import PLAYER_IMMUNE_TIME
from platformer_v1.entities.base import LivingEntity2D
from terminal import on_key_press
from utils import colored

if TYPE_CHECKING:
    from platformer_v1.level_2d import Level2D

_PLAYER_COLOR = Green()
_PLAYER_FRAMES = ["☺"]

_PLAYER_IMMUNE_COLOR = Cyan()
_PLAYER_FLASHING_FRAMES = ["☻"]

_GOOD_HEALTH_LIMIT = 75
_BAD_HEALTH_LIMIT = 25

_GOOD_HEALTH_COLOR = Green()
_MID_HEALTH_COLOR = Yellow()
_BAD_HEALTH_COLOR = Red()


class Player2D(KeyboardHandler, LivingEntity2D):
    status: PlayerStatus
    lives: int
    points: int
    player_number: int

    _immune_counter: int

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
        self._do_the_bare_minimum()
        self._apply_gravity()
        self._calc_collision()

    def _calc_collision(self):
        self._collision_enemies()
        self._collision_things()
        self._collision_jump()

    def _collision_things(self):
        if self.curr_level is None:
            return

        for exit in self.curr_level.exits:
            if self.is_same_position(exit):
                self.status = PlayerStatus.END_LEVEL

    def get_health(self) -> str:
        health = str(self.health)

        # TODO: refactor it to go continuously from green, to yellow, to red
        if self.health <= _BAD_HEALTH_LIMIT:
            health = colored(health, _BAD_HEALTH_COLOR)
        elif _BAD_HEALTH_LIMIT < self.health <= _GOOD_HEALTH_LIMIT:
            health = colored(health, _MID_HEALTH_COLOR)
        elif self.health > _GOOD_HEALTH_LIMIT:
            health = colored(health, _GOOD_HEALTH_COLOR)

        return health

    def _collision_enemies(self):
        if self.curr_level is None:
            return

        if self._immune_counter > 0:
            self.theme.color = _PLAYER_IMMUNE_COLOR if self._immune_counter % 2 == 0 else White()
            self.theme.bg_color = White() if self._immune_counter % 2 == 0 else None
            self._set_char_frames(_PLAYER_FLASHING_FRAMES)
            self._immune_counter -= 1
            return
        elif self._immune_counter == 0 and self._char_frames != _PLAYER_FRAMES:
            self._set_char_frames()
            self._character_frame_index = 0
            self.theme.color = _PLAYER_COLOR

        if any(
            self.is_same_position(enemy) for enemy in self.curr_level.enemies
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
        self._move_by(VectorF(0, -1))
        self._calc_collision()

    @on_key_press(MovementKeys.LEFT)
    def _move_left(self) -> None:
        old_position = PointF(self.position.x, self.position.y)
        self._move_by(VectorF(-1, 0))
        self._collision_landscape(old_position)
        self._calc_collision()

    @on_key_press(MovementKeys.RIGHT)
    def _move_right(self) -> None:
        old_position = PointF(self.position.x, self.position.y)
        self._move_by(VectorF(1, 0))
        self._collision_landscape(old_position)
        self._calc_collision()

    def handle_keyboard_input(self):
        self._jump()
        self._move_left()
        self._move_right()

    def set_curr_level(self, level: "Level2D"):
        self.curr_level = level
        self.position = level.player_starting_position
