"""The Game class: owns the current level and renders each frame."""

import math

from constants import EMPTY_SPACE, X_RESOLUTION_2D, Y_RESOLUTION_2D
from entities.base import Entity2D
from entities.player2d import Player2D
from factories.theme import RGB, Blue, Green, Red, White, Yellow
from level_2d import Level2D
from mappings.keyboard import default_keyboard_mapping
from model.base import Point2, Vector2
from model.keyboard import DisplayKeys
from model.theme import DoubleLines
from terminal import clear
from three_d_renderer.constants import (
    ANTIALIASING_INTENSITY,
    X_RESOLUTION_3D,
    Y_RESOLUTION_3D,
)
from three_d_renderer.entities.player3d import Player3D
from utils import colored, extract_color_from_string, has_bg_color

_GOOD_HEALTH_LIMIT = 75
_BAD_HEALTH_LIMIT = 25

_GOOD_HEALTH_COLOR = Green()
_BAD_HEALTH_COLOR = Red()
_MID_HEALTH_COLOR = Yellow()

_MESSAGE_BORDER_COLOR = Red()
_MESSAGE_TEXT_COLOR = Yellow()


# TODO: add status (2d, 3d)
class Display:
    # we use a matrix representation of the playfield
    _screen_matrix: list[list[str]]
    _curr_level_2D: Level2D

    curr_x_resolution: int
    curr_y_resolution: int

    _debug_str: str | None = None

    # TODO: do this, wire properly!
    # _curr_level_3D: Level3D
    #
    curr_3d_char_mode: str | list[str]

    antialiasing: bool

    def __init__(
        self,
        curr_level: Level2D,
    ):
        self._curr_level_2D = curr_level
        self.populate_level_into_matrix()
        self.curr_3d_char_mode = "█"
        self.antialiasing = True

        self.switch_3d_char_mode()

    def set_2d_resolution(self):
        self._set_resolution((X_RESOLUTION_2D, Y_RESOLUTION_2D))

    def set_3d_resolution(self):
        self._set_resolution((X_RESOLUTION_3D, Y_RESOLUTION_3D))

    def debug_log(self, msg: str) -> None:
        self._debug_str = msg

    def populate_level_into_matrix(self):
        self.set_2d_resolution()
        self.put_screen_content([])

        for y in range(self.curr_y_resolution):
            self._screen_matrix.append([])
            for x in range(self.curr_x_resolution):
                self._screen_matrix[y].append(self._curr_level_2D.map[y][x] or EMPTY_SPACE)

    def switch_3d_char_mode(self) -> str | list[str]:
        # THIS IS HORRIBLE, DO PROPERLY
        char: str | list[str] = "█"
        if self.curr_3d_char_mode == "█":
            char = ["▀", "▄"]
        elif self.curr_3d_char_mode == ["▀", "▄"]:
            char = "░"
        if self.curr_3d_char_mode == "░":
            char = "█"

        self.curr_3d_char_mode = char
        return self.curr_3d_char_mode

    # TODO: border thickness should not be passed here
    def is_in_screen(self, point: Point2, border_thickness: int = 1) -> bool:
        return (
            point[0] >= border_thickness
            and point[0] < self.curr_x_resolution - border_thickness
            and point[1] >= border_thickness
            and point[1] < self.curr_y_resolution - border_thickness
        )

    def modify_resolution(self, amount: Vector2) -> None:
        self.curr_x_resolution += int(amount[0])
        self.curr_y_resolution += int(amount[1])

    def _set_resolution(self, resolution: Vector2) -> None:
        self.curr_x_resolution = int(resolution[0])
        self.curr_y_resolution = int(resolution[1])

    def _put_char_in_pixel(self, char: str, position: Point2):
        y = math.floor(position[1])
        x = math.floor(position[0])

        self._screen_matrix[y][x] = char

    def _add_2d_entity_to_matrix(self, entity: Entity2D):
        y = math.floor(entity.position[1])
        x = math.floor(entity.position[0])

        self._screen_matrix[y][x] = entity.get_char()

    # TODO: this is broken
    def print_message(self, message: str, padding_x: int = 2, padding_y: int = 1):
        if len(message) <= 0:
            return

        mid_x = round(self.curr_x_resolution / 2)
        mid_y = round(self.curr_y_resolution / 2)

        # Message position
        starting_message_x = round(mid_x - len(message) / 2)
        ending_message_x = round(mid_x + len(message) / 2)

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

    def put_screen_content(self, new_screen_matrix: list[list[str]]):
        self._screen_matrix = new_screen_matrix

    def print_curr_screen(self, player: Player2D | Player3D | None = None):
        matrix_string = ""

        for i in range(self.curr_y_resolution):
            for j in range(self.curr_x_resolution):
                matrix_string += (
                    self._screen_matrix[i][j]
                    if has_bg_color(self._screen_matrix[i][j], black_is_not_condidered_bg=False)
                    # TODO: it should not override the color behind it in the case of superposing objects
                    # check if it belongs to the same entity!! we can do that in the loop I think
                    # TODO: how do I know if there is gonna be something there later? since we are checking from closest to farthest
                    # use a precomputed store with the not rounded coord, aka subpixel??
                    else colored(
                        self._screen_matrix[i][j],
                        bg_color=extract_color_from_string(
                            self._screen_matrix[i][j]
                        ).with_intensity(ANTIALIASING_INTENSITY)
                        if self.antialiasing
                        else RGB(0, 0, 0),
                    )
                )
            if i < self.curr_y_resolution - 1:
                matrix_string += "\n"

        clear()

        if self._debug_str:
            matrix_string += colored(" DEBUG: ", Red()) + self._debug_str

        print(matrix_string)

        # TODO: we can use this in 3d to show controls
        if player:
            self._print_hud(player)

    def _print_hud(self, player: Player2D | Player3D | None = None):
        if not player:
            return

        hud = ""
        # Horrible branching
        if isinstance(player, Player3D):
            switch_aa_key = default_keyboard_mapping[DisplayKeys.SWITCH_ANTIALIASING]
            fov_decr_key = default_keyboard_mapping[DisplayKeys.DECREASE_FOV]
            fov_incr_key = default_keyboard_mapping[DisplayKeys.INCREASE_FOV]
            decr_x_key = default_keyboard_mapping[DisplayKeys.DECREASE_X_RESOLUTION]
            incr_x_key = default_keyboard_mapping[DisplayKeys.INCREASE_X_RESOLUTION]
            decr_y_key = default_keyboard_mapping[DisplayKeys.DECREASE_Y_RESOLUTION]
            incr_y_key = default_keyboard_mapping[DisplayKeys.INCREASE_Y_RESOLUTION]
            decr_fog_key = default_keyboard_mapping[DisplayKeys.DECREASE_VISIBILITY]
            incr_vis_key = default_keyboard_mapping[DisplayKeys.INCREASE_VISIBILITY]
            shuffle_key = default_keyboard_mapping[DisplayKeys.SHUFFLE_COLORS]
            mode_key = default_keyboard_mapping[DisplayKeys.SWITCH_CHAR_MODE]

            def _c(s: str) -> str:
                return "'" + colored(s.capitalize(), White(1)) + "'"

            ON_STR = colored("ON", Green(0.8))
            OFF_STR = colored("OFF", Red(0.8))
            SEP = f" {colored('|', Blue(0.8))} "

            hud += f"{colored('KEYS REFERENCE', Yellow(0.9))}: "
            hud += f"AA: ({_c(switch_aa_key)}) {ON_STR if self.antialiasing else OFF_STR}{SEP}"
            hud += f"FOV (-/+): {_c(fov_incr_key)}, {_c(fov_decr_key)}{SEP}"
            hud += f"X (-/+): {_c(decr_x_key)}, {_c(incr_x_key)}{SEP}"
            hud += f"Y (-/+): {_c(decr_y_key)}, {_c(incr_y_key)}{SEP}"
            hud += f"Visibility (-/+): {_c(decr_fog_key)}, {_c(incr_vis_key)}\n{SEP}"
            hud += f"Mode: {_c(mode_key)}{SEP}"
            hud += f"Shuffle!: {_c(shuffle_key)}{SEP}"
            hud += f"Curr pos: {colored((f'({player.position[0]},{player.position[1]},{player.position[2]})'))}{SEP}"

            return print(hud)

        health = str(player.health)

        # TODO: refactor it to go continuously from green, to yellow, to red
        if player.health <= _BAD_HEALTH_LIMIT:
            health = colored(health, _BAD_HEALTH_COLOR)
        elif _BAD_HEALTH_LIMIT < player.health <= _GOOD_HEALTH_LIMIT:
            health = colored(health, _MID_HEALTH_COLOR)
        elif player.health > _GOOD_HEALTH_LIMIT:
            health = colored(health, _GOOD_HEALTH_COLOR)

        hud = "Score: " + str(player.points) + " | Health: " + health
        hud += " | Pos: (" + str(player.position[0]) + ", " + str(player.position[1]) + ") | Vy: "
        hud += str(round(player.falling_velocity, 3))

        print(hud)
