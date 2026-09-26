from random import random
from typing import TYPE_CHECKING

from model.base import PointF, VectorF
from model.theme import RGB, Theme
from physics2d.entities.equipment.thruster import Thruster
from physics2d.shape.model.shared import TransitionType
from physics2d.shape.particle.circular_particle import CircularParticle
from utils import random_offset

if TYPE_CHECKING:
    from physics2d.entities.base import PhysicsEntity
    from physics2d.physics2d import Physics2D


class SoapyThruster(Thruster):
    """Looks like SOAP bubbles!"""

    def __init__(self, engine: "Physics2D"):
        super().__init__(
            particle_generator=ln2_vapor,
            name="SoapyThruster",
            player_theme=Theme(
                color=RGB(0, 0, 255),
            ),
            max_speed=5,
            accel=0.4,
            decel=0.2,
            engine=engine,
        )


################


def ln2_vapor(engine: "Physics2D", source: "PhysicsEntity") -> None:
    pieces: list[CircularParticle] = []
    velocity_magnitude = abs(source.velocity)

    for _i in range(1, int(source.radius * 2)):
        i = _i / 2
        distance_factor = (source.radius - i) * 1
        eye_x = source.center.x - source.velocity.x * distance_factor
        eye_y = source.center.y - source.velocity.y * distance_factor

        is_odd = _i % 2 == 1
        _randomness_multi = random() * 3
        _radius_factor = random() * 1

        # Liquid N2 trail
        _ln2_color = (
            RGB(
                127,
                223 - (i - 1) * 14,
                255 - (i - 1) * 5,
            )
            if is_odd
            else RGB(
                127,
                220 - (i - 1) * 10,
                255 - (i - 1) * 14,
            )
        )

        _VAPOR_SPAWN_RANDOMNESS_FACTOR = 2

        vapor = CircularParticle(
            origin=PointF(
                x=eye_x
                + random_offset() * _VAPOR_SPAWN_RANDOMNESS_FACTOR * _randomness_multi
                + random_offset() * 0.5,
                y=eye_y
                + random_offset() * _VAPOR_SPAWN_RANDOMNESS_FACTOR * _randomness_multi
                + random_offset() * 0.5,
            ),
            initial_velocity=VectorF(
                x=source.velocity.x * _VAPOR_SPAWN_RANDOMNESS_FACTOR * _randomness_multi * 0.1
                + random_offset() * 0.5,
                y=source.velocity.y * _VAPOR_SPAWN_RANDOMNESS_FACTOR * _randomness_multi * 0.1
                + random_offset() * 0.5,
            ),
            engine=engine,
            # radius=i * math.cos((size - i) / size),
            size=i * _radius_factor,
            size_change_type=TransitionType.LINEAR_DECREASE,
            initial_color=_ln2_color,
            ending_color=RGB(177, 255, 255, opacity=0.1),  # N2 like
            ending_color_fade_type=TransitionType.LINEAR_DECREASE,
            life_time=50,
            gravity=0.02,
            floating_multi=0.1 * velocity_magnitude,
        )
        pieces.append(vapor)

        if i % 10 == 0:
            icy_sparks = CircularParticle(
                origin=PointF(
                    x=eye_x + random_offset() * 0.1 + source.velocity.x * 3,
                    y=eye_y + source.velocity.y * 3,
                ),
                initial_velocity=(
                    -VectorF(x=random_offset() * 1, y=random_offset() * velocity_magnitude)
                    + 0.5 * source.velocity
                ).as_vector(),
                size=0.8,
                initial_color=RGB(255, 255, 255, 1),
                life_time=50,
                gravity=0.1,
                engine=engine,
            )
            # pieces.append(icy_sparks)
            engine.scenario.bg_shapes.append(icy_sparks)

    pieces = sorted(pieces, key=random_offset)

    for index in range(len(pieces)):
        if index % 8 == 0:
            engine.scenario.fg_shapes.append(pieces[index])
        else:
            engine.scenario.bg_shapes.append(pieces[index])
