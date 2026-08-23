from typing import TYPE_CHECKING

from display import Display
from factories.theme import DEFAULT_CHAR, RGB
from model.theme import LOWER_PIXEL_CHAR
from physics2d.model.base import RenderInfo
from physics2d.scenario.scenario import Scenario
from physics2d.scenario.scenarios import default_scenario
from utils import colored

if TYPE_CHECKING:
    from game import Game

R2 = 1.414


class Physics2D:
    display: Display
    screen_buffer: list[list[RenderInfo | None]]

    screen_buffer_x_res: int
    screen_buffer_y_res: int

    scenario: Scenario

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

        self.screen_buffer: list[list[RenderInfo | None]] = []
        for y in range(self.screen_buffer_y_res):
            self.screen_buffer.append([])
            for _ in range(self.screen_buffer_x_res):
                self.screen_buffer[y].append(None)

    def game_loop(self) -> None:
        self.scenario.render()
        self.convert_screen_buffer_to_display_data()

    def paint_pixel(self, render_info: RenderInfo) -> None:
        x = min(self.screen_buffer_x_res - 1, max(0, round(render_info.point[0])))
        y = min(self.screen_buffer_y_res - 1, max(0, round(render_info.point[1])))
        self.screen_buffer[y][x] = render_info

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

                def _get_intensity(info: RenderInfo):
                    return max(
                        1 - info.distance_to_pixel_center / R2,
                        0,
                    )

                upper_color = (
                    upper_pixel_info.color.with_intensity(_get_intensity(upper_pixel_info))
                    if upper_pixel_info
                    else RGB(0, 0, 0)
                )
                lower_color = (
                    lower_pixel_info.color.with_intensity(_get_intensity(lower_pixel_info))
                    if lower_pixel_info
                    else RGB(0, 0, 0)
                )

                new_screen_matrix[new_y].append(
                    colored(
                        LOWER_PIXEL_CHAR,
                        color=upper_color,
                        bg_color=lower_color,
                    )
                )

        self.display.put_screen_content(new_screen_matrix)
        self.display.print_curr_screen()
