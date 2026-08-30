from typing import TYPE_CHECKING

from display import Display
from factories.theme import DEFAULT_CHAR, RGB
from model.base import Point2F
from model.keyboard import MovementKeys, PhysicsKey
from model.shared import Engine, KeyboardHandler
from model.theme import LOWER_PIXEL_CHAR
from physics2d.model.base import RenderInfo
from physics2d.scenario.scenario import Scenario
from physics2d.scenario.scenarios import default_scenario
from terminal import on_key_press
from utils import add_triplet, add_tuple, colored

if TYPE_CHECKING:
    from game import Game

INITIAL_CORNER = (0, 0)
CAMERA_MOVEMENT_SPEED = 2

# Determines "how much" antialiasing we have
INTENSITY_BLEND_THRESHOLD = 0.8


class Physics2D(Engine, KeyboardHandler):
    display: Display
    screen_buffer: list[list[list[RenderInfo]]]

    screen_buffer_x_res: int
    screen_buffer_y_res: int

    scenario: Scenario

    screen_corner: Point2F

    def __init__(self, game: "Game", initial_screen_corner: Point2F = INITIAL_CORNER):
        self.game = game
        self.screen_corner = initial_screen_corner
        self.display = self.game.display
        self.scenario = default_scenario(self)
        self.init_screen_buffer()

    def init_screen_buffer(self) -> None:
        self.screen_buffer_x_res = self.display.curr_x_resolution
        self.screen_buffer_y_res = self.display.curr_y_resolution * 2

        self.screen_buffer: list[list[list[RenderInfo]]] = []
        for y in range(self.screen_buffer_y_res):
            self.screen_buffer.append([])
            for _ in range(self.screen_buffer_x_res):
                self.screen_buffer[y].append([])

    def main_loop(self) -> None:
        self.init_screen_buffer()
        self.scenario.act()
        self.scenario.render()
        self.convert_screen_buffer_to_display_data()

    def is_visible(self, point: Point2F) -> bool:
        return (
            point[0] >= 0
            and point[0] < self.screen_buffer_x_res
            and point[1] >= 0
            and point[1] < self.screen_buffer_y_res
        )

    def add_pixel_info_to_buffer(self, render_info: RenderInfo) -> None:
        new_x = round(render_info.point[0] - self.screen_corner[0])
        new_y = round(render_info.point[1] - self.screen_corner[1])

        if self.is_visible((new_x, new_y)):
            self.screen_buffer[new_y][new_x].append(render_info)

    def convert_screen_buffer_to_display_data(self) -> None:
        new_screen_matrix: list[list[str]] = []
        # for p in self.scenario.pieces:
        #     if p.name == "LINEA MIA":
        #         self.display.debug_log(f"angle: PI*{p.angle} radians, {p.angular_velocity}")
        #         pass

        # TODO: for now, we assume y-res is always evenaaaaaaaq

        # Note the step is 2 here <─────────────────┐
        for y in range(0, self.screen_buffer_y_res, 2):
            # each pixel represented in the buffer lands
            # in the actual matrix as the same character actually,
            # with fg color occupying this part "▄" and bg color occupying this part "▀"
            # (or the other way around, who knows)
            # this trick allows us to have "pixels" with a conveniently more square ratio
            new_y = int(y / 2)
            # we use the backwards index because, in the buffer, `going up == y++`,
            # whereas in the screen matrix it's actually the opposite
            backwards_y = self.screen_buffer_y_res - 1 - y

            if len(new_screen_matrix) <= new_y:
                new_screen_matrix.append([])

            for x in range(self.screen_buffer_x_res):
                upper_pixel_info = self.screen_buffer[backwards_y - 1][x]
                lower_pixel_info = self.screen_buffer[backwards_y][x]

                if not upper_pixel_info and not lower_pixel_info:
                    new_screen_matrix[new_y].append(DEFAULT_CHAR)
                    continue

                upper_color = Physics2D._calculate_color_with_aa(upper_pixel_info)
                lower_color = Physics2D._calculate_color_with_aa(lower_pixel_info)

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
        self._move_screen_down()
        self._move_screen_up()
        self._move_screen_left()
        self._move_screen_right()
        self._reset_camera()

    @on_key_press(PhysicsKey.RESET_SCENARIO, act_once_per_press=True)
    def _reset_scenario(self):
        self.scenario = default_scenario(self)

    @on_key_press(MovementKeys.UP)
    def _move_screen_up(self):
        self.screen_corner = add_tuple(self.screen_corner, (0, CAMERA_MOVEMENT_SPEED))

    @on_key_press(MovementKeys.DOWN)
    def _move_screen_down(self):
        self.screen_corner = add_tuple(self.screen_corner, (0, -CAMERA_MOVEMENT_SPEED))

    @on_key_press(MovementKeys.LEFT)
    def _move_screen_left(self):
        self.screen_corner = add_tuple(self.screen_corner, (-CAMERA_MOVEMENT_SPEED, 0))

    @on_key_press(MovementKeys.RIGHT)
    def _move_screen_right(self):
        self.screen_corner = add_tuple(self.screen_corner, (CAMERA_MOVEMENT_SPEED, 0))

    @on_key_press(PhysicsKey.RESET_CAMERA)
    def _reset_camera(self):
        self.screen_corner = (0, 0)

    @staticmethod
    def _get_intensity(info: RenderInfo) -> float:
        return max(
            0,
            1 - info.distance_to_pixel_center,
        )

    @staticmethod
    def _calculate_color_with_aa(info_list: list[RenderInfo]) -> RGB:
        curr_index = 0

        def _get_color(il: list[RenderInfo], idx: int):
            return il[idx].color.with_intensity_v2(Physics2D._get_intensity(il[idx]))

        curr_color = (
            _get_color(info_list, curr_index) if len(info_list) > curr_index else RGB(0, 0, 0)
        )

        curr_index += 1

        while curr_index < len(info_list) and curr_color.intensity < INTENSITY_BLEND_THRESHOLD:
            next_object_color = _get_color(info_list, curr_index).with_intensity(
                (INTENSITY_BLEND_THRESHOLD - curr_color.intensity) / INTENSITY_BLEND_THRESHOLD
            )
            # TODO: fix this shit
            curr_color = (
                RGB(
                    *(
                        min(255, round(c))
                        for c in add_triplet(
                            (curr_color.r, curr_color.g, curr_color.b),
                            (next_object_color.r, next_object_color.g, next_object_color.b),
                        )
                    )
                )
                if curr_index < 2
                else RGB(0, 0, 0)
            )
            curr_index += 1

        return curr_color
