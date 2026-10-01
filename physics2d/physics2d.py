from concurrent.futures import ThreadPoolExecutor
from typing import TYPE_CHECKING

from factories.theme import DEFAULT_CHAR, RGB
from model.base import PointF, ScreenPos
from model.game import GameMode
from model.keyboard import MenuKeys, MovementKeys, PhysicsKey
from model.shared import Engine, KeyboardHandler
from model.theme import LOWER_PIXEL_CHAR
from physics2d.entities.base import PhysicsEntity
from physics2d.entities.model.shared import BackgroundGenerator, ScenarioGenerator
from physics2d.entities.player_blob import PlayerBlob
from physics2d.entities.utils import apply_hp_bar_to_screen
from physics2d.model.frame import FrameSnapshot, HealthBarSnapshot
from physics2d.model.shared import BoundingBox, RenderInfo
from physics2d.scenario.backgrounds.dodeca_dyson import get_dodeca_dyson
from physics2d.scenario.backgrounds.saturn_rings import get_saturn_rings
from physics2d.scenario.backgrounds.starry_space import get_starry_space
from physics2d.scenario.backgrounds.void_space import get_void_space
from physics2d.scenario.scenario import Scenario
from physics2d.scenario.scenarios.color_test import color_test
from physics2d.scenario.scenarios.first_level import first_level
from physics2d.scenario.scenarios.test_scenario import test_scenario
from system import on_key_press
from utils import colored

if TYPE_CHECKING:
    from game import Game
    from physics2d.shape.base import Shape

INITIAL_CORNER = PointF(0, 0)
CAMERA_MOVEMENT_SPEED = 2

# Shapes this far outside the screen are still rendered, so nothing pops in
# at the edge and fast movers aren't culled a frame too early.
CULLING_GRACE_MARGIN = 8


def _get_render_info(entity) -> list[RenderInfo]:
    """Module-level so the pool isn't handed a closure over engine state."""
    return entity.get_render_info()


