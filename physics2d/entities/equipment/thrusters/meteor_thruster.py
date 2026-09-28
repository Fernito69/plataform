from random import random
from typing import TYPE_CHECKING

from model.base import PointF, VectorF
from model.theme import RGB, Theme
from physics2d.entities.equipment.thruster import Thruster
from physics2d.shape.factories.explosion import get_smoke_generator
from physics2d.shape.model.shared import TransitionType
from physics2d.shape.particle.circular_particle import CircularParticle
from utils import random_offset

if TYPE_CHECKING:
    from physics2d.entities.base import PhysicsEntity
    from physics2d.physics2d import Physics2D


class MeteorThruster(Thruster):
    """Looks like a meteor!"""

    def __init__(self, engine: "Physics2D"):
        super().__init__(
            engine=engine,
            particle_generator=meteor_trail,
            name="MeteorThruster",
            player_theme=Theme(
                color=RGB(255, 50, 50),
            ),
            max_speed=6,
            accel=1.3,
            decel=0.3,
        )


###############################


def meteor_trail(engine: "Physics2D", source: "PhysicsEntity") -> None:
    pieces: list[CircularParticle] = []

    vel_magnitude = abs(source.velocity)

    for _i in range(1, int(source.radius * 2)):
        i = _i / 2
        distance_factor = (source.radius - i) * 1
        eye_x = source.center.x - source.velocity.x * distance_factor
        eye_y = source.center.y - source.velocity.y * distance_factor

        is_odd = _i % 2 == 1
        _randomness_multi = random() * 2
        _radius_factor = random() * 1.2

        # METEOR KINDA TRAIL
        _meteor_color = RGB(255 - 50 * random(), 255 * random(), 0, opacity=1)

        _THRUST_FIRE_SPAWN_RANDOMNESS_FACTOR = 2

        size = i * _radius_factor * (1 + vel_magnitude / 5)

        thrust_fire = CircularParticle(
            origin=PointF(
                x=eye_x
                + random_offset() * _THRUST_FIRE_SPAWN_RANDOMNESS_FACTOR * _randomness_multi
                + random_offset() * 0.5,
                y=eye_y
                + random_offset() * _THRUST_FIRE_SPAWN_RANDOMNESS_FACTOR * _randomness_multi
                + random_offset() * 0.5,
            ),
            initial_velocity=VectorF(
                x=source.velocity.x * _THRUST_FIRE_SPAWN_RANDOMNESS_FACTOR * _randomness_multi * 0.1
                + random_offset() * 0.5,
                y=source.velocity.y * _THRUST_FIRE_SPAWN_RANDOMNESS_FACTOR * _randomness_multi * 0.1
                + random_offset() * 0.5,
            ),
            size=size,
            size_change_type=TransitionType.LINEAR_DECREASE,
            initial_color=_meteor_color,
            ending_color=RGB(80, 80, 80, opacity=0.2),  # smokelike
            life_time=15,
            gravity=-0.07,
            engine=engine,
            particle_generator=get_smoke_generator(
                random_offset_factor=size * 2,
                floating_multi=0.2,
                gravity=-0.04,
                life_time=6,
                initial_velocity=VectorF(random_offset() * 0.15, 0),
                size_factor=0.2,
                only_fg=True,
            ),
        )
        pieces.append(thrust_fire)

    for _ in range(round((vel_magnitude / 6) + 1)):
        if vel_magnitude == 0 and engine.scenario.now() % 8 != 0:
            continue

        sparks = CircularParticle(
            origin=PointF(
                x=eye_x + random_offset() * source.radius * 2,
                y=eye_y + random_offset() * source.radius * 2,
            ),
            initial_velocity=VectorF(0, 0)
            if vel_magnitude == 0
            else (
                VectorF(x=random_offset() * 5, y=random_offset() * 5) + 1 * -source.velocity
            ).as_vector(),
            size=0.2,
            initial_color=RGB(255, 255, 200, 1),  # almost white hot
            ending_color=RGB(40, 5, 0, 1),  # dark orange
            life_time=70,
            gravity=0.1,
            engine=engine,
        )
        pieces.append(sparks)

    pieces = sorted(pieces, key=random_offset)

    engine.scenario.bg_shapes[0:0] = pieces
