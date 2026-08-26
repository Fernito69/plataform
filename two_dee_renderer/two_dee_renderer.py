from typing import TYPE_CHECKING

from display import Display
from model.theme import EMPTY_SPACE
from two_dee_renderer.entities.base import Entity2D
from two_dee_renderer.entities.player2d import Player2D
from two_dee_renderer.level_2d import Level2D

if TYPE_CHECKING:
    from game import Game


class TwoDeeRenderer:
    levels_2d: list[Level2D]
    _current_level_index: int
    display: Display
    player2d: Player2D

    def __init__(
        self,
        game: "Game",
        current_level_index: int,
    ):
        self.game = game
        self._current_level_index = current_level_index

        self.levels = self.game.levels2d
        self.display = self.game.display

        self.player2d = self.game.player2d
        self.player2d.set_curr_level(self.levels[self._current_level_index])

    # Legacy
    def game_loop(self) -> None:
        self.player2d.handle_player_input()
        self.populate_level_into_matrix()

        self._compute_actions_and_add_to_screen(self.player2d)

        for enemy in self.levels[self._current_level_index].enemies:
            self._compute_actions_and_add_to_screen(enemy)

        for exit in self.levels[self._current_level_index].exits:
            self._compute_actions_and_add_to_screen(exit)

        self._print_game()

    def _compute_actions_and_add_to_screen(self, entity: Entity2D) -> None:
        entity.do_your_thing()
        self.display._add_2d_entity_to_matrix(entity)

    def _print_game(self) -> None:
        self.display.print_curr_screen(self.player2d)

    # TODO: this shouldn't be here?
    def populate_level_into_matrix(self):
        d = self.display
        d.set_2d_resolution()
        d.put_screen_content([])
        # raise KeyError(d.curr_level_2D.map[0][0])
        for y in range(d.curr_y_resolution):
            d._screen_matrix.append([])
            for x in range(d.curr_x_resolution):
                d._screen_matrix[y].append(d.curr_level_2D.map[y][x] or EMPTY_SPACE)
