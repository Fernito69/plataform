import time

from constants import FPS
from display import Display
from entities.entity import Entity
from entities.player import Player
from level import Level
from model.game import GameStatus
from model.player import PlayerStatus


class Game:
    status: GameStatus = GameStatus.PLAYING
    player: Player
    levels: list[Level]
    current_level_index: int

    display: Display

    def __init__(
        self, player: Player, levels: list[Level], current_level_index: int = 0
    ):
        self.levels = levels
        self.current_level_index = current_level_index

        self.player = player
        self.player.set_curr_level(levels[current_level_index])
        self.display = Display(levels[current_level_index])

    def _check_player_status(self):
        if self.player.status != PlayerStatus.ALIVE:
            match self.player.status:
                case PlayerStatus.DEAD:
                    message = "GAME OVER"
                case PlayerStatus.QUIT:
                    message = "BYE BYE"
                case PlayerStatus.EXIT:
                    message = "YOU WON!"

            self.display.print_message(message)
            self.status = GameStatus.GAMEOVER

    def _compute_actions_and_add_to_screen(self, entity: Entity):
        entity.do_your_thing()
        self.display.add_to_matrix(entity)

    def _frame_delay(self):
        time.sleep(1 / FPS)

    def _print_game(self):
        self.display.print_curr_screen(self.player)

    def game_loop(self):
        self._frame_delay()

        self.player.handle_player_input()
        self.display.populate_level_into_matrix()

        self._compute_actions_and_add_to_screen(self.player)

        for enemy in self.levels[self.current_level_index].enemies:
            self._compute_actions_and_add_to_screen(enemy)

        for exit in self.levels[self.current_level_index].exits:
            self._compute_actions_and_add_to_screen(exit)

        self._print_game()

        self._check_player_status()