class Physics2D(Engine, KeyboardHandler):
    _screen_buffer: list[list[list[RenderInfo]]]

    _screen_buffer_x_res: int
    _screen_buffer_y_res: int

    player: PlayerBlob

    scenario: Scenario
    scenarios: list[ScenarioGenerator] = [
        test_scenario,
        first_level,
        color_test,
    ]
    curr_scenario_index: int

    backgrounds: list[BackgroundGenerator] = [
        get_starry_space,
        get_saturn_rings,
        get_dodeca_dyson,
        get_void_space,
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
        render_workers: int = 0,
    ):
        self.game = game
        self.screen_corner = initial_screen_corner
        self._display = self.game._display
        self.low_quality_mode = False
        self.curr_scenario_index = curr_scenario_index
        self.curr_bg_index = curr_bg_index
        self.init_screen_buffer()

        # Resolving an entity's pixels is independent per entity, so it can be
        # spread over a pool. Only actually parallel on a free-threaded
        # interpreter (python3.14t); under the GIL it just adds overhead.
        self._render_pool = (
            ThreadPoolExecutor(max_workers=render_workers, thread_name_prefix="render-info")
            if render_workers > 1
            else None
        )

    def compute_render_info_batch(self, entities: list) -> list[list[RenderInfo]]:
        """Resolve each entity's pixels, in the order they were given."""
        if self._render_pool is None:
            return [entity.get_render_info() for entity in entities]

        # `map` keeps input order, which the scatter in Scenario depends on.
        return list(self._render_pool.map(_get_render_info, entities))

    def shutdown(self) -> None:
        if self._render_pool is not None:
            self._render_pool.shutdown(wait=False, cancel_futures=True)
            self._render_pool = None

    def init_player(self, scenario: Scenario | None = None) -> None:
        self.player = self.game.player_blob
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
        self.render_frame(self.calculate_frame())

    def calculate_frame(self) -> FrameSnapshot:
        """Stage 1: advance the world and resolve it into a self-contained frame."""
        self.init_screen_buffer()
        self._calc_physics_and_compute_render_info()

        return self._take_frame_snapshot()

    def render_frame(self, frame: FrameSnapshot) -> None:
        """Stage 2: turn a frame into characters and push it to the terminal.

        Reads nothing but `frame`, so it can run while stage 1 is already
        working on the next one.
        """
        new_data = self._convert_screen_buffer_to_display_data(frame)
        new_data = self._add_health_bars(new_data, frame)
        self._send_data_to_display(new_data, frame)

    def _take_frame_snapshot(self) -> FrameSnapshot:
        # `init_screen_buffer` builds a brand new buffer every frame, so handing
        # this one over doesn't need a copy: stage 1 won't write to it again.
        return FrameSnapshot(
            screen_buffer=self._screen_buffer,
            x_res=self._screen_buffer_x_res,
            y_res=self._screen_buffer_y_res,
            health_bars=self._take_health_bar_snapshots(),
            hud=self._display.get_hud_content(self.player),
        )

    def _take_health_bar_snapshots(self) -> list[HealthBarSnapshot]:
        snapshots = [
            enemy.get_hp_bar_snapshot(with_special_chars=False)
            for enemy in self.scenario.enemies
            if enemy.show_health and self.is_in_screen(enemy.position)
        ]

        return [s for s in snapshots if s is not None]

    def is_in_screen(
        self,
        point_or_entity: PointF | PhysicsEntity,
        grace_margin: int = 0,
    ) -> bool:
        X_RES, Y_RES = self.get_resolution()

        # curr visible rectangle
        x_min = self.screen_corner.x - grace_margin
        x_max = self.screen_corner.x + X_RES + grace_margin
        y_min = self.screen_corner.y - grace_margin
        y_max = self.screen_corner.y + Y_RES + grace_margin

        if isinstance(point_or_entity, PhysicsEntity):
            return (
                point_or_entity.position.x + point_or_entity.radius >= x_min
                or point_or_entity.position.x - point_or_entity.radius < x_max
                or point_or_entity.position.y + point_or_entity.radius >= y_min
                or point_or_entity.position.y - point_or_entity.radius < y_max
            )

        return (
            point_or_entity.x >= x_min
            and point_or_entity.x < x_max
            and point_or_entity.y >= y_min
            and point_or_entity.y < y_max
        )

    def get_viewport(self, grace_margin: float = CULLING_GRACE_MARGIN) -> BoundingBox:
        """The visible rectangle in world coordinates."""
        X_RES, Y_RES = self.get_resolution()

        return BoundingBox(
            min_x=self.screen_corner.x - grace_margin,
            min_y=self.screen_corner.y - grace_margin,
            max_x=self.screen_corner.x + X_RES + grace_margin,
            max_y=self.screen_corner.y + Y_RES + grace_margin,
        )

    @staticmethod
    def is_worth_rendering(shape: "Shape", viewport: BoundingBox) -> bool:
        """Whether a shape can possibly land on screen.

        One box test here saves computing every pixel of a shape that is
        nowhere near the camera. Shapes that can't describe their own extent
        return no box, and those we always render.
        """
        box = shape.get_bounding_box()

        return box is None or box.overlaps(viewport)

    def _calc_physics_and_compute_render_info(self) -> None:
        self.scenario.background.update_previous_screen_corner(self.screen_corner)
        self.handle_keyboard_input()
        self.scenario.do_your_thing()
        self.scenario.compute_render_info()

    def _add_health_bars(
        self,
        data: list[list[str]],
        frame: FrameSnapshot,
    ) -> list[list[str]]:
        """since health bars are a pre-constructed string, we add them after rendering the scenario data"""

        for health_bar in frame.health_bars:
            apply_hp_bar_to_screen(data, health_bar)

        return data

    def get_resolution(self) -> ScreenPos:
        return ScreenPos(self._screen_buffer_x_res, self._screen_buffer_y_res)

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

        if (
            new_x >= 0
            and new_x < self._screen_buffer_x_res
            and new_y >= 0
            and new_y < self._screen_buffer_y_res
        ):
            self._screen_buffer[new_y][new_x].append(render_info)

    def _convert_screen_buffer_to_display_data(self, frame: FrameSnapshot) -> list[list[str]]:
        new_screen_grid: list[list[str]] = []
        screen_buffer = frame.screen_buffer

        # TODO: for now, we assume y-res is always even
        # Note the step is 2 here <─────────────────┐
        for y in range(0, frame.y_res, 2):
            new_y = int(y / 2)
            # we use the backwards index because, in the buffer, `going up == y++`,
            # whereas in the screen grid it's actually the opposite
            backwards_y = frame.y_res - 1 - y

            if len(new_screen_grid) <= new_y:
                new_screen_grid.append([])

            for x in range(frame.x_res):
                upper_pixel_info = screen_buffer[backwards_y - 1][x]
                lower_pixel_info = screen_buffer[backwards_y][x]

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

        return new_screen_grid

    def _send_data_to_display(
        self,
        new_screen_grid: list[list[str]],
        frame: FrameSnapshot,
    ) -> None:
        self._display.put_screen_content(new_screen_grid)
        self._display.print_curr_screen(hud=frame.hud)

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
