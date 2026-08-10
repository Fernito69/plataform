"""Level definitions (level layouts and enemy placements)."""

from constants import CR, H, LR, UR, V
from entities.enemy import Enemy
from entities.things import Exit
from level import Level


def build_level1() -> Level:
    enemies_l1 = [
        Enemy(
            enemy_type=1,
            enemy_speed=2,
            movement_type=(1, 0),
            position=(10, 5),
            character_frames=["·", "-", "+", "x", "┼", "X", "o", "·"],
        ),
        Enemy(1, 4, (1, 0), (15, 3), character_frames=["x"]),
        Enemy(
            1,
            1,
            (0, 1),
            (2, 2),
            character_frames=[
                "█",
                "▓",
                "▓",
                "▒",
                "▓",
                "▒",
                "░",
                "░",
                " ",
                "░",
                "▒",
                "▒",
                "▒",
                "▓",
                "▓",
                "█",
            ],
        ),
        Enemy(1, 1, (0, 1), (32, 7), character_frames=["|", "/", "-", "\\"]),
        Enemy(1, 4, (1, 0), (6, 11), character_frames=["&"]),
        Enemy(1, 10, (-1, 1), (40, 11), character_frames=["|", "/", "-", "\\"]),
        # Jumpy enemies
        Enemy(2, 8, (1, 0), (11, 23), character_frames=["@"], color="cyan"),
        Enemy(2, 1, (1, 0), (12, 23), character_frames=["@"], color="blue"),
        Enemy(2, -5, (1.2, 0), (12, 23), character_frames=["@"], color="magenta"),
        Enemy(2, 0, (2, 0), (65, 23), character_frames=["@"], color="yellow"),
    ]

    exits_l1 = [
        Exit((41, 4)),
    ]

    level1 = Level(name="Level 1", enemies=enemies_l1, exits=exits_l1)

    # level 1 landscape
    # TODO: refactor "add_horizontal_line", etc into a level method
    level1.map[5][4] = UR
    level1.map[5][3] = H
    level1.map[5][2] = H
    level1.map[5][1] = H

    level1.map[21][8] = H
    level1.map[21][7] = H
    level1.map[21][6] = H

    level1.map[19][9] = H
    level1.map[19][10] = H
    level1.map[19][11] = H

    level1.map[17][5] = H
    level1.map[17][6] = H
    level1.map[17][7] = H

    level1.map[15][10] = H
    level1.map[15][11] = H
    level1.map[15][12] = H

    level1.map[13][16] = H
    level1.map[13][17] = H
    level1.map[13][18] = H

    level1.map[14][22] = H
    level1.map[14][23] = H
    level1.map[14][24] = H

    level1.map[11][29] = H
    level1.map[11][30] = H
    level1.map[11][31] = H

    level1.map[9][31] = H
    level1.map[9][32] = H
    level1.map[9][33] = H

    level1.map[8][36] = H
    level1.map[8][37] = H
    level1.map[8][38] = H

    level1.map[5][39] = H
    level1.map[5][40] = H
    level1.map[5][41] = H

    level1.map[4][31] = H
    level1.map[4][32] = H
    level1.map[4][33] = H

    level1.map[5][0] = CR

    for i in range(6, 23):
        level1.map[i][4] = V

    level1.map[22][4] = LR
    level1.map[22][3] = H
    level1.map[22][2] = H
    level1.map[22][1] = H
    level1.map[22][0] = CR
    level1.map[17][4] = CR

    return level1
