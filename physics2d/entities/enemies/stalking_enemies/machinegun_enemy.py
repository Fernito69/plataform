from typing import TYPE_CHECKING

from model.base import PointF
from model.theme import RGB, Theme
from physics2d.entities.enemies.stalking_enemy import StalkingEnemy
from physics2d.shape.factories.projectile import get_bullet

if TYPE_CHECKING:
    from physics2d.physics2d import Physics2D

_IDEAL_DISTANCE_FROM_PLAYER = 60
_IDEAL_DISTANCE_FROM_ENEMIES = 20
_MAX_VELOCITY = 4
_PRECISSION = 0.3
_AGGRESSIVITY = 0.05

_BULLET_COLOR = RGB(255, 240, 150)
_BULLET_EDNING_COLOR = RGB(60, 50, 3)
_BULLET_SPEED = 6
_BULLET_SIZE = 1.1
_HEALTH = 150


class MachineGunEnemy(StalkingEnemy):
    def __init__(
        self,
        engine: "Physics2D",
        size: float,
        health: float = _HEALTH,
        name: str = "SmallEnemy",
        position: PointF = PointF(0, 0),
        theme: Theme = Theme(),
        secondary_theme: Theme = Theme(),
        color_gradient_exponent: float = 1,
        color_gradient_exponent_end: float | None = 0.3,
        color_gradient_exponent_cycling_factor: float = 9,
        precision: float = _PRECISSION,
        aggressivity: float = _AGGRESSIVITY,
        max_velocity: float = _MAX_VELOCITY,
        show_health: bool = True,
    ):
        _machine_gun = get_bullet(
            is_enemy=True,
            initial_color=_BULLET_COLOR,
            ending_color=_BULLET_EDNING_COLOR,
            speed=_BULLET_SPEED,
            size=_BULLET_SIZE,
        )

        super().__init__(
            health=health,
            size=size,
            name=name,
            position=position,
            theme=theme,
            secondary_theme=secondary_theme,
            color_gradient_exponent=color_gradient_exponent,
            engine=engine,
            precision=precision,
            aggressivity=aggressivity,
            min_distance_from_player=_IDEAL_DISTANCE_FROM_PLAYER,
            min_distance_from_other_enemies=_IDEAL_DISTANCE_FROM_ENEMIES,
            max_velocity=max_velocity,
            projectile_generator=_machine_gun,
            show_health=show_health,
            color_gradient_exponent_cycling_factor=color_gradient_exponent_cycling_factor,
            color_gradient_exponent_end=color_gradient_exponent_end,
        )
