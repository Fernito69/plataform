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
