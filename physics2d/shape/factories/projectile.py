from typing import TYPE_CHECKING

from model.base import PointF
from model.theme import RGB
from physics2d.shape.factories.explosion import (
    lightning_impact,
)
from physics2d.shape.line import Line
from physics2d.shape.particle.lightning import Lightning
from utils import random_offset_vector

if TYPE_CHECKING:
    from physics2d.entities.base import PhysicsEntity
    from physics2d.entities.enemy import Enemy
    from physics2d.entities.model.shared import ParticleGenerator
    from physics2d.scenario.scenario import Scenario


def get_lightning_bolts(
    initial_color: RGB,
    ending_color: RGB,
    damage: float | None = None,
    damage_range: float = 50,
    default_tendril_length: float = 40,
    num_tendrils: int = 1,
    life_time: int = 4,
    num_segments: int = 12,
) -> "ParticleGenerator":
    def _lightning(scenario: "Scenario", source: "PhysicsEntity") -> None:
        return _lightning_bolts(
            scenario,
            source,
            initial_color,
            ending_color,
            damage,
            damage_range,
            default_tendril_length=default_tendril_length,
            num_tendrils=num_tendrils,
            life_time=life_time,
            num_segments=num_segments,
        )

    return _lightning


def _lightning_bolts(
    scenario: "Scenario",
    source: "PhysicsEntity",
    initial_color: RGB,
    ending_color: RGB,
    damage: float | None = None,
    damage_range: float = 50,
    default_tendril_length: float = 40,
    num_tendrils: int = 1,
    life_time: int = 4,
    num_segments: int = 12,
) -> None:
    pieces: list[Line] = []
    possible_victims: list["Enemy"] = []

    _end_point: PointF = source.center + random_offset_vector(
        default_tendril_length, default_tendril_length
    )

    if damage is not None:
        possible_victims = [r.enemy for r in scenario.get_enemies_in_range(damage_range, source)]

        if len(possible_victims) > 0:
            _size = possible_victims[0].size / 2
            _end_point = possible_victims[0].center + random_offset_vector(_size, _size)
            # TODO: is it right that the particle gen takes care of this?
            possible_victims[0].receive_damage(damage)
            lightning_impact(
                scenario,
                possible_victims[0],
                possible_victims[0].center + random_offset_vector(_size, _size),
            )

    for _ in range(num_tendrils):
        l1 = Lightning(
            source=source,
            end_point=_end_point,
            initial_color=initial_color,
            ending_color=ending_color,
            normal_noise=2,
            parallel_noise=3,
            life_time=life_time,
            num_segments=num_segments,
            thickness=1,
            final_thickness=0.001,
            render_behind_player=True,
            target=possible_victims[0] if len(possible_victims) > 0 else None,
        )
        pieces.append(l1)

    scenario.fg_pieces.extend(pieces)
