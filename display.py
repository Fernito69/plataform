import math
import time
from typing import TYPE_CHECKING, Callable

from constants import ALMOST_ZERO
from factories.theme import RGB, SEPARATOR, Cyan, DoubleLines, Red, White, Yellow
from mappings.keyboard import default_keyboard_mapping
from model.base import PointF, PointI, VectorI
from model.game import GameMode
from model.keyboard import DisplayKeys
from model.shared import KeyboardHandler
from model.theme import BR, EMPTY_SPACE, LOWER_PIXEL_CHAR, UPPER_PIXEL_CHAR
from physics2d.constants import MAX_FPS_PHYSICS, X_RESOLUTION_PHYSICS, Y_RESOLUTION_PHYSICS
from physics2d.entities.player_blob import PlayerBlob
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
from utils import (
    colored,
    extract_bg_color_from_string,
    extract_color_from_string,
    has_bg_color,
    mix_colors,
)

if TYPE_CHECKING:
    from game import Game

_DEFAULT_FPS = MAX_FPS_PHYSICS

_MESSAGE_UPPER_BORDER_COLOR = RGB(0, 255, 100)
_MESSAGE_LOWER_BORDER_COLOR = RGB(170, 80, 255)

_MESSAGE_TEXT_COLOR = Yellow()


