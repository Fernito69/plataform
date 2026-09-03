from display import Display
from model.base import PointF
from model.game import GameMode, GameStatus
from model.keyboard import DisplayKeys, MenuKeys
from model.player import PlayerStatus
from model.shared import Engine, KeyboardHandler
from model.theme import BR
from physics2d.entities.player_blob import PlayerBlob
from physics2d.physics2d import Physics2D
from platformer_v1.entities.player2d import Player2D
from platformer_v1.platformer_v1 import PlatformerV1
from terminal import on_key_press
from three_d_renderer.entities.player3d import Player3D
from three_d_renderer.line_renderer import LineRenderer
from three_d_renderer.voxel_renderer import VoxelRenderer
from utils import shuffle_list

_WELCOME_TIMER = 150
_WELCOME_TEXT: str = str.join(
    BR,
    [
        "Welcome! :)",
        "",
        "Press 1 for legacy platformer",
        "Press 2 for 3D mode",
        "Press V to switch 3D rendering mode",
        "Press P for the 2D physics engine",
    ],
)


class Game(Engine, KeyboardHandler):
    display: Display

    status: GameStatus
    mode: GameMode

    """Game modes"""
    # 3D modes
    player3d: Player3D
    voxel_renderer: VoxelRenderer
    line_renderer: LineRenderer

    # 2D modes
    player2d: Player2D
    platformer_v1: PlatformerV1

    player_blob: PlayerBlob
    physics_engine: Physics2D

    _welcome_message_timer: int = _WELCOME_TIMER

    def __init__(
        self,
        mode: GameMode = GameMode.PHYSICS_2D,
    ):
        self.status = GameStatus.RUNNING
        self.mode = mode

        self.display = Display(self)

        self.player2d = Player2D(1)
        self.platformer_v1 = PlatformerV1(self)

        self.player3d = Player3D(1)
        self.voxel_renderer = VoxelRenderer(self)
        self.line_renderer = LineRenderer(self)

        self.physics_engine = Physics2D(self)
        self.player_blob = PlayerBlob(self.physics_engine)
        self.physics_engine.init_player()

        # hardcoded cool initial place
        self.player3d.position = PointF(9, -44, -33)

    def main_loop(self) -> None:
        def _main_loop():
            self._check_game_status()
            self._handle_welcome_message()

            self.handle_keyboard_input()
            self.display.handle_keyboard_input()

            match self.mode:
                case GameMode.PHYSICS_2D:
                    return self.physics_engine.main_loop()

                case GameMode.VOXELS_3D:
                    return self.voxel_renderer.main_loop()

                case GameMode.LINES_3D:
                    return self.line_renderer.main_loop()

                case GameMode.PLATFORMER_V1:
                    return self.platformer_v1.main_loop()

        self.display.fps_throttle(_main_loop)

    def quit_game(self, message: str = f"BYE BYE!{BR}Thanks for playing :)") -> None:
        self.display.set_message(message)
        self.display.print_curr_screen()
        self.status = GameStatus.QUIT

    def _check_game_status(self) -> None:
        self._check_player_status()

    def _check_player_status(self) -> None:
        for player in [self.player2d, self.player3d]:
            match player.status:
                case PlayerStatus.DEAD:
                    return self.quit_game(message="GAME OVER")

        if self.player2d.status == PlayerStatus.END_LEVEL_2D:
            return self.quit_game(message="YOU WON!!! :D")

    def _handle_welcome_message(self) -> None:
        _WELCOME_MESSAGE_SHOWN = -99

        if (
            not self.status == GameStatus.RUNNING
            or self._welcome_message_timer == _WELCOME_MESSAGE_SHOWN
        ):
            return
        elif self._welcome_message_timer >= 0:
            _text = _WELCOME_TEXT
            # TODO: fix this
            # _WELCOME_TEXT[
            #     0 : (len(_WELCOME_TEXT) - (_WELCOME_TIMER - self._welcome_message_timer))
            # ]
            intensity = 1 - ((_WELCOME_TIMER - self._welcome_message_timer) / _WELCOME_TIMER)
            self.display.set_message(_text, intensity=intensity)
            self._welcome_message_timer -= 1
        elif self.display.has_message():
            self.display.set_message(None)
            self._welcome_message_timer = _WELCOME_MESSAGE_SHOWN

    ##############
    # PLAYER INPUT
    ##############

    def handle_keyboard_input(self) -> None:
        self._press_quit()
        self._switch_3d_rendering_mode()
        self._switch_2d_mode()
        self._switch_3d_mode()
        self._switch_physics2d_mode()
        self._toggle_rotation()

        if self.mode == GameMode.PLATFORMER_V1:
            return

        self._increase_fov()
        self._decrease_fov()

        self._increase_visibility()
        self._decrease_visibility()

        self._shuffle_colors()

    @on_key_press(MenuKeys.QUIT)
    def _press_quit(self):
        self.quit_game()

    @on_key_press(MenuKeys.SWITCH_PHYSICS_2D_MODE, act_once_per_press=True)
    def _switch_physics2d_mode(self):
        self.mode = GameMode.PHYSICS_2D
        self.display.set_mode()

    @on_key_press(MenuKeys.SWITCH_2D_MODE, act_once_per_press=True)
    def _switch_2d_mode(self):
        self.mode = GameMode.PLATFORMER_V1
        self.display.set_mode()

    @on_key_press(MenuKeys.SWITCH_3D_MODE, act_once_per_press=True)
    def _switch_3d_mode(self):
        self.mode = GameMode.VOXELS_3D
        self.display.set_mode()
        self.voxel_renderer.reset_screen_buffer()

    @on_key_press(DisplayKeys.SWITCH_RENDERING_MODE, act_once_per_press=True)
    def _switch_3d_rendering_mode(self):
        self.mode = GameMode.VOXELS_3D if self.mode == GameMode.LINES_3D else GameMode.LINES_3D
        self.display.set_mode()

        if self.mode == GameMode.VOXELS_3D:
            self.voxel_renderer.reset_screen_buffer()
        else:
            self.line_renderer.reset_screen_buffer()
            self.line_renderer.reset_world_data()

    @on_key_press(DisplayKeys.SWITCH_ANTIALIASING, act_once_per_press=True)
    def _switch_antialiasing(self):
        self.display.antialiasing = not self.display.antialiasing

    @on_key_press(DisplayKeys.INCREASE_VISIBILITY)
    def _increase_visibility(self):
        # TODO: I don't like this, should be a single source of truth. Same for all the rest.
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
    # TODO: this is a hack, do properly
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
        self.player3d.curr_level.toggle_rotation()
