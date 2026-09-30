import math

from model.theme import EMPTY_SPACE, RGB
from physics2d.entities.base import PhysicsEntity
from utils import colored

_GREEN = RGB(0, 255, 0)
_RED = RGB(255, 0, 0)
_DEFAULT_NUM_HEALTH_BARS = 10


def get_health_bar(
    entity: PhysicsEntity,
    num_bars=_DEFAULT_NUM_HEALTH_BARS,
) -> str:
    from physics2d.entities.enemy import Enemy
    from physics2d.entities.player_blob import PlayerBlob

    if (
        (not isinstance(entity, Enemy) and not isinstance(entity, PlayerBlob))
        or entity.health is None
        or not entity._initial_health
    ):
        return ""

    health_ratio = entity.health / entity._initial_health

    num_full_bars = math.floor(num_bars * health_ratio)
    full_bars = colored(EMPTY_SPACE * num_full_bars, bg_color=_GREEN)

    num_empty_bars = math.floor(num_bars * (1 - health_ratio))
    empty_bars = colored(EMPTY_SPACE * num_empty_bars, bg_color=_RED)

    _health_per_bar = entity._initial_health / num_bars

    middle_bar = (
        colored(
            EMPTY_SPACE,
            bg_color=_GREEN.get_gradient(
                _RED,
                _health_per_bar - (entity.health % _health_per_bar),
                _health_per_bar,
            ),
        )
        if num_bars - num_full_bars - num_empty_bars != 0
        else ""
    )

    return "[" + full_bars + middle_bar + empty_bars + "]"


def get_health_bar_as_list(
    entity: PhysicsEntity,
    num_bars=_DEFAULT_NUM_HEALTH_BARS,
) -> list[str]:
    from physics2d.entities.enemy import Enemy
    from physics2d.entities.player_blob import PlayerBlob

    if (
        (not isinstance(entity, Enemy) and not isinstance(entity, PlayerBlob))
        or entity.health is None
        or not entity._initial_health
    ):
        return []

    health_per_bar = entity._initial_health / num_bars
    health_ratio = entity.health / entity._initial_health
    health_bar_list = ["["]

    num_full_bars = math.floor(num_bars * health_ratio)
    num_empty_bars = math.floor(num_bars * (1 - health_ratio))

    for _ in range(num_full_bars):
        health_bar_list.append(colored(EMPTY_SPACE, bg_color=_GREEN))

    middle_bar = (
        colored(
            EMPTY_SPACE,
            bg_color=_GREEN.get_gradient(
                _RED,
                health_per_bar - (entity.health % health_per_bar),
                health_per_bar,
            ),
        )
        if num_bars - num_full_bars - num_empty_bars != 0
        else ""
    )

    health_bar_list.append(middle_bar)

    for _ in range(num_empty_bars):
        health_bar_list.append(colored(EMPTY_SPACE, bg_color=_RED))

    health_bar_list.append("]")

    return health_bar_list
