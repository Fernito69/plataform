"""The Game class: owns the current level and renders each frame."""

import math
import time
from typing import Literal

from constants import EMPTY_SPACE, FPS, X_RESOLUTION, Y_RESOLUTION, colored
from entities import Player
from level import Level
from terminal import clear


class Game:
    status: Literal["playing", "paused", "gameover"] = "playing"
    player: Player
    levels: list[Level]
    current_level: int = 0

    def __init__(self, player: Player, levels: list[Level]):
        self.levels = levels
        self.current_level = 0

        self.player = player
        self.player.set_curr_level(self.levels[self.current_level])

    def print_playfield(self):
        # delay FPS
        time.sleep(1 / FPS)

        curr_level = self.levels[self.current_level]
        enemies = curr_level.enemies

        # we make a matrix representation of the playfield
        screen_matrix: list[list[str]] = []

        for i in range(Y_RESOLUTION):
            screen_matrix.append([])
            for j in range(X_RESOLUTION):
                screen_matrix[i].append(EMPTY_SPACE)

        # we insert the level design into the matrix
        for i in range(Y_RESOLUTION):
            for j in range(X_RESOLUTION):
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
        player_x, player_y = self.player.position
        screen_matrix[player_y][player_x] = self.player.get_char()

        # we convert the screen matrix into a string, so we can print it
        matrix_string = ""

        for i in range(Y_RESOLUTION):
            for j in range(X_RESOLUTION):
                matrix_string += screen_matrix[i][j]
            if i < Y_RESOLUTION - 1:
                matrix_string += "\n"

        clear()

        print(matrix_string)

        # HUD
        health = str(self.player.health)

        if self.player.health <= 25:
            health = colored(health, "red")
        elif 75 < self.player.health <= 100:
            health = colored(health, "green")
        elif 25 < self.player.health <= 75:
            health = colored(health, "yellow")

        hud = "Score: " + str(self.player.points) + " | Health: " + health
        hud += (
            " | Pos: ("
            + str(self.player.position[0])
            + ", "
            + str(self.player.position[1])
            + ") | Vy: "
        )
        hud += str(round(self.player.falling_velocity, 3))

        print(hud)
