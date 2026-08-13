"""The Game class: owns the current level and renders each frame."""

import math

from constants import EMPTY_SPACE, X_RESOLUTION, Y_RESOLUTION, DoubleLines
from entities.entity import Entity
from entities.player import Player
from level import Level
from terminal import clear
from utils import colored

_GOOD_HEALTH_LIMIT = 75
_BAD_HEALTH_LIMIT = 25

_GOOD_HEALTH_COLOR = "green"
_BAD_HEALTH_COLOR = "red"
_MID_HEALTH_COLOR = "yellow"

_MESSAGE_BORDER_COLOR = "red"
_MESSAGE_TEXT_COLOR = "yellow"


class Display:
    # we use a matrix representation of the playfield
    _screen_matrix: list[list[str]]
    _curr_level: Level

    def __init__(self, curr_level: Level):
        self._curr_level = curr_level
        self.populate_level_into_matrix()

    def populate_level_into_matrix(self):
        self._screen_matrix = []

        for y in range(Y_RESOLUTION):
            self._screen_matrix.append([])
            for x in range(X_RESOLUTION):
                self._screen_matrix[y].append(self._curr_level.map[y][x] or EMPTY_SPACE)

    def add_to_matrix(self, entity: Entity):
        y = math.floor(entity.position[1])
        x = math.floor(entity.position[0])

        self._screen_matrix[y][x] = entity.get_char()

    def print_message(self, message: str, padding_x: int = 2, padding_y: int = 1):
        if len(message) <= 0:
            return

        mid_x = int(X_RESOLUTION / 2)
        mid_y = int(Y_RESOLUTION / 2)

        # Message position
        starting_message_x = int(mid_x - len(message) / 2)
        ending_message_x = int(mid_x + len(message) / 2)

        # Set up border
        starting_border_x: int = starting_message_x - padding_x
        ending_border_x: int = ending_message_x + padding_x
        starting_border_y: int = mid_y - padding_y
        ending_border_y: int = mid_y + padding_y + 1

        # Print border
        for x in range(starting_border_x, ending_border_x):
            for y in range(starting_border_y, ending_border_y):
                char = EMPTY_SPACE

                if y == starting_border_y:
                    if x == starting_border_x:
                        char = colored(DoubleLines.UL, _MESSAGE_BORDER_COLOR)
                    elif x == ending_border_x - 1:
                        char = colored(DoubleLines.UR, _MESSAGE_BORDER_COLOR)
                    else:
                        char = colored(DoubleLines.H, _MESSAGE_BORDER_COLOR)
                elif y == ending_border_y - 1:
                    if x == starting_border_x:
                        char = colored(DoubleLines.LL, _MESSAGE_BORDER_COLOR)
                    elif x == ending_border_x - 1:
                        char = colored(DoubleLines.LR, _MESSAGE_BORDER_COLOR)
                    else:
                        char = colored(DoubleLines.H, _MESSAGE_BORDER_COLOR)
                elif x == starting_border_x or x == ending_border_x - 1:
                    char = colored(DoubleLines.V, _MESSAGE_BORDER_COLOR)

                self._screen_matrix[y][x] = char

        # Display message
        for x, index in enumerate(range(starting_message_x, ending_message_x)):
            self._screen_matrix[mid_y][index] = colored(message[x], _MESSAGE_TEXT_COLOR)

        self.print_curr_screen()

    def print_curr_screen(self, player: Player | None = None):
        matrix_string = ""

        for i in range(Y_RESOLUTION):
            for j in range(X_RESOLUTION):
                matrix_string += self._screen_matrix[i][j]
            if i < Y_RESOLUTION - 1:
                matrix_string += "\n"

        clear()
        print(matrix_string)

        if player:
            self._print_hud(player)

    def _print_hud(self, player: Player):
        health = str(player.health)

        if player.health <= _BAD_HEALTH_LIMIT:
            health = colored(health, _BAD_HEALTH_COLOR)
        elif _BAD_HEALTH_LIMIT < player.health <= _GOOD_HEALTH_LIMIT:
            health = colored(health, _MID_HEALTH_COLOR)
        elif player.health > _GOOD_HEALTH_LIMIT:
            health = colored(health, _GOOD_HEALTH_COLOR)

        hud = "Score: " + str(player.points) + " | Health: " + health
        hud += (
            " | Pos: ("
            + str(player.position[0])
            + ", "
            + str(player.position[1])
            + ") | Vy: "
        )
        hud += str(round(player.falling_velocity, 3))

        print(hud)
