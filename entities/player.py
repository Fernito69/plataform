"""Game entities: the base Entity, Player, Enemy and Item classes."""

import math
from model.keyboard import KeyCategory, MenuKeys, MovementKeys
from typing import TYPE_CHECKING, Literal, Optional

from constants import (
    IMMUNE_TIME,
    Color,
)
from entities.entity import Entity
from terminal import is_pressed

if TYPE_CHECKING:
    from entities.enemy import Enemy
    from level import Level


class Player(Entity):
    curr_level: Optional["Level"] = None
    immune_counter: int = 0

    def __init__(
        self,
        player_number,
        character_frames: list[str] | None = None,
        color: Color = "green",
    ):
        Entity.__init__(self)
        self.player_number = player_number
        self.health = 100
        self.points = 0
        self.lives = 3
        self.character_frames = character_frames or ["☺"]
        self.color = color
        self.status: Literal["alive", "dead", "quit"] = "alive"

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
        self.color = "green"

        enemies: list[Enemy] = self.curr_level.enemies

        for enemy in enemies:
            if self.position == (
                math.floor(enemy.position[0]),
                math.floor(enemy.position[1]),
            ):  # player loses health and gains immunity!
                self.health -= 20
                self.position = (max(self.position[0] - 1, 0), self.position[1])
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

        ########
        # MENU #
        ########
        if (
            is_pressed(KeyCategory.MOVEMENT, MovementKeys.JUMP)
            and self.y_distance()[0] == 0
        ):
            self.falling_velocity = -1
            self.position = (self.position[0], self.position[1] - 1)

            self.collision_en()

        if is_pressed(KeyCategory.MOVEMENT, MovementKeys.LEFT):
            old_position = (self.position[0], self.position[1])
            self.position = (self.position[0] - 1, self.position[1])

            self.collision_ls(old_position)
            self.collision_en()

        if is_pressed(KeyCategory.MOVEMENT, MovementKeys.RIGHT):
            old_position = (self.position[0], self.position[1])
            self.position = (self.position[0] + 1, self.position[1])

            self.collision_ls(old_position)
            self.collision_en()

        if is_pressed(KeyCategory.MOVEMENT, MovementKeys.DOWN):
            old_position = (self.position[0], self.position[1])
            self.position = (self.position[0], self.position[1] + 1)

            self.collision_ls(old_position)
            self.collision_en()

    def set_curr_level(self, level: "Level"):
        self.curr_level = level
        self.position = level.player_starting_position
