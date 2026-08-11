"""The Game class: owns the current level and renders each frame."""

import math
import time

from constants import EMPTY_SPACE, FPS, X_RESOLUTION, Y_RESOLUTION
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
        self.init_matrix(curr_level)

    def init_matrix(self, curr_level: Level):
        self._screen_matrix = []
        self._curr_level = curr_level

        for i in range(Y_RESOLUTION):
            self._screen_matrix.append([])
            for j in range(X_RESOLUTION):
                self._screen_matrix[i].append(EMPTY_SPACE)

        # we insert the level design into the matrix
        for i in range(Y_RESOLUTION):
            for j in range(X_RESOLUTION):
                self._screen_matrix[i][j] = curr_level.map[i][j]

    def add_to_matrix(self, entity: Entity):
        y = math.floor(entity.position[1])
        x = math.floor(entity.position[0])

        self._screen_matrix[y][x] = entity.get_char()

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

            # TODO: refactor this message out of there
            self.levels[self.current_level_index].print_message(message)
            self.status = GameStatus.GAMEOVER

    def game_loop(self):
        # Listen to player
        self.player.player_input()

        # delay FPS
        time.sleep(1 / FPS)

        curr_level = self.levels[self.current_level_index]

        # Init the matrix
        self.display.init_matrix(curr_level)

        # player actions
        self.player.do_your_thing()
        self.display.add_to_matrix(self.player)

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
