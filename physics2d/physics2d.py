from typing import TYPE_CHECKING

from display import Display
from factories.theme import DEFAULT_CHAR, RGB
from model.keyboard import PhysicsKey
from model.theme import LOWER_PIXEL_CHAR
from physics2d.model.base import RenderInfo
from physics2d.scenario.scenario import Scenario
from physics2d.scenario.scenarios import default_scenario
from terminal import on_key_press
from utils import colored, mix_colors

if TYPE_CHECKING:
    from game import Game


# TODO: place properly
def _get_intensity(info: RenderInfo) -> float:
    return max(
        0,
        1 - info.distance_to_pixel_center,
    )
    # TODO: fix this
    # * (1 - prev_info.color.intensity)
    # if prev_info is not None
    # else 1


# TODO: This won't work until we have a way of separating transparency from intensity
def get_color(info_list: list[RenderInfo]) -> RGB:
    curr_index = 0

    def _get_color(il: list[RenderInfo], idx: int):
        return il[idx].color.with_intensity_v2(_get_intensity(il[idx]))

    color = (
        _get_color(info_list, curr_index)
        if len(info_list) > curr_index
        else RGB(0, 0, 0, intensity=0)
    )

    curr_index += 1

    if color.intensity > 0.3 or curr_index >= len(info_list):
        return color

    color = mix_colors(
        [
            color.with_intensity(1),
            _get_color(info_list, curr_index),
        ]
    )

    return color


class Physics2D:
    display: Display
    screen_buffer: list[list[list[RenderInfo]]]

    screen_buffer_x_res: int
    screen_buffer_y_res: int

    scenario: Scenario

    _pressed_key_map: dict[PhysicsKey, bool] = {}

    def __init__(
        self,
        game: "Game",
    ):
        self.game = game
        self.display = self.game.display
        self.scenario = default_scenario(self)
        self.init_screen_buffer()

    def init_screen_buffer(self) -> None:
        self.display.set_physics_resolution()
        self.screen_buffer_x_res = self.display.curr_x_resolution * 2
        self.screen_buffer_y_res = self.display.curr_y_resolution * 2

        self.screen_buffer: list[list[list[RenderInfo]]] = []
        for y in range(self.screen_buffer_y_res):
            self.screen_buffer.append([])
            for _ in range(self.screen_buffer_x_res):
                self.screen_buffer[y].append([])

    def game_loop(self) -> None:
        self.scenario.act()
        self.scenario.render()
        self.convert_screen_buffer_to_display_data()

    def add_pixel_info_to_buffer(self, render_info: RenderInfo) -> None:
        if (
            render_info.point[0] < 0
            or render_info.point[0] > self.screen_buffer_x_res - 1
            or render_info.point[1] < 0
            or render_info.point[1] > self.screen_buffer_y_res - 1
        ):
            return

        x = round(render_info.point[0])
        y = round(render_info.point[1])

        self.screen_buffer[y][x].append(render_info)

    def convert_screen_buffer_to_display_data(self) -> None:
        new_screen_matrix: list[list[str]] = []

        # TODO: for now, we assume y-res is always even

        # Note the step is 2 here
        for y in range(0, self.screen_buffer_y_res, 2):
            new_y = int(y / 2)
            backwards_y = self.screen_buffer_y_res - 1 - y

            if len(new_screen_matrix) <= new_y:
                new_screen_matrix.append([])

            for x in range(self.screen_buffer_x_res):
                upper_pixel_info = self.screen_buffer[backwards_y - 1][x]
                lower_pixel_info = self.screen_buffer[backwards_y][x]

                if not upper_pixel_info and not lower_pixel_info:
                    new_screen_matrix[new_y].append(DEFAULT_CHAR)
                    continue

                upper_color = get_color(upper_pixel_info)
                lower_color = get_color(lower_pixel_info)

                new_screen_matrix[new_y].append(
                    colored(
                        LOWER_PIXEL_CHAR,
                        color=upper_color,
                        bg_color=lower_color,
                    )
                )

        self.display.put_screen_content(new_screen_matrix)
        self.display.print_curr_screen()

    def handle_player_input(self) -> None:
        self._reset_scenario()

    @on_key_press(PhysicsKey.RESET_SCENARIO, act_once_per_press=True)
    def _reset_scenario(self):
        self.scenario = default_scenario(self)

    def _set_pressed_key(self, key: PhysicsKey, val: bool):
        self._pressed_key_map[key] = val
