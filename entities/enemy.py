import math
import random
from typing import Literal, TYPE_CHECKING, Optional
from entities.entity import Entity


from constants import (
    Color,
    EMPTY_SPACE,
    ENEMY_MOV_FACTOR,
    GRAVITY_ACCELERATION,
    IMMUNE_TIME,
    X_RESOLUTION,
    Y_RESOLUTION,
)


class Enemy(Entity):
    _orig_character_frames: list[str]

    def __init__(
        self,
        enemy_type: int,
        enemy_speed: float,
        movement_type: tuple[float, float],
        position: tuple[float, float],
        character_frames: list[str] | None = None,
        color: Color = "red",
    ):
        Entity.__init__(self)
        self.enemy_type = enemy_type
        # how many spaces per second
        self.enemy_speed = enemy_speed
        # position for enemies is a float!
        self.position = position
        self.movement_type = movement_type
        self.character_frames = character_frames or ["X"]
        self._orig_character_frames = (
            character_frames.copy() if character_frames else ["X"]
        )
        self.color = color

    def collision_enemy(self) -> bool:
        if self.curr_level is None:
            return False

        if self.movement_type[0] > 0 and (
            self.x_distance()[0] <= 0 or self.x_distance_neg()[0] <= 0
        ):
            self.enemy_speed *= -1

        if self.movement_type[1] > 0 and (
            self.y_distance()[0] <= 0 or self.y_distance_neg()[0] <= 0
        ):
            self.enemy_speed *= -1

        return False

    def movement(self):
        if self.curr_level is None:
            return

        # Bounce enemy
        if self.enemy_type == 2:
            # TODO: do proper polymorphism
            _BOUNCE_FRAMES = ["O", "o", "_", "o", "O"]

            # Go back to original characters
            if (
                self.character_frames == _BOUNCE_FRAMES
                and self.character_frame_index == len(_BOUNCE_FRAMES) - 1
            ):
                self.character_frames = self._orig_character_frames
                self.character_frame_index = 0

            # Has gravity and jumps!
            old_position = (self.position[0], self.position[1])
            self.apply_gravity()
            self.collision_ls(old_position)
            self.collision_ls_jump()

            if self.y_distance()[0] == 0:
                self.character_frames = _BOUNCE_FRAMES
                self.character_frame_index = 0
                self.falling_velocity = (
                    (-1) * self.movement_type[0] * (0.1 * random.randrange(8, 12))
                )
                self.position = (self.position[0], self.position[1] - 0.5)
                self.collision_ls_jump()

        # movement types: 0 = horizontal, 1 = vertical
        position0 = (
            self.position[0]
            + self.movement_type[0] * ENEMY_MOV_FACTOR * self.enemy_speed
        )
        position1 = (
            self.position[1]
            + self.movement_type[1] * ENEMY_MOV_FACTOR * self.enemy_speed
        )
        self.position = (position0, position1)

        # Advance character frame
        self.character_frame_index = (
            self.character_frame_index + 1
            if self.character_frame_index < len(self.character_frames) - 1
            else 0
        )

        self.collision_enemy()
