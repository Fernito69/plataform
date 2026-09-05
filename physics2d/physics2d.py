from typing import TYPE_CHECKING

from display import Display
from factories.theme import DEFAULT_CHAR, RGB
from model.base import PointF
from model.keyboard import MovementKeys, PhysicsKey
from model.shared import Engine, KeyboardHandler
from model.theme import LOWER_PIXEL_CHAR
from physics2d.entities.player_blob import PlayerBlob
from physics2d.model.shared import RenderInfo
from physics2d.scenario.scenario import Scenario
from physics2d.scenario.scenarios import default_scenario
from terminal import on_key_press
from utils import colored

if TYPE_CHECKING:
    from game import Game

INITIAL_CORNER = PointF(0, 0)
CAMERA_MOVEMENT_SPEED = 2

# Determines at what level of RGB intensity the antialiasing effect starts to kick in
INTENSITY_BLEND_THRESHOLD = 1


class Physics2D(Engine, KeyboardHandler):
    display: Display
    screen_buffer: list[list[list[RenderInfo]]]

    screen_buffer_x_res: int
    screen_buffer_y_res: int

    player: PlayerBlob
    scenario: Scenario

    screen_corner: PointF

    def __init__(self, game: "Game", initial_screen_corner: PointF = INITIAL_CORNER):
        self.game = game
        self.screen_corner = initial_screen_corner
        self.display = self.game.display
        self.init_screen_buffer()

    def init_player(self, scenario: Scenario | None = None) -> None:
        self.player = self.game.player_blob
        self.scenario = scenario or default_scenario(self)
        self.player.set_scenario(self.scenario)

    def init_screen_buffer(self) -> None:
        self.screen_buffer_x_res = self.display.curr_x_resolution
        # Since we vertically stack 2 "sub-pixels" per terminal character ("▀" and "▄"),
        # our screen buffer is actually twice the y-resolution
        self.screen_buffer_y_res = self.display.curr_y_resolution * 2

        self.screen_buffer: list[list[list[RenderInfo]]] = []
        for y in range(self.screen_buffer_y_res):
            self.screen_buffer.append([])
            for _ in range(self.screen_buffer_x_res):
                self.screen_buffer[y].append([])

    def main_loop(self) -> None:
        self.init_screen_buffer()
        self.handle_keyboard_input()
        self.scenario.act()
        self.scenario.render()
        self.convert_screen_buffer_to_display_data()

    def is_visible(self, point: PointF) -> bool:
        return (
            point.x >= 0
            and point.x < self.screen_buffer_x_res
            and point.y >= 0
            and point.y < self.screen_buffer_y_res
        )

    def add_pixel_info_to_buffer(self, render_info: RenderInfo) -> None:
        new_x = round(render_info.point.x - self.screen_corner.x)
        new_y = round(render_info.point.y - self.screen_corner.y)

        if self.is_visible(PointF(new_x, new_y)):
            self.screen_buffer[new_y][new_x].append(render_info)

    def convert_screen_buffer_to_display_data(self) -> None:
        new_screen_grid: list[list[str]] = []
        # for p in self.scenario.pieces:
        #     if p.name == "LINEA MIA":
        #         self.display.debug_log(f"angle: PI*{p.angle} radians, {p.angular_velocity}")
        #         pass

        # TODO: for now, we assume y-res is always evenaaaaaaaq

        # Note the step is 2 here <─────────────────┐
        for y in range(0, self.screen_buffer_y_res, 2):
            new_y = int(y / 2)
            # we use the backwards index because, in the buffer, `going up == y++`,
            # whereas in the screen grid it's actually the opposite
            backwards_y = self.screen_buffer_y_res - 1 - y

            if len(new_screen_grid) <= new_y:
                new_screen_grid.append([])

            for x in range(self.screen_buffer_x_res):
                upper_pixel_info = self.screen_buffer[backwards_y - 1][x]
                lower_pixel_info = self.screen_buffer[backwards_y][x]

                if not upper_pixel_info and not lower_pixel_info:
                    new_screen_grid[new_y].append(DEFAULT_CHAR)
                    continue

                upper_color = Physics2D._compute_subpixel_color(upper_pixel_info)
                lower_color = Physics2D._compute_subpixel_color(lower_pixel_info)

                new_screen_grid[new_y].append(
                    colored(
                        LOWER_PIXEL_CHAR,
                        color=upper_color,
                        bg_color=lower_color,
                    )
                )

        self.display.put_screen_content(new_screen_grid)
        self.display.print_curr_screen(self.player)

    def handle_keyboard_input(self) -> None:
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
        self.screen_corner = (self.screen_corner + PointF(0, CAMERA_MOVEMENT_SPEED)).as_point()

    @on_key_press(MovementKeys.DOWN)
    def _move_screen_down(self):
        self.screen_corner = (self.screen_corner + PointF(0, -CAMERA_MOVEMENT_SPEED)).as_point()

    @on_key_press(MovementKeys.LEFT)
    def _move_screen_left(self):
        self.screen_corner = (self.screen_corner + PointF(-CAMERA_MOVEMENT_SPEED, 0)).as_point()

    @on_key_press(MovementKeys.RIGHT)
    def _move_screen_right(self):
        self.screen_corner = (self.screen_corner + PointF(CAMERA_MOVEMENT_SPEED, 0)).as_point()

    @on_key_press(PhysicsKey.RESET_CAMERA)
    def _reset_camera(self):
        self.screen_corner = PointF(0, 0)

    @staticmethod
    def _compute_subpixel_color(info_list: list[RenderInfo]) -> RGB:
        curr_index = 0

        def _get_color(il: list[RenderInfo], idx: int):
            if len(il) <= idx:
                return RGB(0, 0, 0)

            return il[idx].color.with_intensity_v2(
                max(
                    0,
                    1 - (il[idx]).distance_to_pixel_center,
                )
            )

        curr_color = _get_color(info_list, curr_index)
        curr_index += 1

        while curr_index < len(info_list) and curr_color.intensity < INTENSITY_BLEND_THRESHOLD:
            next_object_color = _get_color(info_list, curr_index).with_intensity(
                (INTENSITY_BLEND_THRESHOLD - curr_color.intensity) / INTENSITY_BLEND_THRESHOLD
            )
            # TODO: check if this works as intended
            curr_color = RGB(*(min(255, c) for c in curr_color + next_object_color))
            curr_index += 1

        return curr_color
