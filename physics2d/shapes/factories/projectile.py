from random import random
from typing import TYPE_CHECKING

from model.base import VectorF
from model.theme import RGB
from physics2d.entities.equipment.projectile import Projectile
from physics2d.shapes.factories.explosion import bullet_ricochet
from physics2d.shapes.model.shared import TransitionType
from utils import get_vector_angle, random_offset, random_offset_vector

if TYPE_CHECKING:
    from physics2d.scenario.scenario import Scenario
    from physics2d.shapes.circunference import Circunference


def bullet(scenario: "Scenario", source: "Circunference") -> None:
    bullet = Projectile(
        # TODO: fix this typing in the ParticleGeneratorm should be PhysicsEntity?
        owner=source,
        origin=source.center + random_offset_vector(),
        initial_velocity=(
            ((10 + random_offset()) * source.get_last_known_direction()) + source.velocity
        ).as_vector(),
        size=0.7,
        size_change_type=TransitionType.NONE,
        initial_color=RGB(127 + random_offset() * 80, 255 - random() * 60, 255, 1),
        ending_color=RGB(30, 30, 30, intensity=1),
        life_time=50,
        damage=10,
        explosion_generator=bullet_ricochet,
    )
    scenario.projectiles.append(bullet)


def buckshot(scenario: "Scenario", source: "Circunference") -> None:
    _NUM_PELLETS = 10
    pellets: list[Projectile] = []

    for _ in range(_NUM_PELLETS):
        pellet = Projectile(
            owner=source,
            origin=source.center + random_offset_vector(),
            initial_velocity=(
                ((10 + random_offset()) * source.get_last_known_direction())
                + source.velocity
                + VectorF(0, 2 * random_offset()).rotate(
                    get_vector_angle((-source.velocity).as_vector())
                )
            ).as_vector(),
            size=0.6,
            size_change_type=TransitionType.NONE,
            initial_color=RGB(127 + random_offset() * 80, 255 - random() * 60, 255, 1),
            ending_color=RGB(30, 30, 30, intensity=1),
            life_time=50,
            damage=8,
            explosion_generator=bullet_ricochet,
        )
        pellets.append(pellet)

    scenario.projectiles[0:0] = pellets