class Display(KeyboardHandler):
    curr_x_resolution: int
    curr_y_resolution: int
    antialiasing: bool

    _screen_grid: list[list[str]]

    _curr_fps: float
    _debug_str: str | None = None
    _message: str | None
    _message_intensity: float
    _print_fps: bool

    def __init__(
        self,
        game: "Game",
        fps: float = _DEFAULT_FPS,
        print_fps: bool = True,
    ):
        self.game = game
        self.antialiasing = True
        self._curr_fps = fps
        self._print_fps = print_fps
        self._message = None
        self._message_intensity = 0
        self.set_mode()

    def set_mode(self) -> None:
        match self.game.mode:
            case GameMode.PLATFORMER_V1:
                self._set_2d_mode()
            case GameMode.VOXELS_3D | GameMode.LINES_3D:
                self._set_3d_mode()
            case GameMode.PHYSICS_2D:
                self._set_physics_mode()

    def debug_log(self, msg: str) -> None:
        self._debug_str = msg

    def has_message(self) -> bool:
        return self._message is not None

    # TODO: border thickness should not be passed here
    def is_in_screen(self, point: PointF, border_thickness: int = 1) -> bool:
        return (
            point.x >= border_thickness
            and point.x < self.curr_x_resolution - border_thickness
            and point.y >= border_thickness
            and point.y < self.curr_y_resolution - border_thickness
        )

    def modify_resolution(self, amount: VectorI) -> None:
        self.curr_x_resolution += amount.x
        self.curr_y_resolution += amount.y

    def put_char_in_pixel(self, char: str, position: PointF):
        x = math.floor(position.x)
        y = math.floor(position.y)
        if 0 <= y < self.curr_y_resolution and 0 <= x < self.curr_x_resolution:
            self._screen_grid[y][x] = char

    def set_message(self, message: str | None, intensity: float = 0.7) -> None:
        self._message = message
        self._message_intensity = intensity if message else 0

    def put_screen_content(self, new_grid: list[list[str]]) -> None:
        self._screen_grid = new_grid

    def get_screen_content(self) -> list[list[str]]:
        return self._screen_grid

    _measured_fps: float = 0

    def fps_throttle(self, func: Callable[[], None]) -> None:
        period = 1 / (self._curr_fps or 1)

        start = time.perf_counter()
        func()
        ellapsed = time.perf_counter() - start

        self._measured_fps = min(
            self._curr_fps,
            1 / (ellapsed or ALMOST_ZERO),
        )

        time.sleep(max(0, period - ellapsed))

    def print_curr_screen(self, player: Player2D | Player3D | PlayerBlob | None = None):
        message_container_coords: tuple[PointI, PointI] | None = None
        if self._message:
            message_container_coords = self._add_message_to_screen_grid()

        screen_content = ""

        for y in range(self.curr_y_resolution):
            for x in range(self.curr_x_resolution):
                is_part_of_message: bool = (
                    message_container_coords[1].y <= y <= message_container_coords[1].x
                    or message_container_coords[0].y <= x <= message_container_coords[0].x
                    if message_container_coords
                    else False
                )
                # TODO: all this looks nice but is really hacky. Do properly.
                screen_content += (
                    self._screen_grid[y][x]
                    if has_bg_color(self._screen_grid[y][x], black_is_not_condidered_bg=False)
                    # TODO: it should not override the color behind it in the case of superposing objects
                    # check if it belongs to the same entity!! we can do that in the loop I think
                    # TODO: how do I know if there is gonna be something there later? since we are checking from closest to farthest
                    # use a precomputed store with the not rounded coord, aka subpixel??
                    else colored(
                        self._screen_grid[y][x],
                        bg_color=extract_color_from_string(self._screen_grid[y][x]).with_intensity(
                            ANTIALIASING_INTENSITY
                        )
                        if (self.antialiasing and not is_part_of_message)
                        else RGB(0, 0, 0),
                    )
                )
            if y < self.curr_y_resolution - 1:
                screen_content += BR

        if self._debug_str:
            screen_content += colored(BR + "DEBUG: ", Red()) + self._debug_str

        if player:
            screen_content += BR + self._get_hud_string(player)

        if self._print_fps:
            _sep = SEPARATOR if isinstance(player, Player2D) else "" if player else BR
            screen_content += f"{_sep}{colored('FPS:', Cyan())} {str(round(self._measured_fps))}"

        clear()
        print(screen_content)

    # TODO: allow color in the message string instead of hardcoding it
    # TODO: this logic is all sooo hacky, do better
    def _add_message_to_screen_grid(
        self, padding_x: int = 12, padding_y: int = 4
    ) -> tuple[PointI, PointI] | None:
        if self._message is None or len(self._message) <= 0:
            return

        message_parts: list[str] = self._message.split(BR)
        message_height: int = len(message_parts)
        max_message_lenght = max(len(p) for p in message_parts)

        mid_x = round(self.curr_x_resolution / 2)
        mid_y = round(self.curr_y_resolution / 2)

        # Set up border
        # TODO: de-dup code
        starting_message_x = round(mid_x - max_message_lenght / 2)
        ending_message_x = round(mid_x + max_message_lenght / 2)
        starting_border_x: int = starting_message_x - padding_x
        ending_border_x: int = ending_message_x + padding_x
        starting_border_y: int = mid_y - padding_y
        ending_border_y: int = mid_y + padding_y + message_height

        if len(self._message) < len(range(starting_message_x - ending_message_x)):
            raise IndexError("WTF?: " + self._message)

        # Print border
        for x in range(starting_border_x, ending_border_x):
            y_range = range(starting_border_y, ending_border_y)
            for y_idx, y in enumerate(y_range):
                _border_intensity: float = 1 - (y_idx / len(y_range))

                def _border_col(ch: str) -> str:
                    return colored(
                        ch,
                        color=mix_colors(
                            [
                                _MESSAGE_UPPER_BORDER_COLOR.with_intensity(_border_intensity),
                                _MESSAGE_LOWER_BORDER_COLOR.with_intensity(1 - _border_intensity),
                            ]
                        ).with_intensity(self._message_intensity),
                        bg_color=extract_color_from_string(self._screen_grid[y][x]).with_intensity(
                            (1 - self._message_intensity)
                        ),
                    )

                # TODO: This is hacky, do better.
                # TODO: Voxel still prints them flipped, fix!
                _bg_intensity = 1 - self._message_intensity if self._message_intensity else 0.7
                char: str = colored(
                    LOWER_PIXEL_CHAR if self.game.mode == GameMode.PHYSICS_2D else UPPER_PIXEL_CHAR,
                    color=extract_color_from_string(self._screen_grid[y][x]).with_intensity(
                        _bg_intensity
                    ),
                    bg_color=extract_bg_color_from_string(self._screen_grid[y][x]).with_intensity(
                        _bg_intensity
                    ),
                )

                if y == starting_border_y:
                    if x == starting_border_x:
                        char = _border_col(DoubleLines.UL)
                    elif x == ending_border_x - 1:
                        char = _border_col(DoubleLines.UR)
                    else:
                        char = _border_col(DoubleLines.H)
                elif y == ending_border_y - 1:
                    if x == starting_border_x:
                        char = _border_col(DoubleLines.LL)
                    elif x == ending_border_x - 1:
                        char = _border_col(DoubleLines.LR)
                    else:
                        char = _border_col(DoubleLines.H)
                elif x == starting_border_x or x == ending_border_x - 1:
                    char = _border_col(DoubleLines.V)

                self._screen_grid[y][x] = char

        # Add actual message content
        for msg_idx, row in enumerate(message_parts):
            # Message position
            starting_row_x = round(mid_x - len(row) / 2)
            ending_row_x = round(mid_x + len(row) / 2)

            for index, x in enumerate(range(starting_row_x, ending_row_x + 1)):
                new_y_idx = mid_y + msg_idx

                def _c(index: int) -> str:
                    return colored(
                        row[index] if index < len(row) else self._screen_grid[new_y_idx][x],
                        color=_MESSAGE_TEXT_COLOR,
                        bg_color=extract_bg_color_from_string(
                            self._screen_grid[new_y_idx][x]
                        ).with_intensity(1 - self._message_intensity)
                        if self._screen_grid[new_y_idx][x] != EMPTY_SPACE
                        else RGB(0, 0, 0, 0),
                    )

                self._screen_grid[new_y_idx][x] = _c(index)

        return (
            PointI(starting_border_x, starting_border_y),
            PointI(ending_border_y, ending_border_y),
        )

    def _set_2d_mode(self):
        self.antialiasing = True
        self._set_resolution(PointI(X_RESOLUTION_2D, Y_RESOLUTION_2D))
        self._set_max_fps(MAX_FPS_2D)

    def _set_physics_mode(self):
        # Handled in-engine
        self.antialiasing = False
        self._set_max_fps(MAX_FPS_PHYSICS)
        # FAQ: Why Y_RES/2? Each console character represent 2 "pixels" with LOWER_PIXEL_CHAR and a bg color for the empty space
        self._set_resolution(
            PointI(
                X_RESOLUTION_PHYSICS,
                round(Y_RESOLUTION_PHYSICS / 2),
            )
        )

    def _set_3d_mode(self):
        self.antialiasing = True
        self._set_max_fps(MAX_FPS_3D)
        self._set_resolution(PointI(X_RESOLUTION_3D, Y_RESOLUTION_3D))

    def _set_max_fps(self, fps: float) -> None:
        self._curr_fps = fps

    def _set_resolution(self, resolution: PointI) -> None:
        self.curr_x_resolution = resolution.x
        self.curr_y_resolution = resolution.y

    def _get_hud_string(self, player: Player2D | Player3D | PlayerBlob) -> str:
        hud = ""

        # Horrible branching
        if isinstance(player, Player3D):
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

            hud += f"{colored('KEYS REFERENCE', Yellow(0.9))}: "
            hud += f"FOV (-/+): {_c(fov_incr_key)}, {_c(fov_decr_key)}{SEPARATOR}"
            hud += f"X (-/+): {_c(decr_x_key)}, {_c(incr_x_key)}{SEPARATOR}"
            hud += f"Y (-/+): {_c(decr_y_key)}, {_c(incr_y_key)}{SEPARATOR}"
            hud += f"Visibility (-/+): {_c(decr_fog_key)}, {_c(incr_vis_key)}{BR}{SEPARATOR}"
            hud += f"Mode: {_c(mode_key)}{SEPARATOR}"
            hud += f"Shuffle!: {_c(shuffle_key)}{SEPARATOR}"
            hud += f"Curr pos: {colored((f'({int(player.position.x)},{int(player.position.y)},{int(player.position.z or 0)})'))}{SEPARATOR}"
            hud += f"Angle: {colored((f'({int(player.angle.x)},{int(player.angle.y)},{int(player.angle.z or 0)})'))}{SEPARATOR}"

            return hud

        if isinstance(player, PlayerBlob):
            hud += f"Velocity: ({round(player.velocity.x, 1)},{round(player.velocity.y, 1)}){SEPARATOR}"
            return hud

        health = player.get_health()

        hud = "Score: " + str(player.points) + " | Health: " + health
        hud += " | Pos: (" + str(player.position.x) + ", " + str(player.position.y) + ") | Vy: "
        hud += str(round(player.falling_velocity, 3))

        return hud

    ##############
    # PLAYER INPUT
    ##############
    def handle_keyboard_input(self) -> None:
        if self.game.mode == GameMode.PLATFORMER_V1:
            return

        self._increase_x_resolution()
        self._decrease_x_resolution()
        self._increase_y_resolution()
        self._decrease_y_resolution()

    # TODO: increase res functionality is broken, fix
    @on_key_press(DisplayKeys.INCREASE_X_RESOLUTION)
    def _increase_x_resolution(self):
        self.modify_resolution(VectorI(1, 0))

    @on_key_press(DisplayKeys.DECREASE_X_RESOLUTION)
    def _decrease_x_resolution(self):
        self.modify_resolution(VectorI(-1, 0))

    @on_key_press(DisplayKeys.INCREASE_Y_RESOLUTION)
    def _increase_y_resolution(self):
        self.modify_resolution(VectorI(0, 1))

    @on_key_press(DisplayKeys.DECREASE_Y_RESOLUTION)
    def _decrease_y_resolution(self):
        self.modify_resolution(VectorI(0, -1))
