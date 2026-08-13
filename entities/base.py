import math
from typing import TYPE_CHECKING, Optional

from constants import (
    EMPTY_SPACE,
    GRAVITY_ACCELERATION,
    X_RESOLUTION_2D,
    Y_RESOLUTION_2D,
)
from model.entity import Collision2X, Collision2Y
from model.shared import Coord2, Orientation, Vector2
from model.theme import Theme
from utils import add_tuple, colored

if TYPE_CHECKING:
    from level2d import Level2D


# TODO: rename methods properly
# TODO: reuse the Theme types as animation types for _char frames and reuse the method to make level architecture for the change of  indices
class Entity2D:
    _curr_level: Optional["Level2D"] = None
    position: tuple[float, float] = (0, 0)
    falling_velocity: float = 0

    # 1 frame, static charater.
    # >1 frames, animated!
    _char_frames: list[str]
    _default_char_frames: list[str]
    _curr_char_frame_index: int

    theme: Theme

    def __init__(self, level: Optional["Level2D"] = None, theme: Theme | None = None):
        # x and y coordinates
        self._curr_level = level
        self._char_frames = [EMPTY_SPACE]
        self._default_char_frames = [EMPTY_SPACE]
        self._curr_char_frame_index = 0
        self.theme = theme or Theme()

    def _advance_character_frame(self) -> None:
        if len(self._default_char_frames) == 0:
            return

        self._curr_char_frame_index = (
            self._curr_char_frame_index + 1
            if self._curr_char_frame_index < len(self._char_frames) - 1
            else 0
        )

    def _set_char_frames(self, new_char_frames: list[str] | None = None) -> None:
        self._curr_char_frame_index = 0
        self._char_frames = new_char_frames or self._default_char_frames

    def _apply_gravity(self) -> None:
        y_dist = self.y_distance().distance
        y_coor = self.y_distance().y_at_target

        if y_coor is None:
            return

        # moves entity down because of gravity
        if self.position[1] < y_coor - 1 and y_dist > 0:
            # TODO: check if we only need math.floor in the second part
            # TODO: I don't understand this code, wtf is the if condition?
            new_y = (
                y_coor - 1
                if self.position[1] + self.falling_velocity >= y_coor
                else self.position[1] + math.floor(self.falling_velocity)
            )

            self.position = (self.position[0], new_y)
        else:
            self.falling_velocity = 0

        if y_dist > 0:
            self.falling_velocity += GRAVITY_ACCELERATION

    def get_char(self) -> str:
        return colored(
            self._char_frames[self._curr_char_frame_index],
            self.theme.color,
            self.theme.bg_color,
        )

    def do_your_thing(self) -> None:
        # This method should be overwritten by the inheriting classes
        pass

    # TODO: this should calculate player collision before moving ()
    def _move_by(self, vector: Vector2) -> None:
        self.position = add_tuple(self.position, vector)

    def is_same_position(self, entity: "Entity2D") -> bool:
        a = self.position
        b = entity.position

        return round(a[0]) == round(b[0]) and round(a[1]) == round(b[1])

    # checks collision with landscape elements
    def _collision_landscape(self, old_pos: Coord2) -> None:
        if (
            self._curr_level
            and self._curr_level.map[int(self.position[1])][int(self.position[0])]
            != EMPTY_SPACE
        ):
            self.position = old_pos

    # checks collision with landscape elements
    def _collision_jump(self) -> None:
        if self.y_distance_neg().distance == -1:
            self.position = (self.position[0], self.y_distance_neg().y_at_target + 1)
            self.falling_velocity = 0

    # calculates Y-axis distance DOWN to landscape
    # checks from current entity position to the bottom of the screen

    # TODO: all of these methods are dumb as fuck, REFACTOR!
    # TODO: all these tuples should be data classes

    # calculates Y-axis distance DOWN to landscape
    def y_distance(self) -> Collision2Y:
        if self._curr_level is None:
            return Collision2Y()

        y_dist = -1

        for i in range(math.floor(self.position[1]), Y_RESOLUTION_2D):
            # checks all the way down in player's current X-position
            if self._curr_level.map[i][math.floor(self.position[0])] == EMPTY_SPACE:
                y_dist += 1
            else:
                return Collision2Y(
                    y_at_target=i,
                    distance=y_dist,
                    orientation=Orientation.VERTICAL,
                )

        return Collision2Y()

    # calculates Y-axis distance UP to landscape
    # checks from current entity position to the upper part of the screen
    def y_distance_neg(self) -> Collision2Y:
        if self._curr_level is None:
            return Collision2Y()

        y_dist_neg = -1
        for i in range(math.floor(self.position[1]), -1, -1):
            # checks all the way up in player's current X-position
            if self._curr_level.map[i][math.floor(self.position[0])] == EMPTY_SPACE:
                y_dist_neg += 1
            else:
                return Collision2Y(
                    y_at_target=i,
                    distance=y_dist_neg,
                    orientation=Orientation.VERTICAL,
                )

        return Collision2Y()

    # calculates X-axis distance to landscape to the RIGHT
    # checks from current entity position to the leftmost part of the screen
    def x_distance(self) -> Collision2X:
        if self._curr_level is None:
            return Collision2X()

        x_dist = -1

        for i in range(math.floor(self.position[0]), X_RESOLUTION_2D):
            # checks all the way to the right in entity's current Y-position
            if self._curr_level.map[math.floor(self.position[1])][i] == EMPTY_SPACE:
                x_dist += 1
            else:
                return Collision2X(
                    distance=x_dist,
                    x_at_target=i,
                    orientation=Orientation.HORIZONTAL,
                )

        return Collision2X()

    # calculates X-axis distance to landscape to the LEFT
    # checks from current entity position to the upper part of the screen
    def x_distance_neg(self) -> Collision2X:
        if self._curr_level is None:
            return Collision2X()

        x_dist_neg = -1
        for i in range(math.floor(self.position[0]), -1, -1):
            # checks all the way to the left in entity's current Y-position
            if self._curr_level.map[math.floor(self.position[1])][i] == EMPTY_SPACE:
                x_dist_neg += 1
            else:
                return Collision2X(
                    distance=x_dist_neg,
                    x_at_target=i,
                    orientation=Orientation.HORIZONTAL,
                )

        return Collision2X()

    def set_curr_level(self, level: "Level2D"):
        self._curr_level = level


class LivingEntity2D(Entity2D):
    health: int

    def __init__(self, health: int):
        Entity2D.__init__(self)
        self.health = health
