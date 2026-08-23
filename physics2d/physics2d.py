from typing import TYPE_CHECKING

from display import Display
from model.theme import EMPTY_SPACE, LOWER_PIXEL_CHAR
from physics2d.model.base import RenderInfo
from physics2d.scenario.scenario import Scenario
from utils import colored

if TYPE_CHECKING:
    from game import Game


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
        self.init_screen_buffer()

    def init_screen_buffer(self) -> None:
        self.screen_buffer_x_res = self.display.curr_x_resolution * 2
        self.screen_buffer_y_res = self.display.curr_y_resolution * 2

        self.screen_buffer: list[list[RenderInfo | None]] = []
        for y in range(self.screen_buffer_y_res):
            self.screen_buffer.append([])
            for _ in range(self.screen_buffer_x_res):
                self.screen_buffer[y].append(None)

    def game_loop(self) -> None:
        self.render_scenario()

    def render_scenario(self) -> None:
        # Transform buffer into screen matrix
        new_screen_matrix: list[list[str]] = []
        # TODO: for now, we assume y-res is even
        # first_y_is_even: bool = self.display.curr_y_resolution - 1 % 2 == 0

        # Note the step is 2 here
        for y in range(0, self.screen_buffer_y_res - 1, 2):
            new_y = int(y / 2)
            backwards_y = self.screen_buffer_y_res - 1 - y

            if len(new_screen_matrix) <= new_y:
                new_screen_matrix.append([])

            for x in range(self.screen_buffer_x_res - 1):
                # raise NotImplementedError(
                #     f"SCREEN BUFFER y={len(self.screen_buffer)} x={
                #         len(self.screen_buffer[0])
                #     } | SCREEN MATRIX y={len(new_screen_matrix)} x={
                #         len(new_screen_matrix[0])
                #     } backwards_y={backwards_y}"
                # )

                upper_pixel_info = self.screen_buffer[backwards_y][x]
                lower_pixel_info = self.screen_buffer[backwards_y - 1][x]

                if not upper_pixel_info and not lower_pixel_info:
                    new_screen_matrix[new_y].append(EMPTY_SPACE)
                    continue

                new_screen_matrix[new_y][x] = colored(
                    LOWER_PIXEL_CHAR,
                    color=upper_pixel_info.color if upper_pixel_info else None,
                    bg_color=lower_pixel_info.color if lower_pixel_info else None,
                )

        self.display.put_screen_content(new_screen_matrix)
        self.display.print_curr_screen()
