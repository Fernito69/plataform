from random import random
from typing import TYPE_CHECKING

from model.base import PointF, VectorF
from model.theme import RGB
from physics2d.entities.equipment.projectile import Projectile
from physics2d.shape.factories.explosion import (
    bullet_ricochet,
    get_rocket_explosion,
    lightning_impact,
    rocket_trail,
)
from physics2d.shape.factories.utils import is_out_of_sight
from physics2d.shape.line import Line
from physics2d.shape.model.shared import TransitionType
from physics2d.shape.particle.lightning import Lightning
from utils import random_offset

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
    target_projectiles: bool = True,
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
            target_projectiles=target_projectiles,
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
    target_projectiles: bool = True,
) -> None:
    pieces: list[Line] = []
    possible_victims: list["Enemy | Projectile"] = []

    if damage:
        possible_victims = [
            r.enemy
            for r in engine.scenario.get_enemies_in_range(
                damage_range,
                source,
                calc_distance_to_border=True,
            )
        ]
        if target_projectiles:
            possible_victims += [
                r.projectile
                for r in engine.scenario.get_projectiles_in_range(
                    max_range=damage_range,
                    subject=source,
                    calc_distance_to_border=True,
                )
            ]

    # Otherwise too messy!
    num_tendrils = min(num_tendrils, len(possible_victims) or 1) if damage else num_tendrils
    for index in range(num_tendrils):
        _size = possible_victims[index].size / 2 if len(possible_victims) > index else 1
        _end_point: PointF = (
            possible_victims[index].center + VectorF.random_offset_vector(_size)
            if len(possible_victims) > index
            else source.center + VectorF.random_offset_vector(default_tendril_length)
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

        if damage and len(possible_victims) > index:
            from physics2d.entities.enemy import Enemy

            # TODO: is it right that the particle gen takes care of this?
            victim = possible_victims[index]
            if isinstance(victim, Enemy):
                victim.receive_damage(damage)
            else:
                victim.hit()

            lightning_impact(
                engine,
                possible_victims[index],
                possible_victims[index].center + VectorF.random_offset_vector(_size),
            )

    if render_on_top:
        engine.scenario.fg_shapes.extend(pieces)
    else:
        engine.scenario.bg_shapes.extend(pieces)


def get_bullet(
    damage: float = 10,
    speed: float = 10,
    size: float = 0.7,
    is_enemy: bool = False,
    initial_color: RGB = RGB(127 + random_offset() * 80, 255 - random() * 60, 255, 1),
    ending_color: RGB = RGB(30, 30, 30, 1),
    life_time: int = 50,
) -> "ParticleGenerator":
    def _bullet(engine: "Physics2D", source: "PhysicsEntity"):
        velocity = ((speed + random_offset()) * source.get_aiming_direction()).as_vector()

        bullet = Projectile(
            owner=source,
            offset_from_origin=VectorF.random_offset_vector(),
            initial_velocity=velocity,
            size=size,
            size_change_type=TransitionType.NONE,
            initial_color=initial_color,
            ending_color=ending_color,
            life_time=life_time,
            damage=damage,
            explosion_generator=bullet_ricochet,
            engine=engine,
            is_enemy=is_enemy,
        )
        if is_enemy:
            engine.scenario.enemy_projectiles.append(bullet)
        else:
            engine.scenario.projectiles.append(bullet)

    return _bullet


def rocket(
    engine: "Physics2D",
    source: "PhysicsEntity",
    rocket_speed: float,
    life_time: int,
    damage: float,
    blast_radius: float,
    max_blast_damage: float,
    size: float,
    color: RGB = RGB(127, 127, 127, 1),
    is_enemy: bool = False,
):
    return Projectile(
        owner=source,
        engine=engine,
        offset_from_origin=VectorF.random_offset_vector(),
        initial_velocity=(
            (rocket_speed + random_offset()) * source.get_aiming_direction()
        ).as_vector(),
        size=size,
        size_change_type=TransitionType.NONE,
        ending_color_fade_type=TransitionType.NONE,
        initial_color=color,
        life_time=life_time,
        damage=damage,
        explosion_generator=get_rocket_explosion(damage, blast_radius, max_blast_damage),
        trail_generator=rocket_trail,
        density=3,
        explode_on_life_time_over=True,
        is_enemy=is_enemy,
    )


def get_rocket(
    rocket_speed: float,
    life_time: int,
    damage: float,
    blast_radius: float,
    max_blast_damage: float,
    size: float,
    color: RGB = RGB(127, 127, 127, 1),
    is_enemy: bool = False,
) -> "ParticleGenerator":
    def _get_rocket(engine: "Physics2D", source: "PhysicsEntity") -> None:
        _rocket = rocket(
            engine=engine,
            source=source,
            damage=damage,
            rocket_speed=rocket_speed,
            life_time=life_time,
            blast_radius=blast_radius,
            max_blast_damage=max_blast_damage,
            size=size,
            color=color,
            is_enemy=is_enemy,
        )
        if is_enemy:
            engine.scenario.enemy_projectiles.append(_rocket)
        else:
            engine.scenario.projectiles.append(_rocket)

    return _get_rocket
