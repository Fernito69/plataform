"""Game entities: the base Entity, Player, Enemy and Item classes."""

import math
from typing import TYPE_CHECKING, Optional

from constants import (
    EMPTY_SPACE,
    GRAVITY_ACCELERATION,
    X_RESOLUTION,
    Y_RESOLUTION,
    Color,
)
from utils import add_tuple, colored

if TYPE_CHECKING:
    from level import Level


class Entity:
    curr_level: Optional["Level"] = None
    position: tuple[float, float] = (0, 0)
    falling_velocity: float = 0

    character_frames: list[str]
    character_frame_index: int

    color: Color | None = None
    bg_color: Color | None = None

    def __init__(self, level: Optional["Level"] = None):
        # x and y coordinates
        self.curr_level = level
        self.character_frames = [EMPTY_SPACE]
        self.character_frame_index = 0

    def advance_character_frame(self):
        self.character_frame_index = (
            self.character_frame_index + 1
            if self.character_frame_index < len(self.character_frames) - 1
            else 0
        )

    def apply_gravity(self):
        # detemines Y-position and distance to next piece of landscape
        y_dist, y_coor = self.y_distance()

        # moves entity down because of gravity
        if self.position[1] < y_coor - 1 and y_dist > 0:
            # TODO: check if we only need math.floor in the second part
            new_y = (
                y_coor - 1
                if self.position[1] + self.falling_velocity >= y_coor
                else self.position[1] + math.floor(self.falling_velocity)
            )

            self.position = (self.position[0], new_y)
        else:
            self.falling_velocity = 0

        # increases velocity
        if y_dist > 0:
            self.falling_velocity += GRAVITY_ACCELERATION
        # IS THIS NECESSARY?
        # else:
        #     self.falling_velocity = 0

    def get_char(self):
        return colored(
            self.character_frames[self.character_frame_index], self.color, self.bg_color
        )

    def move(self, vector: tuple[int | float, int | float]):
        self.position = add_tuple(self.position, vector)

    def is_same_position(self, entity: "Entity"):
        a = self.position
        b = entity.position

        # Should this be math.floor or math.round?
        return round(a[0]) == round(b[0]) and round(a[1]) == round(b[1])
        # return math.floor(a[0]) == math.floor(b[0]) and math.floor(a[1]) == math.floor(
        #     b[1]
        # )

    # checks collision with landscape elements
    def collision_ls(self, old_pos: tuple[float, float]):
        if (
            self.curr_level
            and self.curr_level.map[int(self.position[1])][int(self.position[0])]
            != EMPTY_SPACE
        ):
            self.position = old_pos

    # checks collision with landscape elements
    def collision_ls_jump(self):
        if self.y_distance_neg()[0] == -1:  # and self.gravity <= 0
            self.position = (self.position[0], self.y_distance_neg()[1] + 1)
            self.falling_velocity = 0

    # calculates Y-axis distance DOWN to landscape
    # checks from current entity position to the bottom of the screen

    # TODO: all of these methods are dumb as fuck, REFACTOR!
    def y_distance(self) -> tuple[int, int]:
        if self.curr_level is None:
            return (1, 1)

        y_dist = -1

        for i in range(math.floor(self.position[1]), Y_RESOLUTION):
            # checks all the way down in player's current X-position
            if self.curr_level.map[i][math.floor(self.position[0])] == EMPTY_SPACE:
                y_dist += 1
            else:
                # returns a list with distance to floor and Y-position of floor
                return (y_dist, i)

        return (0, 0)

    # calculates Y-axis distance UP to landscape
    # checks from current entity position to the upper part of the screen
    def y_distance_neg(self) -> tuple[int, int]:
        if self.curr_level is None:
            return (1, -1)

        y_dist_neg = -1
        for i in range(math.floor(self.position[1]), -1, -1):
            # checks all the way up in player's current X-position
            if self.curr_level.map[i][math.floor(self.position[0])] == EMPTY_SPACE:
                y_dist_neg += 1
            else:
                # returns a list with distance to ceiling and Y-position of ceiling
                return (y_dist_neg, i)

        return (0, 0)

    # calculates X-axis distance to landscape to the RIGHT
    # checks from current entity position to the leftmost part of the screen
    def x_distance(self) -> tuple[int, int]:
        if self.curr_level is None:
            return (0, 0)

        x_dist = -1

        for i in range(math.floor(self.position[0]), X_RESOLUTION):
            # checks all the way to the right in entity's current Y-position
            if self.curr_level.map[math.floor(self.position[1])][i] == EMPTY_SPACE:
                x_dist += 1
            else:
                # returns a list with distance to the right and X-position of the next piece
                return (x_dist, i)

        return (0, 0)

    # calculates X-axis distance to landscape to the LEFT
    # checks from current entity position to the upper part of the screen
    def x_distance_neg(self) -> tuple[int, int]:
        if self.curr_level is None:
            return (0, 0)

        x_dist_neg = -1
        for i in range(math.floor(self.position[0]), -1, -1):
            # checks all the way to the left in entity's current Y-position
            if self.curr_level.map[math.floor(self.position[1])][i] == EMPTY_SPACE:
                x_dist_neg += 1
            else:
                # returns a list with distance to the left and X-position of the next piece
                return (x_dist_neg, i)

        return (0, 0)

    def set_curr_level(self, level: "Level"):
        self.curr_level = level
