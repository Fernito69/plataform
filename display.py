import math
import time
from typing import TYPE_CHECKING, Callable

from factories.theme import RGB, Blue, Green, Red, White, Yellow
from mappings.keyboard import default_keyboard_mapping
from model.base import Point2F, Point2I, Vector2I
from model.game import GameMode
from model.keyboard import DisplayKeys
from model.shared import KeyboardHandler
from model.theme import EMPTY_SPACE, DoubleLines
from physics2d.constants import MAX_FPS_PHYSICS, X_RESOLUTION_PHYSICS, Y_RESOLUTION_PHYSICS
from platformer_v1.constants import MAX_FPS_2D, X_RESOLUTION_2D, Y_RESOLUTION_2D
from platformer_v1.entities.player2d import Player2D
from terminal import clear, on_key_press
from three_d_renderer.constants import (
    ANTIALIASING_INTENSITY,
    MAX_FPS_3D,
    X_RESOLUTION_3D,
    Y_RESOLUTION_3D,
)
from three_d_renderer.entities.player3d import Player3D
from utils import colored, extract_color_from_string, has_bg_color

if TYPE_CHECKING:
    from game import Game

_DEFAULT_FPS = MAX_FPS_PHYSICS

_MESSAGE_BORDER_COLOR = Red()
_MESSAGE_TEXT_COLOR = Yellow()

# TODO: move all these and methods that use them to platformer_v1


