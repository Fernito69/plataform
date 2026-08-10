"""The Level class: map data, borders and in-map messages."""

from constants import (
    EMPTY_SPACE,
    LL,
    LR,
    UL,
    UR,
    X_RESOLUTION,
    Y_RESOLUTION,
    H,
    V,
)
from entities.enemy import Enemy
from entities.things import Exit
from utils import colored


class Level:
    map: list[list[str]]  # matrix representation of the level data
    enemies: list[Enemy]
    exits: list[Exit]
    name: str
    player_starting_position: tuple[int, int]

    def __init__(
        self,
        name: str,
        enemies: list[Enemy],
        exits: list[Exit],
        player_starting_position: tuple[int, int] = (1, 1),
    ):
        self.enemies = enemies
        self.name = name
        self.map = []
        self.player_starting_position = player_starting_position
        self.exits = exits

        # Init enemies
        for enemy in enemies:
            enemy.set_curr_level(self)

        for i in range(Y_RESOLUTION):
            self.map.append([])
            for _ in range(X_RESOLUTION):
                self.map[i].append(EMPTY_SPACE)

        self.init_map_border()

    def init_map_border(self):
        self.map[0][0] = UL
        self.map[Y_RESOLUTION - 1][X_RESOLUTION - 1] = LR
        self.map[0][X_RESOLUTION - 1] = UR
        self.map[Y_RESOLUTION - 1][0] = LL

        for i in range(1, Y_RESOLUTION - 1):
            self.map[i][0] = V
            self.map[i][X_RESOLUTION - 1] = V

        for i in range(1, X_RESOLUTION - 1):
            self.map[0][i] = H
            self.map[Y_RESOLUTION - 1][i] = H

    # TODO: this doesn't belong here
    def print_message(self, message: str, padding_x: int = 2, padding_y: int = 1):
        if len(message) <= 0:
            return

        mid_x: int = int(X_RESOLUTION / 2)
        mid_y: int = int(Y_RESOLUTION / 2)

        # Message position
        starting_message_x: int = int(mid_x - len(message) / 2)
        ending_message_x: int = int(mid_x + len(message) / 2)

        # Set up border
        starting_border_x: int = starting_message_x - padding_x
        ending_border_x: int = ending_message_x + padding_x
        starting_border_y: int = mid_y - padding_y
        ending_border_y: int = mid_y + padding_y + 1

        # Print border
        for x in range(starting_border_x, ending_border_x):
            for y in range(starting_border_y, ending_border_y):
                char = EMPTY_SPACE

                if y == starting_border_y:
                    if x == starting_border_x:
                        char = colored(UL)
                    elif x == ending_border_x - 1:
                        char = colored(UR)
                    else:
                        char = colored(H)
                elif y == ending_border_y - 1:
                    if x == starting_border_x:
                        char = colored(LL)
                    elif x == ending_border_x - 1:
                        char = colored(LR)
                    else:
                        char = colored(H)
                elif x == starting_border_x or x == ending_border_x - 1:
                    char = colored(V)

                self.map[y][x] = char

        # Print message
        for x, index in enumerate(range(starting_message_x, ending_message_x)):
            self.map[mid_y][index] = colored(message[x], "yellow")
