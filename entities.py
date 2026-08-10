"""Game entities: the base Entity, Player, Enemy and Item classes."""
import math
import random
from typing import List, Literal, Optional, TYPE_CHECKING

from constants import (
    Color,
    EMPTY_SPACE,
    ENEMY_MOV_FACTOR,
    GRAVITY_ACCELERATION,
    IMMUNE_TIME,
    X_RESOLUTION,
    Y_RESOLUTION,
    colored,
)
from terminal import is_pressed

if TYPE_CHECKING:
    from level import Level


class Entity:
    curr_level: Optional["Level"] = None
    position: List[int] = (0, 0)
    falling_velocity: float = 0

    character: str = " "
    color: Optional[Color] = None
    bg_color: Optional[Color] = None

    def __init__(self, level: Optional["Level"] = None):
        # x and y coordinates
        self.curr_level = level

    def apply_gravity(self):
        # detemines Y-position and distance to next piece of landscape
        y_dist, y_coor = self.y_distance()

        # moves entity down because of gravity
        if self.position[1] < y_coor - 1 and y_dist > 0:
            curr_vel = math.floor(self.falling_velocity)

            if self.position[1] + curr_vel >= y_coor:
                self.position[1] = y_coor - 1
            else:
                self.position[1] += curr_vel
        else:
            self.falling_velocity = 0

        # increases velocity
        try:
            if y_dist > 0:
                self.falling_velocity += GRAVITY_ACCELERATION
        except Exception as _:
            self.falling_velocity = 0

    def get_char(self):
        return colored(self.character, self.color, self.bg_color)

    # checks collision with landscape elements
    def collision_ls(self, old_pos: List[int]):
        if (
            self.curr_level.map[int(self.position[1])][int(self.position[0])]
            != EMPTY_SPACE
        ):
            self.position = old_pos

    # checks collision with landscape elements
    def collision_ls_jump(self):
        if self.y_distance_neg()[0] == -1:  # and self.gravity <= 0
            self.position[1] = self.y_distance_neg()[1] + 1
            self.falling_velocity = 0

    # calculates Y-axis distance DOWN to landscape
    # checks from current entity position to the bottom of the screen
    def y_distance(self):
        if self.curr_level is None:
            return [1, 1]

        y_dist = -1

        for i in range(math.floor(self.position[1]), Y_RESOLUTION):
            # checks all the way down in player's current X-position
            if self.curr_level.map[i][math.floor(self.position[0])] == EMPTY_SPACE:
                y_dist += 1
            else:
                # returns a list with distance to floor and Y-position of floor
                return [y_dist, i]

    # calculates Y-axis distance UP to landscape
    # checks from current entity position to the upper part of the screen
    def y_distance_neg(self):
        if self.curr_level is None:
            return [-1, -1]

        y_dist_neg = -1
        for i in range(math.floor(self.position[1]), -1, -1):
            # checks all the way up in player's current X-position
            if self.curr_level.map[i][math.floor(self.position[0])] == EMPTY_SPACE:
                y_dist_neg += 1
            else:
                # returns a list with distance to ceiling and Y-position of ceiling
                return [y_dist_neg, i]

    # calculates X-axis distance to landscape to the RIGHT
    # checks from current entity position to the leftmost part of the screen
    def x_distance(self):
        x_dist = -1

        for i in range(math.floor(self.position[0]), X_RESOLUTION):
            # checks all the way to the right in entity's current Y-position
            if self.curr_level.map[math.floor(self.position[1])][i] == EMPTY_SPACE:
                x_dist += 1
            else:
                # returns a list with distance to the right and X-position of the next piece
                return [x_dist, i]

    # calculates X-axis distance to landscape to the LEFT
    # checks from current entity position to the upper part of the screen
    def x_distance_neg(self):
        x_dist_neg = -1
        for i in range(math.floor(self.position[0]), -1, -1):
            # checks all the way to the left in entity's current Y-position
            if self.curr_level.map[math.floor(self.position[1])][i] == EMPTY_SPACE:
                x_dist_neg += 1
            else:
                # returns a list with distance to the left and X-position of the next piece
                return [x_dist_neg, i]

    def set_curr_level(self, level: "Level"):
        self.curr_level = level
        if isinstance(self, Player):
            self.position = level.player_starting_position


class Player(Entity):
    character: str

    curr_level: Optional["Level"] = None
    immune_counter: int = 0

    def __init__(
        self,
        player_number,
        character: str = "☺",
        color: Color = "green",
    ):
        Entity.__init__(self)
        self.player_number = player_number
        self.health = 100
        self.points = 0
        self.lives = 3
        self.character = character
        self.color = color
        self.status: Literal["alive", "dead"] = "alive"

    # checks collision with enemies
    def collision_en(self):
        if self.immune_counter > 0:
            self.color = "cyan" if self.immune_counter % 2 == 0 else "white"
            self.bg_color = "white" if self.immune_counter % 2 == 0 else None
            self.character = "☻"
            self.immune_counter -= 1
            return

        self.character = "☺"
        self.color = "green"

        enemies: List["Enemy"] = self.curr_level.enemies

        for enemy in enemies:
            if self.position == [
                math.floor(enemy.position[0]),
                math.floor(enemy.position[1]),
            ]:  # player loses health and gains immunity!
                self.health -= 20
                self.position = [max(self.position[0] - 1, 0), self.position[1]]
                self.immune_counter = IMMUNE_TIME

                if self.health <= 0:
                    self.character = "🥴"
                    self.status = "dead"

    def player_movement(self):
        if is_pressed("q"):
            return "q"

        if is_pressed("w") and self.y_distance()[0] == 0:
            self.falling_velocity = -1
            self.position[1] -= 1

            self.collision_en()

        if is_pressed("a"):
            old_position = self.position.copy()
            self.position[0] -= 1

            self.collision_ls(old_position)
            self.collision_en()

        if is_pressed("d"):
            old_position = self.position.copy()
            self.position[0] += 1

            self.collision_ls(old_position)
            self.collision_en()

        if is_pressed("s"):
            old_position = self.position.copy()
            self.position[1] += 1

            self.collision_ls(old_position)
            self.collision_en()


class Enemy(Entity):
    _orig_character: str

    def __init__(
        self,
        enemy_type: int,
        enemy_speed: float,
        movement_type: List[int],
        position: List[int],
        character: str = "X",
        color: Color = "red",
    ):
        Entity.__init__(self)
        self.enemy_type = enemy_type
        # how many spaces per second
        self.enemy_speed = enemy_speed
        # position for enemies is a float!
        self.position = position
        self.movement_type = movement_type
        self.character = character
        self._orig_character = character
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

        if self.enemy_type == 2:
            self.character = self._orig_character
            # Has gravity and jumps!
            old_position = self.position.copy()
            self.apply_gravity()
            self.collision_ls(old_position)
            self.collision_ls_jump()

            if self.y_distance()[0] == 0:
                self.character = "_"
                self.falling_velocity = (
                    (-1) * self.movement_type[0] * (0.1 * random.randrange(8, 12))
                )
                self.position[1] -= 0.5
                self.collision_ls_jump()

        # movement types: 0 = horizontal, 1 = vertical
        self.position[0] += self.movement_type[0] * ENEMY_MOV_FACTOR * self.enemy_speed
        self.position[1] += self.movement_type[1] * ENEMY_MOV_FACTOR * self.enemy_speed

        self.collision_enemy()


class Item(Entity):
    def __init__(self, item_type):
        Entity.__init__(self)
        self.item_type = item_type
