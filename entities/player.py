from typing import TYPE_CHECKING, Literal, Optional

from constants import IMMUNE_TIME, Color
from entities.entity import Entity
from model.keyboard import KeyCategory, MenuKeys, MovementKeys
from terminal import is_pressed

if TYPE_CHECKING:
    from level import Level

_PLAYER_COLOR = "green"
_PLAYER_FRAMES = ["☺"]


class Player(Entity):
    curr_level: Optional["Level"] = None
    immune_counter: int = 0

    def __init__(
        self,
        player_number,
        character_frames: list[str] = _PLAYER_FRAMES,
        color: Color = _PLAYER_COLOR,
    ):
        Entity.__init__(self)
        self.player_number = player_number
        self.health = 100
        self.points = 0
        self.lives = 3
        self.character_frames = character_frames
        self.color = color
        # TODO: make an enum
        self.status: Literal["alive", "dead", "quit", "exit"] = "alive"

    # checks collision with everything
    def collision(self):
        self.collision_en()
        self.collision_things()

    # checks collision with everything
    def collision_things(self):
        if self.curr_level is None:
            return

        for exit in self.curr_level.exits:
            if self.is_same_position(exit):
                self.status = "exit"

    # checks collision with enemies
    def collision_en(self):
        if self.curr_level is None:
            return

        if self.immune_counter > 0:
            self.color = "cyan" if self.immune_counter % 2 == 0 else "white"
            self.bg_color = "white" if self.immune_counter % 2 == 0 else None
            self.character = "☻"
            self.immune_counter -= 1
            return

        self.character = "☺"
        self.color = _PLAYER_COLOR

        if any(
            self.is_same_position(enemy) for enemy in self.curr_level.enemies
        ):  # player loses health and gains immunity!
            self.health -= 20
            self.immune_counter = IMMUNE_TIME

            if self.health <= 0:
                self.character = "🥴"
                self.status = "dead"

    def player_movement(self):
        ########
        # MENU #
        ########
        if is_pressed(KeyCategory.MENU, MenuKeys.QUIT):
            self.status = "quit"

        ############
        # MOVEMENT #
        ############
        if (
            is_pressed(KeyCategory.MOVEMENT, MovementKeys.JUMP)
            and self.y_distance()[0] == 0
        ):
            self.falling_velocity = -1
            self.move((0, -1))

            self.collision()

        if is_pressed(KeyCategory.MOVEMENT, MovementKeys.LEFT):
            old_position = (self.position[0], self.position[1])
            self.move((-1, 0))

            self.collision_ls(old_position)
            self.collision()

        if is_pressed(KeyCategory.MOVEMENT, MovementKeys.RIGHT):
            old_position = (self.position[0], self.position[1])
            self.move((1, 0))

            self.collision_ls(old_position)
            self.collision()

        if is_pressed(KeyCategory.MOVEMENT, MovementKeys.DOWN):
            old_position = (self.position[0], self.position[1])
            self.move((0, 1))

            self.collision_ls(old_position)
            self.collision()

    def set_curr_level(self, level: "Level"):
        self.curr_level = level
        self.position = level.player_starting_position
