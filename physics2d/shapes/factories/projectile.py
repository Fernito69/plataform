from random import random
from typing import TYPE_CHECKING

from model.theme import RGB
from physics2d.entities.equipment.projectile import Projectile
from physics2d.shapes.factories.explosion import bullet_ricochet
from physics2d.shapes.model.shared import TransitionType
from utils import random_offset, random_offset_vector

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
