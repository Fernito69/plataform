from typing import TYPE_CHECKING

from model.base import PointF
from model.theme import RGB, Theme
from physics2d.entities.enemies.shooting_enemy import ShootingEnemy
from physics2d.shape.factories.projectile import get_bullet

if TYPE_CHECKING:
    from physics2d.physics2d import Physics2D

_IDEAL_DISTANCE_FROM_PLAYER = 60
_IDEAL_DISTANCE_FROM_ENEMIES = 20
_MAX_VELOCITY = 4
_PRECISSION = 0.3
_AGGRESSIVITY = 0.05

_BULLET_COLOR = RGB(255, 150, 150)
_BULLET_SPEED = 6


class MachineGunEnemy(ShootingEnemy):
    def __init__(
        self,
        engine: "Physics2D",
        size: float,
        health: float,
        name: str = "SmallEnemy",
        position: PointF = PointF(0, 0),
        theme: Theme = Theme(),
        precision: float = _PRECISSION,
        aggressivity: float = _AGGRESSIVITY,
        max_velocity: float = _MAX_VELOCITY,
    ):
        _machine_gun = get_bullet(
            is_enemy=True,
            initial_color=_BULLET_COLOR,
            speed=_BULLET_SPEED,
        )

        super().__init__(
            health=health,
            size=size,
            name=name,
            position=position,
            theme=theme,
            engine=engine,
            precision=precision,
            aggressivity=aggressivity,
            min_distance_from_player=_IDEAL_DISTANCE_FROM_PLAYER,
            min_distance_from_other_enemies=_IDEAL_DISTANCE_FROM_ENEMIES,
            max_velocity=max_velocity,
            projectile_generator=_machine_gun,
        )
