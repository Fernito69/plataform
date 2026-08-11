from constants import CR, LR, UR, H, V
from entities.things import Exit
from factories.enemy import DumbBouncingEnemy, DumbFireFloatingEnemy, DumbFloatingEnemy
from level import Level


def build_level1() -> Level:
    enemies = [
        DumbFloatingEnemy(movement_type=(1, 0), position=(10, 5), speed=2),
        DumbFireFloatingEnemy(movement_type=(1, 0), position=(15, 3), speed=4),
        DumbFloatingEnemy(movement_type=(0, 1), position=(2, 9), speed=6),
        DumbFireFloatingEnemy(movement_type=(0, 1), position=(2, 2), speed=4),
        DumbFloatingEnemy(movement_type=(0, 1), position=(32, 7)),
        DumbFloatingEnemy(movement_type=(1, 0), position=(6, 11), speed=4),
        DumbFloatingEnemy(movement_type=(1, -1), position=(50, 11), speed=10),
        # Jumpy enemies
        DumbBouncingEnemy(
            movement_type=(1, 0), position=(11, 23), color="cyan", speed=8
        ),
        DumbBouncingEnemy(movement_type=(1, 0), position=(12, 23), speed=-5),
        DumbBouncingEnemy(
            movement_type=(1.2, 0), position=(12, 23), color="magenta", speed=1
        ),
        DumbBouncingEnemy(
            movement_type=(2, 0),
            position=(65, 23),
            color="yellow",
            speed=0,
        ),
    ]

    exits = [
        Exit((41, 4)),
    ]

    level = Level(name="Level 1", enemies=enemies, exits=exits)

    # level 1 terrain
    # TODO: refactor "add_horizontal_line", etc into a level method
    level.map[5][4] = UR
    level.map[5][3] = H
    level.map[5][2] = H
    level.map[5][1] = H

    level.map[21][8] = H
    level.map[21][7] = H
    level.map[21][6] = H

    level.map[19][9] = H
    level.map[19][10] = H
    level.map[19][11] = H

    level.map[17][5] = H
    level.map[17][6] = H
    level.map[17][7] = H

    level.map[15][10] = H
    level.map[15][11] = H
    level.map[15][12] = H

    level.map[13][16] = H
    level.map[13][17] = H
    level.map[13][18] = H

    level.map[14][22] = H
    level.map[14][23] = H
    level.map[14][24] = H

    level.map[11][29] = H
    level.map[11][30] = H
    level.map[11][31] = H

    level.map[9][31] = H
    level.map[9][32] = H
    level.map[9][33] = H

    level.map[8][36] = H
    level.map[8][37] = H
    level.map[8][38] = H

    level.map[5][39] = H
    level.map[5][40] = H
    level.map[5][41] = H

    level.map[4][31] = H
    level.map[4][32] = H
    level.map[4][33] = H

    level.map[5][0] = CR

    for i in range(6, 23):
        level.map[i][4] = V

    level.map[22][4] = LR
    level.map[22][3] = H
    level.map[22][2] = H
    level.map[22][1] = H
    level.map[22][0] = CR
    level.map[17][4] = CR

    return level
