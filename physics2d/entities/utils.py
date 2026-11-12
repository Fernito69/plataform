import math

from model.theme import EMPTY_SPACE, LOWER_SUBPIXEL_CHAR, RGB
from physics2d.model.frame import HealthBarSnapshot
from utils import colored, extract_bg_color_from_string, extract_color_from_string

_GREEN = RGB(0, 255, 0)
_RED = RGB(255, 0, 0)
_DEFAULT_NUM_HEALTH_BARS = 10
_STATUS_BAR_TITLE_COLOR = RGB(255, 255, 255)

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from physics2d.entities.enemy import Enemy
    from physics2d.entities.equipment.thruster import Thruster
    from physics2d.entities.equipment.weapon import Weapon
    from physics2d.entities.player_blob import PlayerBlob

# _LEFT_BRACKET = colored(
#     "[",
#     color=RGB(255, 255, 255),
#     bg_color=RGB(0, 0, 0),
# )

# _RIGHT_BRACKET = colored(
#     "]",
#     color=RGB(255, 255, 255),
#     bg_color=RGB(0, 0, 0),
# )


# TODO: this is hacky, do better
def _get_values(
    entity: "Enemy | PlayerBlob | Thruster | Weapon",
) -> tuple[float | None, float | None]:
    from physics2d.entities.equipment.thruster import Thruster
    from physics2d.entities.equipment.weapon import Weapon

    curr_value: float | None
    initial_value: float | None

    if isinstance(entity, Weapon):
        curr_value = entity._ammo
        initial_value = entity._max_ammo

    elif isinstance(entity, Thruster):
        curr_value = entity.fuel
        initial_value = 1

    else:
        curr_value = entity.health
        initial_value = entity._initial_health

    return curr_value, initial_value


def get_status_bar_str(
    entity: "Enemy | PlayerBlob | Thruster | Weapon",
    num_bars=_DEFAULT_NUM_HEALTH_BARS,
    with_special_chars: bool = True,
    special_charset_index: int = 0,
    color_full: RGB = _GREEN,
    color_empty: RGB = _RED,
) -> str:
    curr_value, initial_value = _get_values(entity)

    if curr_value is None or not initial_value:
        return ""

    health_ratio = curr_value / initial_value

    num_full_bars = math.floor(num_bars * health_ratio)
    full_bars = colored(EMPTY_SPACE * num_full_bars, bg_color=color_full)

    num_empty_bars = math.floor(num_bars * (1 - health_ratio))
    empty_bars = colored(EMPTY_SPACE * num_empty_bars, bg_color=color_empty)

    middle_bar = _get_middle_char(
        entity=entity,
        num_bars=num_bars,
        num_full_bars=num_full_bars,
        num_empty_bars=num_empty_bars,
        special_charset_index=special_charset_index,
        with_special_chars=with_special_chars,
        color_full=color_full,
        color_empty=color_empty,
    )

    return full_bars + middle_bar + empty_bars


def get_status_bar_as_list(
    entity: "Enemy | PlayerBlob | Thruster | Weapon",
    num_bars=_DEFAULT_NUM_HEALTH_BARS,
    with_special_chars: bool = True,
    special_charset_index: int = 0,
    color_full: RGB = _GREEN,
    color_empty: RGB = _RED,
) -> list[str]:
    curr_value, initial_value = _get_values(entity)

    if curr_value is None or not initial_value:
        return []

    health_ratio = curr_value / initial_value
    health_bar_list = []

    num_full_bars = math.floor(num_bars * health_ratio)
    num_empty_bars = math.floor(num_bars * (1 - health_ratio))

    for _ in range(num_full_bars):
        health_bar_list.append(colored(EMPTY_SPACE, bg_color=color_full))

    middle_bar = _get_middle_char(
        entity=entity,
        num_bars=num_bars,
        num_full_bars=num_full_bars,
        num_empty_bars=num_empty_bars,
        special_charset_index=special_charset_index,
        with_special_chars=with_special_chars,
        color_full=color_full,
        color_empty=color_empty,
    )

    if middle_bar:
        health_bar_list.append(middle_bar)

    for _ in range(num_empty_bars):
        health_bar_list.append(colored(EMPTY_SPACE, bg_color=color_empty))

    return health_bar_list


_HEALTH_BAR_STEPS: list[str] = [
    "▉▊▋▌▍▎▏",
    "▇▆▅▄▃▂▁",
    "▙▚▖",
]


def _get_middle_char(
    entity: "Enemy | PlayerBlob | Thruster | Weapon",
    num_bars: int,
    num_full_bars: int,
    num_empty_bars: int,
    special_charset_index: int,
    with_special_chars: bool,
    color_full: RGB,
    color_empty: RGB,
) -> str:
    curr_value, initial_value = _get_values(entity)

    if curr_value is None or not initial_value:
        return ""

    _health_per_bar = initial_value / num_bars
    _middle_bar_portion = _health_per_bar - (curr_value % _health_per_bar)
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
                color=color_full,
                bg_color=color_empty,
            )
            if with_special_chars
            else colored(
                _char,
                bg_color=color_full.get_gradient(
                    color_empty,
                    _middle_bar_portion,
                    _health_per_bar,
                ),
            )
        )
        if num_bars - num_full_bars - num_empty_bars != 0
        else ""
    )
    return middle_bar


def apply_status_bar_to_screen(
    data: list[list[str]],
    health_bar: HealthBarSnapshot,
    status_bar_intensity: float = 0.4,
    title: str = "",
) -> None:
    for x_idx, x in enumerate(
        range(health_bar.x_start, health_bar.x_start + len(health_bar.pixels))
    ):
        _new_pixel = health_bar.pixels[x_idx]

        if not health_bar.with_special_chars:
            _health_bar_color = extract_bg_color_from_string(_new_pixel)
            _color = extract_color_from_string(data[health_bar.y][x])
            _bg_color = extract_bg_color_from_string(data[health_bar.y][x])

            _new_pixel = colored(
                LOWER_SUBPIXEL_CHAR,
                color=(
                    status_bar_intensity * _health_bar_color + (1 - status_bar_intensity) * _color
                ),
                bg_color=(
                    status_bar_intensity * _health_bar_color
                    + (1 - status_bar_intensity) * _bg_color
                ),
            )

        data[health_bar.y][x] = _new_pixel

    if title:
        for x_idx, char in enumerate(title):
            x = health_bar.x_start - (len(title) - x_idx) - 1
            if x < 0:
                continue

            _color = extract_color_from_string(data[health_bar.y][x])
            _bg_color = extract_bg_color_from_string(data[health_bar.y][x])

            data[health_bar.y][x] = colored(
                char,
                color=_STATUS_BAR_TITLE_COLOR,
                bg_color=_color.get_gradient(_bg_color),
            )
