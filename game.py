import time

from display import Display
from model.game import GameStatus
from model.keyboard import DisplayKeys, MenuKeys
from model.player import PlayerStatus
from model.shared import KeyboardHandler
from physics2d.constants import FPS_PHYSICS
from physics2d.physics2d import Physics2D
from platformer_v1.constants import FPS_2D
from platformer_v1.entities.player2d import Player2D
from platformer_v1.platformer_v1 import PlatformerV1
from terminal import on_key_press
from three_d_renderer.constants import FPS_3D
from three_d_renderer.entities.player3d import Player3D
from three_d_renderer.legacy_3d_renderer import Legacy3DRenderer
from three_d_renderer.renderer_3d_v2 import Renderer3DV2
from three_d_renderer.scenario.level_3d import Level3D
from utils import shuffle_list


class Game(KeyboardHandler):
    status: GameStatus

    # TODO: should go in respective renderer
    levels_3d: list[Level3D]

    display: Display

    # TODO: this should actuaklly go in Display, together with 2D renderer when refactored.
    # Maybe renderer is not the right term for these classes? Or they should have a Game3D master
    legacy_3d_renderer: Legacy3DRenderer
    renderer_3d_v2: Renderer3DV2

    # 2D
    platformer_v1: PlatformerV1
    physics_2d: Physics2D

    def __init__(
        self,
        status: GameStatus = GameStatus.MODE_PHYSICS_2D,
    ):
        self.player2d = Player2D(1)
        self.player3d = Player3D(1)

        self.display = Display(
            fps=FPS_PHYSICS,
        )
        self.status = status
        # TODO: deprecate, use always display.fps
        self._curr_fps = FPS_PHYSICS
        self.display.set_physics_resolution()

        self.platformer_v1 = PlatformerV1(self)
        self.physics_2d = Physics2D(self)

        self.legacy_3d_renderer = Legacy3DRenderer(self)
        self.renderer_3d_v2 = Renderer3DV2(self)

        # hardcoded cool initial place
        self.player3d.position = (18, 84, -33)

    def _check_game_status(self) -> None:
        match self.status:
            case GameStatus.QUIT:
                message = "BYE BYE"
                self.display.print_message(message)
                self.status = GameStatus.GAMEOVER

        self._check_player_status()

    def _check_player_status(self) -> None:
        for player in [self.player2d, self.player3d]:
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

    def _frame_delay(self) -> None:
        time.sleep(1 / self._curr_fps)

    def game_loop(self) -> None:
        self._frame_delay()
        self.handle_player_input()
        self._check_game_status()

        if self.status == GameStatus.MODE_PHYSICS_2D:
            self.physics_2d.init_screen_buffer()
            self.physics_2d.handle_player_input()
            return self.physics_2d.game_loop()

        # TODO: this should not happen here, do properly
        if self.status == GameStatus.MODE_3D:
            self.player3d.handle_player_input()
            return self.legacy_3d_renderer.visualize_scenario()

        if self.status == GameStatus.MODE_3D_V2:
            self.player2d.handle_player_input()
            return self.renderer_3d_v2.render_v2()

        self.platformer_v1.game_loop()

    # Input methods
    # TODO: all display methods should go in Display class, or Three3d, whatever fits
    @on_key_press(MenuKeys.QUIT)
    def _quit(self):
        self.status = GameStatus.QUIT
        # TODO: fix the quit loop: check why the message is not being printed
        raise

    @on_key_press(MenuKeys.SWITCH_PHYSICS_2D_MODE, act_once_per_press=True)
    def _switch_physics2d_mode(self):
        self.status = GameStatus.MODE_PHYSICS_2D
        self._curr_fps = FPS_2D

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
        if self.status == GameStatus.MODE_3D:
            self.legacy_3d_renderer.reset_screen_buffer()
            self.legacy_3d_renderer.draw_screen_border()
        else:
            self.renderer_3d_v2.reset_screen_buffer()
            self.renderer_3d_v2.empty_screen_data()
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
        self.legacy_3d_renderer.visibility_threshold += 5
        self.renderer_3d_v2.visibility_threshold += 5

    @on_key_press(DisplayKeys.DECREASE_VISIBILITY)
    def _decrease_visibility(self):
        self.legacy_3d_renderer.visibility_threshold -= 5
        self.renderer_3d_v2.visibility_threshold -= 5

    @on_key_press(DisplayKeys.DECREASE_FOV)
    def _decrease_fov(self):
        self.legacy_3d_renderer.fov -= 5
        self.renderer_3d_v2.fov -= 5

    @on_key_press(DisplayKeys.INCREASE_FOV)
    def _increase_fov(self):
        self.legacy_3d_renderer.fov += 5
        self.renderer_3d_v2.fov += 5

    @on_key_press(DisplayKeys.SHUFFLE_COLORS, act_once_per_press=True)
    def _shuffle_colors(self):
        renderers = [self.legacy_3d_renderer, self.renderer_3d_v2]

        new_colors = sorted(
            renderers[0].colors,
            key=shuffle_list,
        )

        for r in renderers:
            r.colors = new_colors

    @on_key_press(MenuKeys.TOGGLE_ROTATION, act_once_per_press=True)
    def _toggle_rotation(self) -> None:
        if not self.player3d.curr_level:
            return
        self.player3d.curr_level.toggle_rotation()

    def handle_player_input(self) -> None:
        self._quit()
        self._switch_rendering_mode()
        self._switch_2d_mode()
        self._switch_3d_mode()
        self._switch_physics2d_mode()
        self._toggle_rotation()

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
