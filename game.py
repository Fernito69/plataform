import time

from constants import FPS_2D, X_RESOLUTION_2D, Y_RESOLUTION_2D
from display import Display
from entities.base import Entity2D
from entities.player2d import Player2D
from level_2d import Level2D
from model.game import GameStatus
from model.keyboard import DisplayKeys, MenuKeys
from model.player import PlayerStatus
from terminal import is_pressed
from three_d_renderer.constants import FPS_3D, X_RESOLUTION_3D, Y_RESOLUTION_3D
from three_d_renderer.entities.player3d import Player3D
from three_d_renderer.three_d_renderer import ThreeDeeRenderer


class Game:
    status: GameStatus = GameStatus.MODE_2D
    player2d: Player2D
    levels: list[Level2D]
    current_level_index: int
    _curr_fps: int = FPS_2D

    three_d_renderer: ThreeDeeRenderer

    display: Display

    def __init__(
        self,
        player_2d: Player2D,
        player_3d: Player3D,
        levels: list[Level2D],
        current_level_index: int = 0,
    ):
        self.levels = levels
        self.current_level_index = current_level_index

        self.player2d = player_2d
        self.player2d.set_curr_level(levels[current_level_index])
        self.display = Display(levels[current_level_index])

        self.three_d_renderer = ThreeDeeRenderer(player=player_3d, display=self.display)

    def _check_game_status(self) -> None:
        match self.status:
            case GameStatus.QUIT:
                message = "BYE BYE"
                self.display.print_message(message)
                self.status = GameStatus.GAMEOVER

        self._check_player_status()

    def _check_player_status(self) -> None:
        for player in [self.player2d, self.three_d_renderer.player]:
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
        self.display._add_to_matrix(entity)

    def _frame_delay(self) -> None:
        time.sleep(1 / self._curr_fps)

    def _print_game(self) -> None:
        self.display.print_curr_screen(self.player2d)

    def game_loop(self) -> None:
        self._frame_delay()

        self.handle_player_input()
        self.player2d.handle_player_input()
        self.three_d_renderer.player.handle_player_input()

        # TODO: this should not happen here, do properly
        if self.status == GameStatus.MODE_3D:
            self._check_game_status()
            return self.three_d_renderer.print_scenario()

        self.display.populate_level_into_matrix()

        self._compute_actions_and_add_to_screen(self.player2d)

        for enemy in self.levels[self.current_level_index].enemies:
            self._compute_actions_and_add_to_screen(enemy)

        for exit in self.levels[self.current_level_index].exits:
            self._compute_actions_and_add_to_screen(exit)

        self._print_game()

        self._check_game_status()

    def handle_player_input(self):
        ########
        # MENU #
        ########
        if is_pressed(MenuKeys.QUIT):
            self.status = GameStatus.QUIT

        # TODO: for menu keys, add a refractory period so the action doesn't get triggered several times
        if is_pressed(MenuKeys.SWITCH_2D_MODE):
            self.status = GameStatus.MODE_2D
            self.display.set_2d_resolution()
            self._curr_fps = FPS_2D

        if is_pressed(MenuKeys.SWITCH_3D_MODE):
            self.status = GameStatus.MODE_3D
            self.display.set_3d_resolution()
            self._curr_fps = FPS_3D

        # For now screen is fixed for 2D mode
        if self.status != GameStatus.MODE_3D:
            return

        if is_pressed(DisplayKeys.INCREASE_X_RESOLUTION):
            self.display.modify_resolution((1, 0))

        if is_pressed(DisplayKeys.DECREASE_X_RESOLUTION):
            self.display.modify_resolution((-1, 0))

        if is_pressed(DisplayKeys.INCREASE_Y_RESOLUTION):
            self.display.modify_resolution((0, 1))

        if is_pressed(DisplayKeys.DECREASE_Y_RESOLUTION):
            self.display.modify_resolution((0, -1))
