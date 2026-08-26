import random

from factories.theme import DefaultTheme, DoubleLines
from model.base import Orientation, Point2
from model.theme import EMPTY_SPACE, RGB, Theme
from two_dee_renderer.constants import X_RESOLUTION_2D, Y_RESOLUTION_2D
from two_dee_renderer.entities.enemy2d import Enemy2D
from two_dee_renderer.entities.things2d import Exit2D
from utils import colored

_DEFAULT_LINE_TYPE = DoubleLines


class Level2D:
    map: list[list[str]]  # matrix representation of the level data
    enemies: list[Enemy2D]
    exits: list[Exit2D]
    name: str
    player_starting_position: Point2
    theme: Theme

    def __init__(
        self,
        name: str,
        enemies: list[Enemy2D],
        exits: list[Exit2D],
        theme: Theme | None,
        player_starting_position: Point2 = (1, 1),
    ):
        self.enemies = enemies
        self.name = name
        self.map = []
        self.player_starting_position = player_starting_position
        self.exits = exits
        self.theme = theme or DefaultTheme

        # Init enemies
        for enemy in enemies:
            enemy.set_curr_level(self)

        for i in range(Y_RESOLUTION_2D):
            self.map.append([])
            for _ in range(X_RESOLUTION_2D):
                self.map[i].append(EMPTY_SPACE)

        self.init_map_border()

    def init_map_border(self):
        line = self.theme.line_type or _DEFAULT_LINE_TYPE
        self.add_char(line.UL, (0, 0))
        self.add_char(line.LR, (X_RESOLUTION_2D - 1, Y_RESOLUTION_2D - 1))
        self.add_char(line.UR, (X_RESOLUTION_2D - 1, 0))
        self.add_char(line.LL, (0, Y_RESOLUTION_2D - 1))

        # repeat the loops to respect the _curr_custom_char_index order
        # TODO: do it better so it's really a loop, even considering corners
        for i in range(1, Y_RESOLUTION_2D - 1):
            self.add_char(line.V, (0, i))
        for i in range(1, Y_RESOLUTION_2D - 1):
            self.add_char(line.V, (X_RESOLUTION_2D - 1, i))

        for i in range(1, X_RESOLUTION_2D - 1):
            self.add_char(line.H, (i, 0))
        for i in range(1, X_RESOLUTION_2D - 1):
            self.add_char(line.H, (i, Y_RESOLUTION_2D - 1))

    def _color(self, char: str, color: RGB | None = None, bg_color: RGB | None = None):
        return colored(
            char[0],
            color or self.theme.color,
            bg_color or self.theme.bg_color,
        )

    def add_char(
        self,
        char: str,
        position: Point2,
        color: RGB | None = None,
        bg_color: RGB | None = None,
    ):
        char = self._get_custom_theme_char(char[0])
        color = color or self.theme.color
        bg_color = bg_color or self.theme.bg_color
        # TODO: check whether round or math.floor works better here
        self.map[round(position[1])][round(position[0])] = self._color(char, color, bg_color)

    _curr_custom_char_index: int = 0
    _directions = (1, -1)
    _curr_direction_index: int = 0

    def _get_custom_theme_char(self, fallback: str) -> str:
        if self.theme.custom_line_chars:
            index: int
            match self.theme.custom_line_type:
                case "random":
                    index = int(random.random() * len(self.theme.custom_line_chars))
                # TODO: check why this is not returning the last char
                case "sequential":
                    index = self._curr_custom_char_index

                    # bump the index
                    self._curr_custom_char_index = (
                        self._curr_custom_char_index + 1
                        if self._curr_custom_char_index < len(self.theme.custom_line_chars) - 1
                        else 0
                    )
                case "back&forth":
                    index = self._curr_custom_char_index

                    # set the right index
                    direction = self._directions[self._curr_direction_index]

                    self._curr_custom_char_index = self._curr_custom_char_index + direction

                    # flip the direction if need be
                    if (
                        direction == 1
                        and self._curr_custom_char_index >= len(self.theme.custom_line_chars) - 1
                    ):
                        self._curr_direction_index = 1
                    elif direction == -1 and self._curr_custom_char_index <= 0:
                        self._curr_direction_index = 0

            return self.theme.custom_line_chars[index]
        return fallback

    # TODO: implement animated map parts :O with a self.do_your_thing() method
    def add_line(
        self,
        initial_position: Point2,
        length: int = 3,
        orientation: Orientation = Orientation.HORIZONTAL,
        # TODO: refactor Theme here!!!
        color: RGB | None = None,
        bg_color: RGB | None = None,
    ):
        x1, y1 = initial_position

        for i in range(length):
            x = max(
                min(
                    x1 + i if orientation == Orientation.HORIZONTAL else x1,
                    X_RESOLUTION_2D - 1,
                ),
                0,
            )
            y = max(
                min(
                    y1 + i if orientation == Orientation.VERTICAL else y1,
                    Y_RESOLUTION_2D - 1,
                ),
                0,
            )
            line = self.theme.line_type or _DEFAULT_LINE_TYPE
            char = (
                self._get_custom_theme_char(line.H)
                if orientation == Orientation.HORIZONTAL
                else self._get_custom_theme_char(line.V)
            )
            self.map[int(y)][int(x)] = self._color(
                char=char,
                color=color or self.theme.color,
                bg_color=bg_color or self.theme.bg_color,
            )
