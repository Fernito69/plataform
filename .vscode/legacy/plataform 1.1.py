# imports
import os
import time
import math
from typing import Literal, List, Optional

import platform
import random


# USEFUL CONSTS
_EMPTY_SPACE = " "
_UL = "╔"
_UR = "╗"
_LL = "╚"
_LR = "╝"
_H = "═"
_V = "║"
_CR = "╠"
_CL = "╣"
_CD = "╦"
_CU = "╩"
_CA = "╬"

IMMUNE_TIME = 30
GRAVITY_ACCELERATION = 0.3
ENEMY_MOV_FACTOR = 0.1

Color = Literal[
    "black",
    "red",
    "green",
    "yellow",
    "blue",
    "magenta",
    "cyan",
    "white",
]

COLOR_CODES = {
    "black": "\033[30m",
    "red": "\033[31m",
    "green": "\033[32m",
    "yellow": "\033[33m",
    "blue": "\033[34m",
    "magenta": "\033[35m",
    "cyan": "\033[36m",
    "white": "\033[37m",
}

BG_COLOR_CODES = {
    "black": "\033[40m",
    "red": "\033[41m",
    "green": "\033[42m",
    "yellow": "\033[43m",
    "blue": "\033[44m",
    "magenta": "\033[45m",
    "cyan": "\033[46m",
    "white": "\033[47m",
}

RESET = "\033[0m"


def colored(text: str, color: Color = "red", bg_color: Optional[Color] = None) -> str:
    bg_code = BG_COLOR_CODES[bg_color] if bg_color else ""
    return f"{COLOR_CODES[color]}{bg_code}{text}{RESET}"


if platform.system() == "Windows":
    import ctypes

    def is_pressed(key):
        return ctypes.windll.user32.GetAsyncKeyState(ord(key.upper())) & 0x8000
else:
    from pynput import keyboard as _pynput_keyboard

    _pressed_keys = set()

    def _on_press(key):
        try:
            _pressed_keys.add(key.char.lower())
        except AttributeError:
            pass

    def _on_release(key):
        try:
            _pressed_keys.discard(key.char.lower())
        except AttributeError:
            pass

    _listener = _pynput_keyboard.Listener(on_press=_on_press, on_release=_on_release)
    _listener.daemon = True
    _listener.start()

    def is_pressed(key):
        return key.lower() in _pressed_keys


if os.name == "nt":
    import msvcrt

    def get_key():
        if not msvcrt.kbhit():
            return None

        # getwch() returns a Unicode character, so decoding isn't needed.
        key = msvcrt.getwch()

        # Arrow and other special keys return a two-character sequence.
        if key in ("\x00", "\xe0"):
            special_key = msvcrt.getwch()

            # WASD controls.
            return {
                "H": "w",  # Up
                "P": "s",  # Down
                "K": "a",  # Left
                "M": "d",  # Right
            }.get(special_key)

        return key.lower()


def clear():
    os.system("cls" if os.name == "nt" else "clear")


clear()


# a cuántos FPS  corre el juego
fps = 30

x_resolution: int = 80
y_resolution: int = 25


# ALL GAME ENTITIES
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
            != _EMPTY_SPACE
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

        for i in range(math.floor(self.position[1]), y_resolution):
            # checks all the way down in player's current X-position
            if self.curr_level.map[i][math.floor(self.position[0])] == _EMPTY_SPACE:
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
        # print(str(y_resolution) + ", " + str(self.position[1]))
        for i in range(math.floor(self.position[1]), -1, -1):
            # checks all the way up in player's current X-position
            if self.curr_level.map[i][math.floor(self.position[0])] == _EMPTY_SPACE:
                y_dist_neg += 1
            else:
                # returs a list with distance to ceiling and Y-position of ceiling
                return [
                    y_dist_neg,
                    i,
                ]  # <--- tengo que encontrar la posición de la pieza ql

    # calculates X-axis distance to landscape to the RIGHT
    # checks from current entity position to the leftmost part of the screen
    def x_distance(self):
        x_dist = -1

        for i in range(math.floor(self.position[0]), x_resolution):
            # checks all the way to the right in entity's current Y-position
            if self.curr_level.map[math.floor(self.position[1])][i] == _EMPTY_SPACE:
                x_dist += 1
            else:
                # returns a list with distance to the right and X-position of the next piece
                return [x_dist, i]

    # calculates X-axis distance to landscape to the LEFT
    # checks from current entity position to the upper part of the screen
    def x_distance_neg(self):
        x_dist_neg = -1
        # print(str(y_resolution) + ", " + str(self.position[1]))
        for i in range(math.floor(self.position[0]), -1, -1):
            # checks all the way to the left in entity's current Y-position
            if self.curr_level.map[math.floor(self.position[1])][i] == _EMPTY_SPACE:
                x_dist_neg += 1
            else:
                # returns a list with distance to the left and X-position of the next piece
                return [x_dist_neg, i]

    def set_curr_level(self, level: "Level"):
        self.curr_level = level
        if isinstance(self, Player):
            self.position = level.player_starting_position


