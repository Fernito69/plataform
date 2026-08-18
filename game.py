import random
import time

from constants import FPS_2D
from display import Display
from entities.base import Entity2D
from entities.player2d import Player2D
from level_2d import Level2D
from model.game import GameStatus
from model.keyboard import DisplayKeys, KeyboardKeys, MenuKeys
from model.player import PlayerStatus
from terminal import on_key_press
from three_d_renderer.constants import FPS_3D
from three_d_renderer.entities.player3d import Player3D
from three_d_renderer.legacy_renderer import LegacyRenderer
from three_d_renderer.renderer_v2 import RendererV2


# TODO: Game should not handle the 2D game directly, it should be a subclass like the 3D renderer
class Game:
    status: GameStatus

    _curr_fps: int
    _current_level_index: int

    # TODO: refactor this into its own renderere
    player2d: Player2D
    levels: list[Level2D]

    display: Display

    # TODO: this should actuaklly go in Display, together with 2D renderer when refactored
    legacy_renderer: LegacyRenderer
    renderer_v2: RendererV2

    _pressed_key_map: dict[KeyboardKeys, bool] = {}

    def __init__(
        self,
        player_2d: Player2D,
        player_3d: Player3D,
        levels: list[Level2D],
        current_level_index: int = 0,
    ):
        self.levels = levels
        self._current_level_index = current_level_index

        self.player2d = player_2d
        self.player2d.set_curr_level(levels[current_level_index])
        self.display = Display(levels[current_level_index])
        self.status = GameStatus.MODE_3D
        self._curr_fps = FPS_3D
        self.display.set_3d_resolution()
        self.legacy_renderer = LegacyRenderer(player=player_3d, display=self.display)
        self.renderer_v2 = RendererV2(player=player_3d, display=self.display)

    def _check_game_status(self) -> None:
        match self.status:
            case GameStatus.QUIT:
                message = "BYE BYE"
                self.display.print_message(message)
                self.status = GameStatus.GAMEOVER

        self._check_player_status()

    def _check_player_status(self) -> None:
        for player in [self.player2d, self.renderer_v2.player, self.legacy_renderer.player]:
            message: str = ""

            match player.status:
                case PlayerStatus.DEAD:
                    message = "GAME OVER"

            if message != "":
                self.display.print_message(message)
                self.status = GameStatus.GAMEOVER

        if self.player2d.status == PlayerStatus.END_LEVEL_2D:
            message = "YOU WON!!! :D"
            self.display.print_message(message)
            self.status = GameStatus.GAMEOVER

    def _compute_actions_and_add_to_screen(self, entity: Entity2D) -> None:
        entity.do_your_thing()
        self.display._add_2d_entity_to_matrix(entity)

    def _frame_delay(self) -> None:
        time.sleep(1 / self._curr_fps)

    def _print_game(self) -> None:
        self.display.print_curr_screen(self.player2d)

    def game_loop(self) -> None:
        self._frame_delay()
        self.handle_player_input()

        # TODO: this should not happen here, do properly
        if self.status == GameStatus.MODE_3D:
            self._check_game_status()
            self.legacy_renderer.player.handle_player_input()
            return self.legacy_renderer.visualize_scenario()

        if self.status == GameStatus.MODE_3D_V2:
            self._check_game_status()
            self.renderer_v2.player.handle_player_input()
            return self.renderer_v2.render_v2()

        # 2D mode is handled here, refactor. 
        self.player2d.handle_player_input()
        self.display.populate_level_into_matrix()

        self._compute_actions_and_add_to_screen(self.player2d)

        for enemy in self.levels[self._current_level_index].enemies:
            self._compute_actions_and_add_to_screen(enemy)

        for exit in self.levels[self._current_level_index].exits:
            self._compute_actions_and_add_to_screen(exit)

        self._print_game()

    # Input methods
    # TODO: all display methods should go in Display class
    @on_key_press(MenuKeys.QUIT)
    def _quit(self):
        self.status = GameStatus.QUIT
        # TODO: fix the quit loop: check why the message is not being printed
        raise

    @on_key_press(MenuKeys.SWITCH_2D_MODE, act_once_per_press=True)
    def _switch_2d_mode(self):
        self.status = GameStatus.MODE_2D
        self.display.set_2d_resolution()
        # TODO: this should be part of Display, and go into the method .set_2d_resolution()
        self._curr_fps = FPS_2D

    @on_key_press(MenuKeys.SWITCH_3D_MODE, act_once_per_press=True)
    def _switch_3d_mode(self):
        self.status = GameStatus.MODE_3D
        self.display.set_3d_resolution()
        # TODO: this should be part of Display, and go into the method .set_3d_resolution()
        self._curr_fps = FPS_3D

    @on_key_press(DisplayKeys.SWITCH_RENDERING_MODE, act_once_per_press=True)
    def _switch_rendering_mode(self):
        self.status = (
            GameStatus.MODE_3D if self.status == GameStatus.MODE_3D_V2 else GameStatus.MODE_3D_V2
        )
        self._curr_fps = FPS_3D

    @on_key_press(DisplayKeys.INCREASE_X_RESOLUTION)
    def _increase_x_resolution(self):
        self.display.modify_resolution((1, 0))

    @on_key_press(DisplayKeys.DECREASE_X_RESOLUTION)
    def _decrease_x_resolution(self):
        self.display.modify_resolution((-1, 0))

    @on_key_press(DisplayKeys.INCREASE_Y_RESOLUTION)
    def _increase_y_resolution(self):
        self.display.modify_resolution((0, 1))

    @on_key_press(DisplayKeys.DECREASE_Y_RESOLUTION)
    def _decrease_y_resolution(self):
        self.display.modify_resolution((0, -1))

    @on_key_press(DisplayKeys.SWITCH_ANTIALIASING, act_once_per_press=True)
    def _switch_antialiasing(self):
        self.display.antialiasing = not self.display.antialiasing

    @on_key_press(DisplayKeys.INCREASE_VISIBILITY)
    def _increase_visibility(self):
        # TODO: I don't like this, should be unified. Same for all the rest:
        self.legacy_renderer.visibility_threshold += 5
        self.renderer_v2.visibility_threshold += 5

    @on_key_press(DisplayKeys.DECREASE_VISIBILITY)
    def _decrease_visibility(self):
        self.legacy_renderer.visibility_threshold -= 5
        self.renderer_v2.visibility_threshold -= 5

    @on_key_press(DisplayKeys.DECREASE_FOV)
    def _decrease_fov(self):
        self.legacy_renderer.fov -= 5
        self.renderer_v2.fov -= 5

    @on_key_press(DisplayKeys.INCREASE_FOV)
    def _increase_fov(self):
        self.legacy_renderer.fov += 5
        self.renderer_v2.fov += 5

    @on_key_press(DisplayKeys.SHUFFLE_COLORS, act_once_per_press=True)
    def _shuffle_colors(self):
        for r in [self.legacy_renderer, self.renderer_v2]:
            r.colors = sorted(
                r.colors,
                key=lambda _: 0.5 - random.random(),
            )

    def handle_player_input(self):
        self._quit()
        self._switch_rendering_mode()
        self._switch_2d_mode()
        self._switch_3d_mode()

        self._increase_fov()
        self._decrease_fov()

        if self.status == GameStatus.MODE_2D:
            return

        self._increase_x_resolution()
        self._decrease_x_resolution()
        self._increase_y_resolution()
        self._decrease_y_resolution()

        self._increase_visibility()
        self._decrease_visibility()

        self._shuffle_colors()

    def _set_pressed_key(self, key: KeyboardKeys, val: bool):
        self._pressed_key_map[key] = val
