import random

from constants import EMPTY_SPACE, X_RESOLUTION, Y_RESOLUTION
from entities.enemy import Enemy
from entities.things import Exit
from factories.theme import DefaultTheme
from model.shared import Coord, Orientation
from model.theme import RGB, Theme
from utils import colored


class Level:
    map: list[list[str]]  # matrix representation of the level data
    enemies: list[Enemy]
    exits: list[Exit]
    name: str
    player_starting_position: Coord
    theme: Theme

    def __init__(
        self,
        name: str,
        enemies: list[Enemy],
        exits: list[Exit],
        theme: Theme | None,
        player_starting_position: Coord = (1, 1),
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

        for i in range(Y_RESOLUTION):
            self.map.append([])
            for _ in range(X_RESOLUTION):
                self.map[i].append(EMPTY_SPACE)

        self.init_map_border()

    def init_map_border(self):
        l = self.theme.line_type
        self.add_char(l.UL, (0, 0))
        self.add_char(l.LR, (X_RESOLUTION - 1, Y_RESOLUTION - 1))
        self.add_char(l.UR, (X_RESOLUTION - 1, 0))
        self.add_char(l.LL, (0, Y_RESOLUTION - 1))

        # repeat the loops to respect the _curr_custom_char_index order
        # TODO: do it better so it's really a loop, even considering corners
        for i in range(1, Y_RESOLUTION - 1):
            self.add_char(l.V, (0, i))
        for i in range(1, Y_RESOLUTION - 1):
            self.add_char(l.V, (X_RESOLUTION - 1, i))

        for i in range(1, X_RESOLUTION - 1):
            self.add_char(l.H, (i, 0))
        for i in range(1, X_RESOLUTION - 1):
            self.add_char(l.H, (i, Y_RESOLUTION - 1))

    def _color(
        self, char: str, color: RGB | None = None, bg_color: RGB | None = None
    ):
        return colored(
            char[0],
            color or self.theme.color,
            bg_color or self.theme.bg_color,
        )

    def add_char(
        self,
        char: str,
        position: Coord,
        color: RGB | None = None,
        bg_color: RGB | None = None,
    ):
        char = self.get_custom_theme_char(char[0])
        color = color or self.theme.color
        bg_color = bg_color or self.theme.bg_color
        # TODO: check whether round or math.floor works better here
        self.map[round(position[1])][round(position[0])] = self._color(
            char, color, bg_color
        )

    _curr_custom_char_index: int = 0
    _directions = (1, -1)
    _curr_direction_index: int = 0

    def get_custom_theme_char(self, fallback: str) -> str:
        if self.theme.custom_line_chars:
            index: int
            match self.theme.custom_line_type:
                case "random":
                    index = int(random.random() * len(self.theme.custom_line_chars))
                case "sequential":
                    index = self._curr_custom_char_index

                    # bump the index
                    self._curr_custom_char_index = (
                        self._curr_custom_char_index + 1
                        if self._curr_custom_char_index
                        < len(self.theme.custom_line_chars) - 1
                        else 0
                    )
                case "back&forth":
                    index = self._curr_custom_char_index

                    # set the right index
                    direction = self._directions[self._curr_direction_index]

                    self._curr_custom_char_index = (
                        self._curr_custom_char_index + direction
                    )

                    # flip the direction if need be
                    if (
                        direction == 1
                        and self._curr_custom_char_index
                        >= len(self.theme.custom_line_chars) - 1
                    ):
                        self._curr_direction_index = 1
                    elif direction == -1 and self._curr_custom_char_index <= 0:
                        self._curr_direction_index = 0

            # bump the index

            return self.theme.custom_line_chars[index]
        return fallback

    # TODO: implement animated map parts :O with a self.do_your_thing() method
    def add_line(
        self,
        initial_position: Coord,
        length: int = 3,
        direction: Orientation = Orientation.HORIZONTAL,
        color: RGB | None = None,
        bg_color: RGB | None = None,
    ):
        x1, y1 = initial_position

        for i in range(length):
            x = max(
                min(
                    x1 + i if direction == Orientation.HORIZONTAL else x1,
                    X_RESOLUTION - 1,
                ),
                0,
            )
            y = max(
                min(
                    y1 + i if direction == Orientation.VERTICAL else y1, Y_RESOLUTION - 1
                ),
                0,
            )
            char = (
                self.get_custom_theme_char(self.theme.line_type.H)
                if direction == Orientation.HORIZONTAL
                else self.get_custom_theme_char(self.theme.line_type.V)
            )
            self.map[int(y)][int(x)] = self._color(
                char=char,
                color=color or self.theme.color,
                bg_color=bg_color or self.theme.bg_color,
            )
