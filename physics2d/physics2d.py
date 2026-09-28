from typing import TYPE_CHECKING

from display import Display
from factories.theme import DEFAULT_CHAR, RGB
from model.base import PointF, ScreenPos
from model.game import GameMode
from model.keyboard import MenuKeys, MovementKeys, PhysicsKey
from model.shared import Engine, KeyboardHandler
from model.theme import LOWER_PIXEL_CHAR
from physics2d.entities.model.shared import BackgroundGenerator, ScenarioGenerator
from physics2d.entities.player_blob import PlayerBlob
from physics2d.model.shared import RenderInfo
from physics2d.scenario.backgrounds.saturn_rings import get_saturn_rings
from physics2d.scenario.backgrounds.sea_background import get_sea_background
from physics2d.scenario.backgrounds.starry_background import get_starry_background
from physics2d.scenario.scenario import Scenario
from physics2d.scenario.scenarios.first_level import first_level
from physics2d.scenario.scenarios.test_scenario import test_scenario
from system import on_key_press
from utils import colored

if TYPE_CHECKING:
    from game import Game

INITIAL_CORNER = PointF(0, 0)
CAMERA_MOVEMENT_SPEED = 2


class Physics2D(Engine, KeyboardHandler):
    _display: Display
    _screen_buffer: list[list[list[RenderInfo]]]

    _screen_buffer_x_res: int
    _screen_buffer_y_res: int

    player: PlayerBlob

    scenario: Scenario
    scenarios: list[ScenarioGenerator] = [
        test_scenario,
        first_level,
    ]
    curr_scenario_index: int

    backgrounds: list[BackgroundGenerator] = [
        get_starry_background,
        get_saturn_rings,
        get_sea_background,
    ]
    curr_bg_index: int

    screen_corner: PointF

    # For better performance
    low_quality_mode: bool

    def __init__(
        self,
        game: "Game",
        initial_screen_corner: PointF = INITIAL_CORNER,
        curr_scenario_index: int = 1,
        curr_bg_index: int = 0,
    ):
        self.game = game
        self.screen_corner = initial_screen_corner
        self._display = self.game.display
        self.low_quality_mode = False
        self.curr_scenario_index = curr_scenario_index
        self.curr_bg_index = curr_bg_index
        self.init_screen_buffer()

    def init_player(self, scenario: Scenario | None = None) -> None:
        self.player = self.game.player_blob
        # TODO: thisi is hacky, do properly
        _curr_weapon_idx = self.player._curr_weapon_index if self.player else 0
        _curr_thruster_idx = self.player._curr_thruster_index if self.player else 0

        self.scenario = scenario or self.scenarios[self.curr_scenario_index](
            self,
            self.backgrounds[self.curr_bg_index],
        )
        self.player.set_scenario(self.scenario)
        self.player._curr_weapon_index = _curr_weapon_idx
        self.player._curr_thruster_index = _curr_thruster_idx

    def init_screen_buffer(self) -> None:
        res = self._display.get_resolution()
        self._screen_buffer_x_res = res.x
        # Since we vertically stack 2 "sub-pixels" per terminal character ("▀" and "▄"),
        # our screen buffer is actually twice the terminal's y-resolution
        self._screen_buffer_y_res = res.y * 2

        self._screen_buffer: list[list[list[RenderInfo]]] = []
        for y in range(self._screen_buffer_y_res):
            self._screen_buffer.append([])
            for _ in range(self._screen_buffer_x_res):
                self._screen_buffer[y].append([])

    def main_loop(self) -> None:
        self.init_screen_buffer()
        self.scenario.background.set_previous_screen_corner(self.screen_corner)
        self.handle_keyboard_input()
        self.scenario.act()
        self.scenario.render()
        self.convert_screen_buffer_to_display_data()

    def get_resolution(self) -> ScreenPos:
        return ScreenPos(self._screen_buffer_x_res, self._screen_buffer_y_res)

    def is_visible(self, point: PointF) -> bool:
        return (
            point.x >= 0
            and point.x < self._screen_buffer_x_res
            and point.y >= 0
            and point.y < self._screen_buffer_y_res
        )

    def add_pixel_info_to_buffer(
        self,
        render_info: RenderInfo,
        absolute_positioning: bool = False,
    ) -> None:
        new_x = (
            round(render_info.point.x)
            if absolute_positioning
            else round(render_info.point.x - self.screen_corner.x)
        )
        new_y = (
            round(render_info.point.y)
            if absolute_positioning
            else round(render_info.point.y - self.screen_corner.y)
        )

        if self.is_visible(PointF(new_x, new_y)):
            self._screen_buffer[new_y][new_x].append(render_info)

    def convert_screen_buffer_to_display_data(self) -> None:
        new_screen_grid: list[list[str]] = []
        # for p in self.scenario.pieces:
        #     if p.name == "LINEA MIA":
        #         self.display.debug_log(f"angle: PI*{p.angle} radians, {p.angular_velocity}")
        #         pass

        # TODO: for now, we assume y-res is always evenaaaaaaaq
        # Note the step is 2 here <─────────────────┐
        for y in range(0, self._screen_buffer_y_res, 2):
            new_y = int(y / 2)
            # we use the backwards index because, in the buffer, `going up == y++`,
            # whereas in the screen grid it's actually the opposite
            backwards_y = self._screen_buffer_y_res - 1 - y

            if len(new_screen_grid) <= new_y:
                new_screen_grid.append([])

            for x in range(self._screen_buffer_x_res):
                upper_pixel_info = self._screen_buffer[backwards_y - 1][x]
                lower_pixel_info = self._screen_buffer[backwards_y][x]

                if not upper_pixel_info and not lower_pixel_info:
                    new_screen_grid[new_y].append(DEFAULT_CHAR)
                    continue

                upper_color = Physics2D._compute_subpixel_color(upper_pixel_info)
                lower_color = Physics2D._compute_subpixel_color(lower_pixel_info)

                # TODO: use a special algorithm to detect when to use special chars, e.g., ▞, `▛`, `▜`
                char = LOWER_PIXEL_CHAR

                new_screen_grid[new_y].append(
                    colored(
                        char,
                        color=upper_color,
                        bg_color=lower_color,
                    )
                )

        self._display.put_screen_content(new_screen_grid)
        self._display.print_curr_screen(self.player)

    def handle_keyboard_input(self) -> None:
        self._reset_scenario()
        self._move_screen_down()
        self._move_screen_up()
        self._move_screen_left()
        self._move_screen_right()
        self._reset_camera()
        self._cycle_scenario_background()
        self._cycle_scenario()

    @on_key_press(PhysicsKey.RESET_SCENARIO, act_once_per_press=True)
    def _reset_scenario(self):
        self.init_player()

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

    @on_key_press(MenuKeys.CYCLE_LEVELS, act_once_per_press=True)
    def _cycle_scenario(self) -> None:
        if self.game.mode != GameMode.PHYSICS_2D:
            return

        next_idx = (self.curr_scenario_index + 1) % len(self.scenarios)
        self.curr_scenario_index = next_idx
        self.scenario = self.scenarios[next_idx](
            self,
            self.backgrounds[self.curr_bg_index],
        )
        self.init_player()

    @on_key_press(MenuKeys.CYCLE_BACKGROUND, act_once_per_press=True)
    def _cycle_scenario_background(self) -> None:
        if self.game.mode != GameMode.PHYSICS_2D:
            return

        next_idx = (self.curr_bg_index + 1) % len(self.backgrounds)
        self.curr_bg_index = next_idx
        self.scenario.background = self.backgrounds[next_idx](self)

    @staticmethod
    def _compute_subpixel_color(info_list: list[RenderInfo]) -> RGB:
        curr_index = 0

        def _get_color(il: list[RenderInfo], idx: int):
            # TODO: do we need this safeguard?
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

        covers_everything = curr_color.intensity >= 1
        is_transparent = curr_color.opacity < 1

        while curr_index < len(info_list):
            _next_raw_color = _get_color(info_list, curr_index)
            _prev_color = curr_color.copy()

            covers_everything = curr_color.intensity >= 1
            is_transparent = curr_color.opacity < 1

            if covers_everything and not is_transparent:
                return curr_color

            curr_index += 1

            # TODO: I'm sure you can generalize, but let's play it safe first with cases
            # case 1:
            if not covers_everything and not is_transparent:
                curr_color = curr_color + _next_raw_color.with_intensity_v2(
                    (1 - curr_color.intensity) * _next_raw_color.opacity
                )

            # TODO: case 3 works well, except when more than 1 transparent tile stacked together, then the opacities kinda stack up as intensities

            # case 2:
            elif covers_everything and is_transparent:
                curr_color = curr_color.with_intensity_v2(
                    curr_color.opacity
                ) + _next_raw_color.with_intensity_v2(
                    (1 - curr_color.opacity) * _next_raw_color.opacity
                )

            # case 3:
            elif not covers_everything and is_transparent:
                # This is not perfect, but good enough it seems
                _factor = curr_color.opacity * curr_color.intensity
                curr_color = (
                    curr_color.with_intensity_v2(_factor)
                    + _next_raw_color.with_intensity_v2(1 - _factor) * _next_raw_color.opacity
                )

            # TODO: monitor this optimization, not sure if we could be missing some contributions like this
            if curr_color == _prev_color:
                break

            curr_index += 1

        # if it's the last in the list and it's transparent, check againstbackground
        if len(info_list) > 0 and info_list[-1].color.opacity < 1:
            curr_color = curr_color.with_intensity_v2(curr_color.opacity)

        return curr_color
