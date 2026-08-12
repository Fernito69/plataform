from typing import TYPE_CHECKING, Optional

from constants import IMMUNE_TIME
from entities.entity import LivingEntity
from model.keyboard import KeyCategory, MenuKeys, MovementKeys
from model.player import PlayerStatus
from model.theme import Color, Theme
from terminal import is_pressed

if TYPE_CHECKING:
    from level import Level

_PLAYER_COLOR = "green"
_PLAYER_FRAMES = ["☺"]
_PLAYER_FLASHING_FRAMES = ["☻"]


class Player(LivingEntity):
    curr_level: Optional["Level"] = None
    immune_counter: int
    lives: int
    _character_frames: list[str]
    color: Color
    points: int
    status: PlayerStatus

    def __init__(
        self,
        player_number,
    ):
        LivingEntity.__init__(self, health=100)
        self.player_number = player_number
        self.immune_counter: int = 0
        self.lives: int = 3
        self._character_frames = _PLAYER_FRAMES
        self._default_character_frames = _PLAYER_FRAMES

        self.theme = Theme(color=_PLAYER_COLOR)
        self.points = 0
        self.status = PlayerStatus.ALIVE

    def do_your_thing(self):
        self.apply_gravity()
        self.calc_collision()
        self.advance_character_frame()

    # checks collision with everything
    def calc_collision(self):
        self.collision_enemies()
        self.collision_things()
        self.collision_jump()

    # checks collision with everything
    def collision_things(self):
        if self.curr_level is None:
            return

        for exit in self.curr_level.exits:
            if self.is_same_position(exit):
                self.status = PlayerStatus.EXIT

    # checks collision with enemies
    def collision_enemies(self):
        if self.curr_level is None:
            return

        if self.immune_counter > 0:
            self.theme.color = "cyan" if self.immune_counter % 2 == 0 else "white"
            self.theme.bg_color = "white" if self.immune_counter % 2 == 0 else None

            self.set_char_frames(_PLAYER_FLASHING_FRAMES)
            self.immune_counter -= 1
            return
        elif self.immune_counter == 0 and self._character_frames != _PLAYER_FRAMES:
            self.set_char_frames()
            self._character_frame_index = 0
            self.theme.color = _PLAYER_COLOR

        if any(
            self.is_same_position(enemy) for enemy in self.curr_level.enemies
        ):  # player loses health and gains immunity!
            self.health -= 20
            self.immune_counter = IMMUNE_TIME

            if self.health <= 0:
                self.character = "🥴"
                self.status = PlayerStatus.DEAD

    def player_input(self):
        ########
        # MENU #
        ########
        if is_pressed(KeyCategory.MENU, MenuKeys.QUIT):
            self.status = PlayerStatus.QUIT

        ############
        # MOVEMENT #
        ############
        if (
            is_pressed(KeyCategory.MOVEMENT, MovementKeys.JUMP)
            and self.y_distance()[0] == 0
        ):
            self.falling_velocity = -1
            self.move_to((0, -1))

            self.calc_collision()

        # These are a bit dumb, refactor
        if is_pressed(KeyCategory.MOVEMENT, MovementKeys.LEFT):
            old_position = (self.position[0], self.position[1])
            self.move_to((-1, 0))

            self.collision_landscape(old_position)
            self.calc_collision()

        if is_pressed(KeyCategory.MOVEMENT, MovementKeys.RIGHT):
            old_position = (self.position[0], self.position[1])
            self.move_to((1, 0))

            self.collision_landscape(old_position)
            self.calc_collision()

        if is_pressed(KeyCategory.MOVEMENT, MovementKeys.DOWN):
            old_position = (self.position[0], self.position[1])
            self.move_to((0, 1))

            self.collision_landscape(old_position)
            self.calc_collision()

    def set_curr_level(self, level: "Level"):
        self.curr_level = level
        self.position = level.player_starting_position
