import math
from typing import TYPE_CHECKING

from display import Display
from model.base import PointF
from model.shared import Engine
from model.theme import EMPTY_SPACE
from platformer_v1.entities.base import Entity2D
from platformer_v1.entities.player2d import Player2D
from platformer_v1.level_2d import Level2D
from platformer_v1.levels_2d import build_2d_levels

if TYPE_CHECKING:
    from game import Game


class PlatformerV1(Engine):
    _levels_2d: list[Level2D]
    _current_level_index: int
    _display: Display
    _player2d: Player2D

    def __init__(
        self,
        game: "Game",
        current_level_index: int = 0,
    ):
        self.game = game
        self._current_level_index = current_level_index

        self._display = self.game.display

        self._player2d = self.game.player2d
        self._levels_2d = build_2d_levels()
        self._player2d.set_curr_level(self._levels_2d[self._current_level_index])

    def main_loop(self) -> None:
        self._player2d._handle_keyboard_input()
        self.populate_level_into_screen_grid()

        self._compute_actions_and_add_to_screen(self._player2d)

        for enemy in self._levels_2d[self._current_level_index].enemies:
            self._compute_actions_and_add_to_screen(enemy)

        for exit in self._levels_2d[self._current_level_index].exits:
            self._compute_actions_and_add_to_screen(exit)

        self._print_game()

    def _put_char_in_pixel(self, char: str, position: PointF):
        X_RES, Y_RES = self._display.get_resolution()
        x = math.floor(position.x)
        y = math.floor(position.y)
        if 0 <= y < Y_RES and 0 <= x < X_RES:
            self._display.screen_grid[y][x] = char

    def _compute_actions_and_add_to_screen(self, entity: Entity2D) -> None:
        entity.do_your_thing()
        self._put_char_in_pixel(entity.get_char(), entity.position)

    def _print_game(self) -> None:
        self._display.print_curr_screen(self._player2d)

    # TODO: this shouldn't be here?
    def populate_level_into_screen_grid(self):
        _screen_content: list[list[str]] = []

        X_RES, Y_RES = self._display.get_resolution()
        for y in range(Y_RES):
            _screen_content.append([])
            for x in range(X_RES):
                _screen_content[y].append(
                    self._levels_2d[self._current_level_index].map[y][x] or EMPTY_SPACE
                )

        self._display.put_screen_content(_screen_content)