# PLAYER CLASS
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
        # self.character = "😄"
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

        # print(self.position+", "+enemy.position)
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
            old_position = self.position.copy()

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


# ENEMY CLASS
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

        """
        movement types:
        0 = horizontal
        1 = vertical
        """

        self.position[0] += self.movement_type[0] * ENEMY_MOV_FACTOR * self.enemy_speed
        self.position[1] += self.movement_type[1] * ENEMY_MOV_FACTOR * self.enemy_speed

        self.collision_enemy()


# ITEMS CLASS
class Item(Entity):
    def __init__(self, item_type):
        Entity.__init__(self)
        self.item_type = item_type


# LANDSCAPE OBJECTS CLASS
class Level:
    map: List[List[str]]  # matrix representation of the level data
    enemies: List[Enemy]
    name: str
    player_starting_position: List[int]

    def __init__(
        self,
        name: str,
        enemies: List[Enemy],
        player_starting_position: List[int] = [1, 1],
    ):
        self.enemies = enemies
        self.name = name
        self.map = []
        self.player_starting_position = player_starting_position

        # Init enemies
        for enemy in enemies:
            enemy.set_curr_level(self)

        for i in range(y_resolution):
            self.map.append([])
            for _ in range(x_resolution):
                self.map[i].append(_EMPTY_SPACE)

        self.init_map_border()

    def init_map_border(self):
        self.map[0][0] = _UL
        self.map[y_resolution - 1][x_resolution - 1] = _LR
        self.map[0][x_resolution - 1] = _UR
        self.map[y_resolution - 1][0] = _LL

        for i in range(1, y_resolution - 1):
            self.map[i][0] = _V
            self.map[i][x_resolution - 1] = _V

        for i in range(1, x_resolution - 1):
            self.map[0][i] = _H
            self.map[y_resolution - 1][i] = _H

    def print_message(self, message: str):
        if len(message) <= 0:
            return

        mid_x: int = int(x_resolution / 2)
        mid_y: int = int(y_resolution / 2)

        # Message position
        starting_message_x: int = int(mid_x - len(message) / 2)
        ending_message_x: int = int(mid_x + len(message) / 2)

        # Set up border
        starting_border_x: int = starting_message_x - 2
        ending_border_x: int = ending_message_x + 2
        starting_border_y: int = mid_y - 2
        ending_border_y: int = mid_y + 3

        # Print border
        for x in range(starting_border_x, ending_border_x):
            for y in range(starting_border_y, ending_border_y):
                char = _EMPTY_SPACE

                if y == starting_border_y:
                    if x == starting_border_x:
                        char = colored(_UL)
                    elif x == ending_border_x - 1:
                        char = colored(_UR)
                    else:
                        char = colored(_H)
                elif y == ending_border_y - 1:
                    if x == starting_border_x:
                        char = colored(_LL)
                    elif x == ending_border_x - 1:
                        char = colored(_LR)
                    else:
                        char = colored(_H)
                elif y == ending_border_y - 1:
                    char = colored(_H)
                elif x == starting_border_x or x == ending_border_x - 1:
                    char = colored(_V)

                self.map[y][x] = char

        # Print message
        for x, index in enumerate(range(starting_message_x, ending_message_x)):
            self.map[mid_y][index] = colored(message[x], "yellow")


