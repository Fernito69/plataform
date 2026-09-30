import math

from model.theme import EMPTY_SPACE, RGB
from utils import colored

_GREEN = RGB(0, 255, 0)
_RED = RGB(255, 0, 0)
_DEFAULT_NUM_HEALTH_BARS = 10

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from physics2d.entities.enemy import Enemy
    from physics2d.entities.player_blob import PlayerBlob

_LEFT_BRACKET = colored(
    "[",
    color=RGB(255, 255, 255),
    bg_color=RGB(0, 0, 0),
)

_RIGHT_BRACKET = colored(
    "]",
    color=RGB(255, 255, 255),
    bg_color=RGB(0, 0, 0),
)


def get_health_bar(
    entity: "Enemy | PlayerBlob",
    num_bars=_DEFAULT_NUM_HEALTH_BARS,
    with_special_chars: bool = False,
    special_charset_index: int = 0,
) -> str:
    if entity.health is None or not entity._initial_health:
        return ""

    health_ratio = entity.health / entity._initial_health

    num_full_bars = math.floor(num_bars * health_ratio)
    full_bars = colored(EMPTY_SPACE * num_full_bars, bg_color=_GREEN)

    num_empty_bars = math.floor(num_bars * (1 - health_ratio))
    empty_bars = colored(EMPTY_SPACE * num_empty_bars, bg_color=_RED)

    middle_bar = _get_middle_bar(
        entity=entity,
        num_bars=num_bars,
        num_full_bars=num_full_bars,
        num_empty_bars=num_empty_bars,
        special_charset_index=special_charset_index,
        with_special_chars=with_special_chars,
    )

    return _LEFT_BRACKET + full_bars + middle_bar + empty_bars + _RIGHT_BRACKET


def get_health_bar_as_list(
    entity: "Enemy | PlayerBlob",
    num_bars=_DEFAULT_NUM_HEALTH_BARS,
    with_special_chars: bool = True,
    special_charset_index: int = 0,
) -> list[str]:
    if entity.health is None or not entity._initial_health:
        return []

    health_ratio = entity.health / entity._initial_health
    health_bar_list = [_LEFT_BRACKET]

    num_full_bars = math.floor(num_bars * health_ratio)
    num_empty_bars = math.floor(num_bars * (1 - health_ratio))

    for _ in range(num_full_bars):
        health_bar_list.append(colored(EMPTY_SPACE, bg_color=_GREEN))

    middle_bar = _get_middle_bar(
        entity=entity,
        num_bars=num_bars,
        num_full_bars=num_full_bars,
        num_empty_bars=num_empty_bars,
        special_charset_index=special_charset_index,
        with_special_chars=with_special_chars,
    )

    if middle_bar:
        health_bar_list.append(middle_bar)

    for _ in range(num_empty_bars):
        health_bar_list.append(colored(EMPTY_SPACE, bg_color=_RED))

    health_bar_list.append(_RIGHT_BRACKET)

    return health_bar_list


_HEALTH_BAR_STEPS: list[str] = [
    "▉▊▋▌▍▎▏",
    "▇▆▅▄▃▂▁",
    "▙▚▖",
]


def _get_middle_bar(
    entity: "Enemy | PlayerBlob",
    num_bars: int,
    num_full_bars: int,
    num_empty_bars: int,
    special_charset_index: int,
    with_special_chars: bool,
) -> str:
    if entity.health is None or not entity._initial_health:
        return ""

    _health_per_bar = entity._initial_health / num_bars
    _middle_bar_portion = _health_per_bar - (entity.health % _health_per_bar)
    _health_bar_steps = _HEALTH_BAR_STEPS[special_charset_index]

    step_index = math.floor(_middle_bar_portion / (_health_per_bar / len(_health_bar_steps)))

    _char = (
        _health_bar_steps[step_index]
        if with_special_chars and step_index < len(_health_bar_steps)
        else EMPTY_SPACE
    )

    middle_bar = (
        (
            colored(
                _char,
                color=_GREEN,
                bg_color=_RED,
            )
            if with_special_chars
            else colored(
                _char,
                bg_color=_GREEN.get_gradient(
                    _RED,
                    _middle_bar_portion,
                    _health_per_bar,
                ),
            )
        )
        if num_bars - num_full_bars - num_empty_bars != 0
        else ""
    )
    return middle_bar
