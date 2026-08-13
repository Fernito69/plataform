import time

from constants import FPS_2D
from display import Display
from entities.base import Entity2D
from entities.player2d import Player2D
from level2d import Level2D
from model.game import GameStatus
from model.player import PlayerStatus
from three_d_renderer.constants import FPS_3D
from three_d_renderer.entities.player3d import Player3D
from three_d_renderer.three_d_renderer import ThreeDeeRenderer


class Game:
    status: GameStatus = GameStatus.PLAYING
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

        self.three_d_renderer = ThreeDeeRenderer(player=player_3d)

    def _check_player_status(self) -> None:
        if self.player2d.status != PlayerStatus.ALIVE:
            match self.player2d.status:
                case PlayerStatus.MODE_3D:
                    self._curr_fps = FPS_3D
                    self.status = GameStatus.THREE_D_RENDERER
                    return
                case PlayerStatus.MODE_2D:
                    self._curr_fps = FPS_2D
                    self.status = GameStatus.PLAYING
                    return
                case PlayerStatus.DEAD:
                    message = "GAME OVER"
                case PlayerStatus.QUIT:
                    message = "BYE BYE"
                case PlayerStatus.EXIT:
                    message = "YOU WON!"

            self.display.print_message(message)
            self.status = GameStatus.GAMEOVER

    def _compute_actions_and_add_to_screen(self, entity: Entity2D) -> None:
        entity.do_your_thing()
        self.display.add_to_matrix(entity)

    def _frame_delay(self) -> None:
        time.sleep(1 / self._curr_fps)

    def _print_game(self) -> None:
        self.display.print_curr_screen(self.player2d)

    def game_loop(self) -> None:
        self._frame_delay()

        self.player2d.handle_player_input()

        # TODO: this should not happen here, do properly
        if self.status == GameStatus.THREE_D_RENDERER:
            self._check_player_status()
            return self.three_d_renderer.print_scenario()

        self.display.populate_level_into_matrix()

        self._compute_actions_and_add_to_screen(self.player2d)

        for enemy in self.levels[self.current_level_index].enemies:
            self._compute_actions_and_add_to_screen(enemy)

        for exit in self.levels[self.current_level_index].exits:
            self._compute_actions_and_add_to_screen(exit)

        self._print_game()

        self._check_player_status()
