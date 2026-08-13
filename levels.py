from entities.things import Exit
from factories.enemy import DumbBouncingEnemy, DumbFireFloatingEnemy, DumbFloatingEnemy
from factories.theme import JungleTheme
from level import Level
from model.shared import Direction


def build_level1() -> Level:
    enemies = [
        DumbFloatingEnemy(movement_type=(1, 0), position=(10, 5), speed=2),
        DumbFloatingEnemy(movement_type=(0, 1), position=(2, 9), speed=6),
        DumbFloatingEnemy(movement_type=(0, 1), position=(32, 7)),
        DumbFloatingEnemy(movement_type=(1, 0), position=(6, 11), speed=4),
        DumbFloatingEnemy(movement_type=(1, -1), position=(50, 11), speed=10),
        DumbFireFloatingEnemy(movement_type=(1, 0), position=(15, 3), speed=4),
        DumbFireFloatingEnemy(movement_type=(0, 1), position=(2, 2), speed=4),
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

    level = Level(
        name="Level 1",
        enemies=enemies,
        exits=exits,
        theme=JungleTheme,
    )

    # level 1 terrain
    l = level.theme.line_type
    level.add_char(l.UR, (4, 5))

    level.add_line(initial_position=(1, 5))
    level.add_line((6, 21))
    level.add_line((9, 19))
    level.add_line((5, 17))
    level.add_line((10, 15))
    level.add_line((16, 13))
    level.add_line((22, 14))
    level.add_line((9, 19))
    level.add_line((29, 11))
    level.add_line((31, 9))
    level.add_line((36, 8))
    level.add_line((39, 5))
    level.add_line((31, 4))
    level.add_line((31, 4))

    level.add_char(l.CR, (0, 5))

    level.add_line((4, 6), 17, Direction.VERTICAL)
    level.add_line((1, 22))

    level.add_char(l.CR, (0, 22))
    level.add_char(l.CR, (4, 17))
    level.add_char(l.LR, (4, 22))

    return level
