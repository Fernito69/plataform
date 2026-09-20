from typing import TYPE_CHECKING

from model.base import PointF, VectorF
from model.theme import RGB
from physics2d.shape.factories.explosion import lightning_impact
from physics2d.shape.factories.utils import is_out_of_sight
from physics2d.shape.line import Line
from physics2d.shape.particle.lightning import Lightning
from utils import random_offset_vector

if TYPE_CHECKING:
    from physics2d.entities.base import PhysicsEntity
    from physics2d.entities.enemy import Enemy
    from physics2d.entities.model.shared import ParticleGenerator
    from physics2d.physics2d import Physics2D


def get_lightning_bolts(
    initial_color: RGB,
    ending_color: RGB,
    damage: float | None = None,
    damage_range: float = 50,
    default_tendril_length: float = 40,
    num_tendrils: int = 1,
    life_time: int = 4,
    num_segments: int = 12,
    render_on_top: bool = True,
) -> "ParticleGenerator":
    def _lightning(engine: "Physics2D", source: "PhysicsEntity") -> None:
        if is_out_of_sight(engine, source):
            return

        return _lightning_bolts(
            engine=engine,
            source=source,
            initial_color=initial_color,
            ending_color=ending_color,
            damage=damage,
            damage_range=damage_range,
            default_tendril_length=default_tendril_length,
            num_tendrils=num_tendrils,
            life_time=life_time,
            num_segments=num_segments,
            render_on_top=render_on_top,
        )

    return _lightning


def _lightning_bolts(
    engine: "Physics2D",
    source: "PhysicsEntity",
    initial_color: RGB,
    ending_color: RGB,
    num_tendrils: int = 1,
    damage: float | None = None,
    damage_range: float = 50,
    default_tendril_length: float = 40,
    life_time: int = 4,
    num_segments: int = 12,
    render_on_top: bool = True,
) -> None:
    pieces: list[Line] = []
    possible_victims: list["Enemy"] = []

    if damage:
        possible_victims = [
            r.enemy
            for r in engine.scenario.get_enemies_in_range(
                damage_range,
                source,
                calc_distance_to_border=True,
            )
        ]

    # Otherwise too messy!
    num_tendrils = min(num_tendrils, len(possible_victims) or 1) if damage else num_tendrils
    for index in range(num_tendrils):
        _size = possible_victims[index].size / 2 if len(possible_victims) > index else 1
        _end_point: PointF = (
            possible_victims[index].center + random_offset_vector(_size, _size)
            if len(possible_victims) > index
            else source.center
            + random_offset_vector(default_tendril_length, default_tendril_length)
        )
        l1 = Lightning(
            source=source,
            end_point=_end_point,
            initial_color=initial_color,
            ending_color=ending_color,
            normal_noise=2,
            parallel_noise=3,
            engine=engine,
            life_time=life_time,
            num_segments=num_segments,
            thickness=1,
            final_thickness=0.001,
            render_behind_player=True,
            target=possible_victims[index] if len(possible_victims) > index else None,
        )
        pieces.append(l1)

        if len(possible_victims) > index:
            # TODO: is it right that the particle gen takes care of this?
            possible_victims[index].receive_damage(damage or 0)
            lightning_impact(
                engine,
                possible_victims[index],
                possible_victims[index].center + VectorF.random_offset_vector(_size),
            )

    if render_on_top:
        engine.scenario.fg_shapes.extend(pieces)
    else:
        engine.scenario.bg_shapes.extend(pieces)
