from factories.theme import (
    BloodTheme,
    Blue,
    Cyan,
    DoubleLines,
    JungleTheme,
    Magenta,
    Red,
    WaterTheme,
    Yellow,
)
from model.base import Orientation, PointF, VectorF
from platformer_v1.entities.things2d import Exit2D
from platformer_v1.factories import DumbBouncingEnemy, DumbFireFloatingEnemy, DumbFloatingEnemy
from platformer_v1.level_2d import Level2D

_DEFAULT_LINE_TYPE = DoubleLines


def build_level1() -> Level2D:
    enemies = [
        DumbFloatingEnemy(movement_type=VectorF(1, 0), position=PointF(10, 5), speed=2),
        DumbFloatingEnemy(movement_type=VectorF(0, 1), position=PointF(9, 7), speed=6),
        DumbFloatingEnemy(movement_type=VectorF(0, 1), position=PointF(32, 7)),
        DumbFloatingEnemy(movement_type=VectorF(1, 0), position=PointF(6, 11), speed=4),
        DumbFloatingEnemy(movement_type=VectorF(1, -1), position=PointF(50, 11), speed=10),
        DumbFireFloatingEnemy(movement_type=VectorF(1, 0), position=PointF(15, 3), speed=4),
        DumbFireFloatingEnemy(movement_type=VectorF(0, 1), position=PointF(2, 2), speed=4),
        DumbFireFloatingEnemy(
            movement_type=VectorF(1, 0),
            position=PointF(20, 1),
            speed=10,
            bg_color=Blue(),
            color=Red(),
        ),
        # Jumpy enemies
        DumbBouncingEnemy(
            movement_type=VectorF(1, 0), position=PointF(11, 22), color=Cyan(), speed=8
        ),
        DumbBouncingEnemy(movement_type=VectorF(1, 0), position=PointF(12, 22), speed=-5),
        DumbBouncingEnemy(
            movement_type=VectorF(1.2, 0), position=PointF(12, 22), color=Magenta(), speed=1
        ),
        DumbBouncingEnemy(
            movement_type=VectorF(2, 0),
            position=PointF(65, 22),
            color=Yellow(),
            speed=0,
        ),
    ]

    exits = [
        Exit2D(PointF(41, 4)),
    ]

    level = Level2D(
        name="Level 1",
        enemies=enemies,
        exits=exits,
        theme=BloodTheme,
    )

    # level 1 terrain
    l = level.theme.line_type or _DEFAULT_LINE_TYPE
    level.add_char(l.UR, PointF(4, 5))

    level.add_line(initial_position=PointF(1, 5))
    level.add_line(PointF(6, 21), theme=JungleTheme)
    level.add_line(PointF(9, 19), theme=JungleTheme)
    level.add_line(PointF(5, 17))
    level.add_line(PointF(10, 15), theme=JungleTheme)
    level.add_line(PointF(16, 13))
    level.add_line(PointF(22, 14))
    level.add_line(PointF(9, 19), theme=JungleTheme)
    level.add_line(PointF(29, 11))
    level.add_line(PointF(31, 9))
    level.add_line(PointF(36, 8), theme=JungleTheme)
    level.add_line(PointF(39, 5))
    level.add_line(PointF(31, 4))
    level.add_line(PointF(31, 4))

    level.add_char(l.CR, PointF(0, 5))

    level.add_line(PointF(4, 6), 17, Orientation.VERTICAL)
    level.add_line(PointF(3, 6), 17, orientation=Orientation.VERTICAL)
    level.add_line(PointF(2, 6), 17, orientation=Orientation.VERTICAL)
    level.add_line(PointF(1, 6), 17, orientation=Orientation.VERTICAL)

    level.add_char(l.CR, PointF(0, 22))
    level.add_char(l.CR, PointF(4, 17))
    level.add_char(l.LR, PointF(4, 22))

    level.add_line(PointF(1, 23), 78, theme=WaterTheme)

    return level


def build_2d_levels() -> list[Level2D]:
    return [
        build_level1(),
    ]