# PLAYFIELD CLASS
class Game:
    status: Literal["playing", "paused", "gameover"] = "playing"
    player: Player
    levels: List[Level]
    current_level: int = 0

    def __init__(self, player: Player, levels: List[Level]):
        self.levels = levels
        self.current_level = 0

        self.player = player
        self.player.set_curr_level(self.levels[self.current_level])

        print("INIT GAME")
        print(self.player.curr_level)
        print(self.levels[self.current_level])
        print(self.levels[self.current_level].enemies)

    """
    MOST IMPORTANT METHOD
    """

    def print_playfield(self):
        # delay FPS
        time.sleep(1 / fps)

        curr_level = self.levels[self.current_level]
        enemies = curr_level.enemies

        # we make a matrix representation of the playfield
        screen_matrix: List[List[str]] = []

        for i in range(y_resolution):
            screen_matrix.append([])
            for j in range(x_resolution):
                screen_matrix[i].append(_EMPTY_SPACE)

        # we insert the level design into the matrix

        for i in range(y_resolution):
            for j in range(x_resolution):
                screen_matrix[i][j] = curr_level.map[i][j]

        # we insert the enemies
        for enemy in enemies:
            # enemies move
            enemy.movement()

            # depends on the type of enemy:
            y = math.floor(enemy.position[1])
            x = math.floor(enemy.position[0])

            screen_matrix[y][x] = enemy.get_char()

        # calculates effect of gravity in player
        self.player.apply_gravity()

        # landscape collision when jumping
        self.player.collision_ls_jump()

        # enemy collision
        self.player.collision_en()

        # we insert the player character
        playerX, playerY = player.position
        screen_matrix[playerY][playerX] = self.player.get_char()

        # we convert the screen matrix into a string, so we can print it
        matrix_string = ""

        for i in range(y_resolution):
            for j in range(x_resolution):
                matrix_string += screen_matrix[i][j]
            if i < y_resolution - 1:
                matrix_string += "\n"

        clear()

        print(matrix_string)

        # HUD
        # TODO: refactor
        hud = ""

        health = str(self.player.health)

        if self.player.health <= 25:
            health = colored(health, "red")
        elif 75 < self.player.health <= 100:
            health = colored(health, "green")
        elif 25 < self.player.health <= 75:
            health = colored(health, "yellow")

        # points
        # hud += (
        #     "Score: " + str(self.player.points) + " | Health: " + health + " | Y-dist: "
        # )ddwaa
        # hud += (
        #     str(self.player.y_distance()[0])
        #     + " | (-)Y-dist: ("
        #     + str(self.player.y_distance_neg()[0])
        #     + ","
        #     + str(self.player.y_distance_neg()[1])
        #     + ")"
        # )
        hud += "Score: " + str(self.player.points) + " | Health: " + health
        hud += (
            " | Pos: ("
            + str(self.player.position[0])
            + ", "
            + str(self.player.position[1])
            + ") | Vy: "
        )
        hud += str(round(self.player.falling_velocity, 3))
        # hud += " | X-dist: (" + str(player.x_distance(level1)[0]) + "," + str(player.x_distance(level1)[1]) + ") | "
        # hud += "(-)X-dist: (" + str(player.x_distance_neg(level1)[0]) + "," + str(player.x_distance_neg(level1)[1]) + ")"

        print(hud)


################################################################################

# we initialize classes
player = Player(0)

"""
level 1 DATA:
"""

# level 1 enemies
enemies_l1 = [
    Enemy(
        enemy_type=1,
        enemy_speed=2,
        movement_type=[1, 0],
        position=[10, 5],
        character="*",
    ),
    Enemy(1, 4, [1, 0], [15, 3], character="x"),
    Enemy(1, 1, [0, 1], [2, 2], character="0"),
    Enemy(1, 1, [0, 1], [32, 7], character="%"),
    Enemy(1, 4, [1, 0], [6, 11], character="&"),
    Enemy(1, 10, [-1, 1], [40, 11], character="*"),
    # Jumpy enemies
    Enemy(2, 8, [1, 0], [11, 23], character="@", color="cyan"),
    Enemy(2, 1, [1, 0], [12, 23], character="@", color="blue"),
    Enemy(2, -5, [1.2, 0], [12, 23], character="@", color="magenta"),
    Enemy(2, 0, [2, 0], [65, 23], character="@", color="yellow"),
]

level1 = Level(name="Level 1", enemies=enemies_l1)

# level 1 landscape
level1.map[5][4] = _UR
level1.map[5][3] = _H
level1.map[5][2] = _H
level1.map[5][1] = _H

level1.map[21][8] = _H
level1.map[21][7] = _H
level1.map[21][6] = _H

level1.map[19][9] = _H
level1.map[19][10] = _H
level1.map[19][11] = _H

level1.map[17][5] = _H
level1.map[17][6] = _H
level1.map[17][7] = _H

level1.map[15][10] = _H
level1.map[15][11] = _H
level1.map[15][12] = _H

level1.map[13][16] = _H
level1.map[13][17] = _H
level1.map[13][18] = _H

level1.map[14][22] = _H
level1.map[14][23] = _H
level1.map[14][24] = _H

level1.map[11][29] = _H
level1.map[11][30] = _H
level1.map[11][31] = _H

level1.map[9][31] = _H
level1.map[9][32] = _H
level1.map[9][33] = _H

level1.map[8][36] = _H
level1.map[8][37] = _H
level1.map[8][38] = _H

level1.map[5][39] = _H
level1.map[5][40] = _H
level1.map[5][41] = _H

level1.map[4][31] = _H
level1.map[4][32] = _H
level1.map[4][33] = _H

level1.map[5][0] = _CR

for i in range(6, 23):
    level1.map[i][4] = _V

level1.map[22][4] = _LR
level1.map[22][3] = _H
level1.map[22][2] = _H
level1.map[22][1] = _H
level1.map[22][0] = _CR
level1.map[17][4] = _CR

"""    
end of level 1 DATA
"""

# INSTANTIATE GAME
game = Game(player=player, levels=[level1])

while game.status == "playing":
    if player.player_movement() == "q":
        level1.print_message("BYE BYE")
        game.status = "gameover"

    if player.status == "dead":
        level1.print_message("GAME OVER")
        game.status = "gameover"

    game.print_playfield()
