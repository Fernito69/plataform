from random import random
from typing import TYPE_CHECKING

from model.base import PointF, VectorF
from model.theme import RGB
from physics2d.entities.equipment.projectile import Projectile
from physics2d.shapes.model.shared import TransitionType
from physics2d.shapes.shape import Shape
from utils import random_offset, random_offset_vector

if TYPE_CHECKING:
    from physics2d.scenario.scenario import Scenario
    from physics2d.shapes.circunference import Circunference


def bullet(scenario: "Scenario", source: "Circunference") -> None:
    bullet = Projectile(
        origin=source.center + random_offset_vector(),
        initial_velocity=(
            ((5 + random_offset()) * source.get_last_known_direction()) + source.velocity
        ).as_vector(),
        size=1,
        size_change_type=TransitionType.NONE,
        initial_color=RGB(255, 255, 255, 1),
        ending_color=RGB(30, 30, 30, intensity=1),  # smokelike
        life_time=50,
    )
    scenario.projectiles.append(bullet)
