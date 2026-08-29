from display import Display
from model.game import GameMode, GameStatus
from model.keyboard import DisplayKeys, MenuKeys
from model.player import PlayerStatus
from model.shared import KeyboardHandler
from physics2d.physics2d import Physics2D
from platformer_v1.entities.player2d import Player2D
from platformer_v1.platformer_v1 import PlatformerV1
from terminal import on_key_press
from three_d_renderer.entities.player3d import Player3D
from three_d_renderer.legacy_3d_renderer import VoxelRenderer
from three_d_renderer.renderer_3d_v2 import LineRenderer
from utils import shuffle_list


class Game(KeyboardHandler):
    display: Display

    status: GameStatus
    mode: GameMode

    """Game modes"""
    # 3D modes
    voxel_renderer: VoxelRenderer
    line_renderer: LineRenderer

    # 2D modes
    platformer_v1: PlatformerV1
    physics_engine: Physics2D

    def __init__(
        self,
        mode: GameMode = GameMode.MODE_PHYSICS_2D,
        status: GameStatus = GameStatus.RUNNING,
    ):
        self.status = status
        self.mode = mode

        self.display = Display()
        self.display.set_physics_mode()

        self.player2d = Player2D(1)
        self.player3d = Player3D(1)

        self.platformer_v1 = PlatformerV1(self)
        self.physics_engine = Physics2D(self)

        self.voxel_renderer = VoxelRenderer(self)
        self.line_renderer = LineRenderer(self)

        # hardcoded cool initial place
        self.player3d._position = (18, 84, -33)

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

    def main_loop(self) -> None:
        def _main_loop():
            self.handle_player_input()
            self._check_game_status()

            match self.mode:
                case GameMode.MODE_PHYSICS_2D:
                    self.physics_engine.init_screen_buffer()
                    self.physics_engine.handle_player_input()
                    return self.physics_engine.game_loop()

                case GameMode.MODE_3D:
                    self.player3d.handle_player_input()
                    return self.voxel_renderer.visualize_scenario()

                case GameMode.MODE_3D_V2:
                    self.player2d.handle_player_input()
                    return self.line_renderer.render_v2()

                case GameMode.MODE_2D:
                    return self.platformer_v1.game_loop()

        self.display.fps_throttle(_main_loop)

    # Input methods
    # TODO: all display methods should go in Display class, or Three3d, whatever fits
    @on_key_press(MenuKeys.QUIT)
    def _quit(self):
        self.status = GameStatus.QUIT
        # TODO: fix the quit loop: check why the message is not being printed
        raise

    @on_key_press(MenuKeys.SWITCH_PHYSICS_2D_MODE, act_once_per_press=True)
    def _switch_physics2d_mode(self):
        self.mode = GameMode.MODE_PHYSICS_2D
        self.display.set_physics_mode()

    @on_key_press(MenuKeys.SWITCH_2D_MODE, act_once_per_press=True)
    def _switch_2d_mode(self):
        self.mode = GameMode.MODE_2D
        self.display.set_2d_mode()

    @on_key_press(MenuKeys.SWITCH_3D_MODE, act_once_per_press=True)
    def _switch_3d_mode(self):
        self.mode = GameMode.MODE_3D
        self.display.set_3d_mode()

    @on_key_press(DisplayKeys.SWITCH_RENDERING_MODE, act_once_per_press=True)
    def _switch_rendering_mode(self):
        self.mode = GameMode.MODE_3D if self.status == GameMode.MODE_3D_V2 else GameMode.MODE_3D_V2
        if self.mode == GameMode.MODE_3D:
            self.voxel_renderer.reset_screen_buffer()
            self.voxel_renderer.draw_screen_border()
        else:
            self.line_renderer.reset_screen_buffer()
            self.line_renderer.empty_screen_data()

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
        self.voxel_renderer.visibility_threshold += 5
        self.line_renderer.visibility_threshold += 5

    @on_key_press(DisplayKeys.DECREASE_VISIBILITY)
    def _decrease_visibility(self):
        self.voxel_renderer.visibility_threshold -= 5
        self.line_renderer.visibility_threshold -= 5

    @on_key_press(DisplayKeys.DECREASE_FOV)
    def _decrease_fov(self):
        self.voxel_renderer.fov -= 5
        self.line_renderer.fov -= 5

    @on_key_press(DisplayKeys.INCREASE_FOV)
    def _increase_fov(self):
        self.voxel_renderer.fov += 5
        self.line_renderer.fov += 5

    @on_key_press(DisplayKeys.SHUFFLE_COLORS, act_once_per_press=True)
    def _shuffle_colors(self):
        renderers = [self.voxel_renderer, self.line_renderer]

        new_colors = sorted(
            renderers[0].colors,
            key=shuffle_list,
        )

        for r in renderers:
            r.colors = new_colors

    @on_key_press(MenuKeys.TOGGLE_ROTATION, act_once_per_press=True)
    def _toggle_rotation(self) -> None:
        if not self.player3d._curr_level:
            return
        self.player3d._curr_level.toggle_rotation()

    def handle_player_input(self) -> None:
        self._quit()
        self._switch_rendering_mode()
        self._switch_2d_mode()
        self._switch_3d_mode()
        self._switch_physics2d_mode()
        self._toggle_rotation()

        self._increase_fov()
        self._decrease_fov()

        if self.mode == GameMode.MODE_2D:
            return

        self._increase_x_resolution()
        self._decrease_x_resolution()
        self._increase_y_resolution()
        self._decrease_y_resolution()

        self._increase_visibility()
        self._decrease_visibility()

        self._shuffle_colors()
