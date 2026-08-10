import random
from utils import add_tuple

from constants import (
    ENEMY_MOV_FACTOR,
    Color,
)
from entities.entity import Entity

_BOUNCE_FRAMES = ["_", ",", "o", "O", "o", "O"]
_MIN_BOUNCING_RANDOMNESS = 8
_MAX_BOUNCING_RANDOMNESS = 12

_STANDARD_FRAMES = ["X"]


class Enemy(Entity):
    _orig_character_frames: list[str]

    def __init__(
        self,
        enemy_type: int,
        enemy_speed: float,
        movement_type: tuple[float, float],
        position: tuple[float, float],
        character_frames: list[str] = _STANDARD_FRAMES,
        color: Color = "red",
    ):
        Entity.__init__(self)
        self.enemy_type = enemy_type
        self.enemy_speed = enemy_speed
        self.position = position
        self.movement_type = movement_type
        self.character_frames = character_frames
        self._orig_character_frames = character_frames.copy()
        self.color = color

    def collision(self) -> bool:
        if self.curr_level is None:
            return False

        colliding_x = self.movement_type[0] > 0 and (
            self.x_distance()[0] <= 0 or self.x_distance_neg()[0] <= 0
        )
        colliding_y = self.movement_type[1] > 0 and (
            self.y_distance()[0] <= 0 or self.y_distance_neg()[0] <= 0
        )

        if colliding_x or colliding_y:
            # Just dumbly turn around
            self.enemy_speed *= -1
            return True

        return False

    def movement(self):
        if self.curr_level is None:
            return

        # Bounce enemy
        # TODO: do proper polymorphism
        if self.enemy_type == 2:
            # Go back to original characters after bouncing animation is finished
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
                    (-1)
                    * self.movement_type[0]
                    * (
                        0.1
                        * random.randrange(
                            _MIN_BOUNCING_RANDOMNESS, _MAX_BOUNCING_RANDOMNESS
                        )
                    )
                )
                self.move((0, -0.5))
                self.collision_ls_jump()

        # movement types: 0 = horizontal, 1 = vertical
        # position0 = (
        #     self.position[0]
        #     + self.movement_type[0] * ENEMY_MOV_FACTOR * self.enemy_speed
        # )
        # position1 = (
        #     self.position[1]
        #     + self.movement_type[1] * ENEMY_MOV_FACTOR * self.enemy_speed
        # )
        # self.position = (position0, position1)
        self.move(
            (
                self.movement_type[0] * ENEMY_MOV_FACTOR * self.enemy_speed,
                self.movement_type[1] * ENEMY_MOV_FACTOR * self.enemy_speed,
            )
        )

        self.advance_character_frame()

        self.collision()
