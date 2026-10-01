from display import Display
from model.base import PointF
from model.game import GameMode, GameStatus
from model.keyboard import DisplayKeys, MenuKeys
from model.shared import Engine, KeyboardHandler
from model.theme import BR
from physics2d.entities.player_blob import PlayerBlob
from physics2d.model.frame import FrameSnapshot
from physics2d.physics2d import Physics2D
from pipeline import FramePipeline, SequentialFramePipeline, ThreadedFramePipeline
from platformer_v1.entities.player2d import Player2D
from platformer_v1.platformer_v1 import PlatformerV1
from player import Player, PlayerStatus
from system import on_key_press, stop_mouse_listener
from three_d_renderer.entities.player3d import Player3D
from three_d_renderer.line_renderer import LineRenderer
from three_d_renderer.three_d_renderer import ThreeDeeRenderer
from three_d_renderer.voxel_renderer import VoxelRenderer
from utils import random_offset

_WELCOME_TIMER = 50
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
        threaded: bool = False,
        render_workers: int = 0,
    ):
        self.status = GameStatus.RUNNING
        self.mode = mode

        self._display = Display(self)

        self.player2d = Player2D(1)
        self.platformer_v1 = PlatformerV1(self)

        self.player3d = Player3D(1)
        self.voxel_renderer = VoxelRenderer(self)
        self.line_renderer = LineRenderer(self)

        self.physics_engine = Physics2D(self, render_workers=render_workers)
        self.player_blob = PlayerBlob(self.physics_engine)
        self.physics_engine.init_player()

        # hardcoded cool initial place
        self.player3d.position = PointF(9, -44, -33)

        self._pipeline: FramePipeline = (
            ThreadedFramePipeline(self.calculate_frame, self.render_frame)
            if threaded
            else SequentialFramePipeline(self.calculate_frame, self.render_frame)
        )

    def main_loop(self) -> None:
        self._display.fps_throttle(self._pipeline.run_frame)

    def calculate_frame(self) -> FrameSnapshot | None:
        """Stage 1: everything that reads input or mutates game state.

        Under a threaded pipeline this is the only place game state is touched,
        so it must stay on a single thread.
        """
        self._check_game_status()
        self._handle_welcome_message()

        self.handle_keyboard_input()
        self._display.handle_keyboard_input()

        match self.mode:
            case GameMode.PHYSICS_2D:
                return self.physics_engine.calculate_frame()

            # The other modes aren't split into stages yet, so they still
            # calculate and draw in one go, right here.
            case GameMode.VOXELS_3D:
                self.voxel_renderer.main_loop()

            case GameMode.LINES_3D:
                self.line_renderer.main_loop()

            case GameMode.PLATFORMER_V1:
                self.platformer_v1.main_loop()

        return None

    def render_frame(self, frame: FrameSnapshot | None) -> None:
        """Stage 2: draw a finished frame. Reads nothing but `frame`."""
        # A frame can still be in flight when the mode changes under us, and the
        # display has already been resized by then, so drop it.
        if frame is None or self.mode != GameMode.PHYSICS_2D:
            return

        self.physics_engine.render_frame(frame)

    def shutdown(self) -> None:
        self._pipeline.shutdown()
        self.physics_engine.shutdown()

    def quit_game(self, message: str = f"BYE BYE!{BR}Thanks for playing :)") -> None:
        self._display.set_message(message)
        self._display.print_curr_screen()
        stop_mouse_listener()
        self.status = GameStatus.QUIT

    def _check_game_status(self) -> None:
        self._check_player_status()

    def _check_player_status(self) -> None:
        players: list[Player] = [self.player2d, self.player3d, self.player_blob]
        for player in players:
            match player.status:
                case PlayerStatus.DEAD:
                    return self.quit_game(message="GAME OVER")

        if self.player2d.status == PlayerStatus.END_LEVEL:
            return self.quit_game(message="YOU WON!!! :D")

    def _handle_welcome_message(self) -> None:
        _WELCOME_MESSAGE_SHOWN = -99

        if (
            self._welcome_message_timer == _WELCOME_MESSAGE_SHOWN
            or not self.status == GameStatus.RUNNING
        ):
            return
        elif self._welcome_message_timer >= 0:
            _text = _WELCOME_TEXT
            intensity = 1 - ((_WELCOME_TIMER - self._welcome_message_timer) / _WELCOME_TIMER)
            self._display.set_message(_text, intensity=intensity)
            self._welcome_message_timer -= 1
        elif self._display.has_message():
            self._display.set_message(None)
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
        self._toggle_quality()

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
        self._display.switch_mode_by_game_mode()

    @on_key_press(MenuKeys.SWITCH_2D_MODE, act_once_per_press=True)
    def _switch_2d_mode(self):
        self.mode = GameMode.PLATFORMER_V1
        self._display.switch_mode_by_game_mode()

    @on_key_press(MenuKeys.SWITCH_3D_MODE, act_once_per_press=True)
    def _switch_3d_mode(self):
        self.mode = GameMode.VOXELS_3D
        self._display.switch_mode_by_game_mode()
        self.voxel_renderer.reset_screen_buffer()

    @on_key_press(DisplayKeys.SWITCH_RENDERING_MODE, act_once_per_press=True)
    def _switch_3d_rendering_mode(self):
        self.mode = GameMode.VOXELS_3D if self.mode == GameMode.LINES_3D else GameMode.LINES_3D
        self._display.switch_mode_by_game_mode()

        if self.mode == GameMode.VOXELS_3D:
            self.voxel_renderer.reset_screen_buffer()
        else:
            self.line_renderer.reset_screen_buffer()
            self.line_renderer.reset_world_data()

    # TODO: deprecate this?
    @on_key_press(DisplayKeys.SWITCH_ANTIALIASING, act_once_per_press=True)
    def _switch_antialiasing(self):
        self._display._antialiasing = not self._display._antialiasing

    @on_key_press(DisplayKeys.INCREASE_VISIBILITY)
    def _increase_visibility(self):
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
        renderers: list[ThreeDeeRenderer] = [self.voxel_renderer, self.line_renderer]

        new_colors = sorted(
            renderers[0].colors,
            key=random_offset,
        )

        for r in renderers:
            r.colors = new_colors

    @on_key_press(MenuKeys.TOGGLE_ROTATION, act_once_per_press=True)
    def _toggle_rotation(self) -> None:
        self.player3d.curr_level.toggle_rotation()

    @on_key_press(MenuKeys.TOGGLE_GRAPHICS_QUALITY, act_once_per_press=True)
    def _toggle_quality(self) -> None:
        self.physics_engine.low_quality_mode = not self.physics_engine.low_quality_mode