class Display(KeyboardHandler):
    _screen_matrix: list[list[str]]

    curr_fps: float
    curr_x_resolution: int
    curr_y_resolution: int

    _debug_str: str | None = None

    antialiasing: bool

    _print_fps: bool

    def __init__(
        self,
        game: "Game",
        fps: float = _DEFAULT_FPS,
        print_fps: bool = True,
    ):
        self.game = game
        self.antialiasing = True
        self.curr_fps = fps
        self._print_fps = print_fps

    def set_mode(self, mode: GameMode) -> None:
        match mode:
            case GameMode.PLATFORMER_V1:
                self._set_2d_mode()
            case GameMode.LINES_3D | GameMode.VOXELS_3D:
                self._set_3d_mode()
            case GameMode.PHYSICS_2D:
                self._set_physics_mode()

    def debug_log(self, msg: str) -> None:
        self._debug_str = msg

    # TODO: border thickness should not be passed here
    def is_in_screen(self, point: Point2F, border_thickness: int = 1) -> bool:
        return (
            point[0] >= border_thickness
            and point[0] < self.curr_x_resolution - border_thickness
            and point[1] >= border_thickness
            and point[1] < self.curr_y_resolution - border_thickness
        )

    def modify_resolution(self, amount: Vector2I) -> None:
        self.curr_x_resolution += amount[0]
        self.curr_y_resolution += amount[1]

    def put_char_in_pixel(self, char: str, position: Point2F):
        y = math.floor(position[1])
        x = math.floor(position[0])
        if 0 <= y < self.curr_y_resolution and 0 <= x < self.curr_x_resolution:
            self._screen_matrix[y][x] = char

    # TODO: this is not working well, fix
    def print_message(self, message: str, padding_x: int = 4, padding_y: int = 2):
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

        if len(message) < len(range(starting_message_x - ending_message_x)):
            raise IndexError("WTF?: " + message)

        # Print border
        for x in range(starting_border_x, ending_border_x):
            for y in range(starting_border_y, ending_border_y):

                def _col(ch: str) -> str:
                    return colored(
                        ch,
                        color=_MESSAGE_BORDER_COLOR,
                        bg_color=extract_color_from_string(
                            self._screen_matrix[y][x]
                        ).with_intensity(1),
                    )

                char = self._screen_matrix[y][x]

                if y == starting_border_y:
                    if x == starting_border_x:
                        char = _col(DoubleLines.UL)
                    elif x == ending_border_x - 1:
                        char = _col(DoubleLines.UR)
                    else:
                        char = _col(DoubleLines.H)
                elif y == ending_border_y - 1:
                    if x == starting_border_x:
                        char = _col(DoubleLines.LL)
                    elif x == ending_border_x - 1:
                        char = _col(DoubleLines.LR)
                    else:
                        char = _col(DoubleLines.H)
                elif x == starting_border_x or x == ending_border_x - 1:
                    char = _col(DoubleLines.V)

                self._screen_matrix[y][x] = char

        # Display message
        for index, x in enumerate(range(starting_message_x, ending_message_x)):

            def _c(index: int) -> str:
                return colored(
                    message[index] if index < len(message) else self._screen_matrix[mid_y][x],
                    color=_MESSAGE_TEXT_COLOR,
                    bg_color=extract_color_from_string(
                        self._screen_matrix[mid_y][x]
                    ).with_intensity(0.5)
                    if self._screen_matrix[mid_y][x] != EMPTY_SPACE
                    else RGB(0, 0, 0, 0),
                )

            self._screen_matrix[mid_y][x] = _c(index)

        _curr_antialiasing = self.antialiasing
        self.antialiasing = True
        self.print_curr_screen()
        self.antialiasing = _curr_antialiasing

    def put_screen_content(self, new_screen_matrix: list[list[str]]) -> None:
        self._screen_matrix = new_screen_matrix

    def get_screen_content(self) -> list[list[str]]:
        return self._screen_matrix

    _measured_fps: float = 0

    def fps_throttle(self, func: Callable[[], None]) -> None:
        period = 1 / (self._curr_fps or 1)

        start = time.perf_counter()
        func()
        ellapsed = time.perf_counter() - start

        raw_diff = period - ellapsed

        self._measured_fps = min(1 / ((period - raw_diff) or 0.001), self._curr_fps)

        time.sleep(max(0, raw_diff))

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
            matrix_string += colored("\nDEBUG: ", Red()) + self._debug_str

        if player:
            self._print_hud(player)

        if self._print_fps:
            matrix_string += f"{colored('\nFPS: ', Green())} {str(round(self._measured_fps, 2))}"

        print(matrix_string)

    def _set_2d_mode(self):
        self.antialiasing = True
        self._set_fps(MAX_FPS_2D)
        self._set_resolution((X_RESOLUTION_2D, Y_RESOLUTION_2D))

    def _set_physics_mode(self):
        # Handled in-engine
        self.antialiasing = False
        self._set_fps(MAX_FPS_PHYSICS)
        # FAQ: Why Y_RES/2? Each console character represent 2 "pixels" with LOWER_PIXEL_CHAR and a bg color for the empty space
        self._set_resolution((X_RESOLUTION_PHYSICS, round(Y_RESOLUTION_PHYSICS / 2)))

    def _set_3d_mode(self):
        self.antialiasing = True
        self._set_fps(MAX_FPS_3D)
        self._set_resolution((X_RESOLUTION_3D, Y_RESOLUTION_3D))

    def _set_fps(self, fps: float) -> None:
        self._curr_fps = fps

    def _set_resolution(self, resolution: Point2I) -> None:
        self.curr_x_resolution = resolution[0]
        self.curr_y_resolution = resolution[1]

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
            mode_key = default_keyboard_mapping[DisplayKeys.SWITCH_RENDERING_MODE]

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

        health = player.get_health()

        hud = "Score: " + str(player.points) + " | Health: " + health
        hud += " | Pos: (" + str(player.position[0]) + ", " + str(player.position[1]) + ") | Vy: "
        hud += str(round(player.falling_velocity, 3))

        print(hud)

    ##############
    # PLAYER INPUT
    ##############
    def handle_player_input(self) -> None:
        if self.game.mode == GameMode.PLATFORMER_V1:
            return

        self._increase_x_resolution()
        self._decrease_x_resolution()
        self._increase_y_resolution()
        self._decrease_y_resolution()

    # TODO: increase res functionality is broken, fix
    @on_key_press(DisplayKeys.INCREASE_X_RESOLUTION)
    def _increase_x_resolution(self):
        self.modify_resolution((1, 0))

    @on_key_press(DisplayKeys.DECREASE_X_RESOLUTION)
    def _decrease_x_resolution(self):
        self.modify_resolution((-1, 0))

    @on_key_press(DisplayKeys.INCREASE_Y_RESOLUTION)
    def _increase_y_resolution(self):
        self.modify_resolution((0, 1))

    @on_key_press(DisplayKeys.DECREASE_Y_RESOLUTION)
    def _decrease_y_resolution(self):
        self.modify_resolution((0, -1))
