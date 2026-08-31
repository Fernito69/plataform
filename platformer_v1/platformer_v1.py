import math
from typing import TYPE_CHECKING

from display import Display
from model.shared import Engine
from model.theme import EMPTY_SPACE
from platformer_v1.entities.base import Entity2D
from platformer_v1.entities.player2d import Player2D
from platformer_v1.level_2d import Level2D
from platformer_v1.levels_2d import build_2d_levels

if TYPE_CHECKING:
    from game import Game


class PlatformerV1(Engine):
    levels_2d: list[Level2D]
    _current_level_index: int
    display: Display
    player2d: Player2D

    def __init__(
        self,
        game: "Game",
        current_level_index: int = 0,
    ):
        self.game = game
        self._current_level_index = current_level_index

        self.display = self.game.display

        self.player2d = self.game.player2d
        self.levels_2d = build_2d_levels()
        self.player2d.set_curr_level(self.levels_2d[self._current_level_index])

    def main_loop(self) -> None:
        self.player2d.handle_player_input()
        self.populate_level_into_matrix()

        self._compute_actions_and_add_to_screen(self.player2d)

        for enemy in self.levels_2d[self._current_level_index].enemies:
            self._compute_actions_and_add_to_screen(enemy)

        for exit in self.levels_2d[self._current_level_index].exits:
            self._compute_actions_and_add_to_screen(exit)

        self._print_game()

    def _compute_actions_and_add_to_screen(self, entity: Entity2D) -> None:
        entity.do_your_thing()

        y = math.floor(entity.position[1])
        x = math.floor(entity.position[0])

        self.display.put_char_in_pixel(entity.get_char(), (x, y))

    def _print_game(self) -> None:
        self.display.print_curr_screen(self.player2d)

    # TODO: this shouldn't be here?
    def populate_level_into_matrix(self):
        d = self.display
        d.put_screen_content([])
        for y in range(d.curr_y_resolution):
            d._screen_matrix.append([])
            for x in range(d.curr_x_resolution):
                d._screen_matrix[y].append(
                    self.levels_2d[self._current_level_index].map[y][x] or EMPTY_SPACE
                )
