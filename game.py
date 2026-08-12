"""The Game class: owns the current level and renders each frame."""

import math
import time

from constants import EMPTY_SPACE, FPS, X_RESOLUTION, Y_RESOLUTION, DoubleLines
from entities.entity import Entity
from entities.player import Player
from level import Level
from model.game import GameStatus
from model.player import PlayerStatus
from terminal import clear
from utils import colored

_GOOD_HEALTH_LIMIT = 75
_BAD_HEALTH_LIMIT = 25

_GOOD_HEALTH_COLOR = "green"
_BAD_HEALTH_COLOR = "red"
_MID_HEALTH_COLOR = "yellow"


class Display:
    # we use a matrix representation of the playfield
    _screen_matrix: list[list[str]]
    _curr_level: Level

    def __init__(self, curr_level: Level):
        self._curr_level = curr_level
        self.populate_level_into_matrix()

    def populate_level_into_matrix(self):
        self._screen_matrix = []

        for i in range(Y_RESOLUTION):
            self._screen_matrix.append([])
            for _ in range(X_RESOLUTION):
                self._screen_matrix[i].append(EMPTY_SPACE)

        # we insert the level design into the matrix
        for i in range(Y_RESOLUTION):
            for j in range(X_RESOLUTION):
                # self._screen_matrix[i][j] = self._curr_level.map[i][j]
                # for _ in range(X_RESOLUTION):
                self._screen_matrix[i].append(self._curr_level.map[i][j] or EMPTY_SPACE)

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
                        char = colored(DoubleLines.UL, "red")
                    elif x == ending_border_x - 1:
                        char = colored(DoubleLines.UR, "red")
                    else:
                        char = colored(DoubleLines.H, "red")
                elif y == ending_border_y - 1:
                    if x == starting_border_x:
                        char = colored(DoubleLines.LL, "red")
                    elif x == ending_border_x - 1:
                        char = colored(DoubleLines.LR, "red")
                    else:
                        char = colored(DoubleLines.H, "red")
                elif x == starting_border_x or x == ending_border_x - 1:
                    char = colored(DoubleLines.V, "red")

                self._screen_matrix[y][x] = char

        # Display message
        for x, index in enumerate(range(starting_message_x, ending_message_x)):
            self._screen_matrix[mid_y][index] = colored(message[x], "yellow")

        self.print_game()

    def print_game(self):
        matrix_string = ""

        for i in range(Y_RESOLUTION):
            for j in range(X_RESOLUTION):
                matrix_string += self._screen_matrix[i][j]
            if i < Y_RESOLUTION - 1:
                matrix_string += "\n"

        clear()

        print(matrix_string)

    def print_hud(self, player: Player):
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


class Game:
    status: GameStatus = GameStatus.PLAYING
    player: Player
    levels: list[Level]
    current_level_index: int = 0

    display: Display

    def __init__(
        self, player: Player, levels: list[Level], current_level_index: int = 0
    ):
        self.levels = levels
        self.current_level_index = 0

        self.player = player
        self.player.set_curr_level(levels[current_level_index])
        self.display = Display(levels[current_level_index])

    def check_player_status(self):
        if self.player.status != PlayerStatus.ALIVE:
            match self.player.status:
                case PlayerStatus.DEAD:
                    message = "GAME OVER"
                case PlayerStatus.QUIT:
                    message = "BYE BYE"
                case PlayerStatus.EXIT:
                    message = "YOU WON!"

            self.display.print_message(message)
            self.status = GameStatus.GAMEOVER

    def game_loop(self):
        # Listen to player
        self.player.player_input()

        # delay FPS
        time.sleep(1 / FPS)

        # Init the matrix
        self.display.populate_level_into_matrix()

        # player actions
        self.player.do_your_thing()
        self.display.add_to_matrix(self.player)

        curr_level = self.levels[self.current_level_index]

        # enemy actions
        for enemy in curr_level.enemies:
            enemy.do_your_thing()
            self.display.add_to_matrix(enemy)

        # exit actions
        for exit in curr_level.exits:
            exit.do_your_thing()
            self.display.add_to_matrix(exit)

        # Print the shit
        self.display.print_game()
        self.display.print_hud(self.player)

        # Check player status
        self.check_player_status()
