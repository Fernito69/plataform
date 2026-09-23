from typing import TYPE_CHECKING

from model.base import PointF
from model.theme import Theme
from physics2d.entities.enemies.shooting_enemy import ShootingEnemy
from physics2d.shape.factories.projectile import get_rocket

if TYPE_CHECKING:
    from physics2d.physics2d import Physics2D

_IDEAL_DISTANCE_FROM_PLAYER = 60
_IDEAL_DISTANCE_FROM_ENEMIES = 20
_MAX_VELOCITY = 3
_PRECISSION = 0.2
_AGGRESSIVITY = 0.03

_DAMAGE = 100
_ROCKET_SPEED = 4
_LIFE_TIME = 100
_BLAST_RADIUS = 20
_MAX_BLAST_DAMAGE = 80
_SIZE = 1.2


class RocketEnemy(ShootingEnemy):
    def __init__(
        self,
        engine: "Physics2D",
        size: float,
        health: float,
        name: str = "RocketEnemy",
        position: PointF = PointF(0, 0),
        theme: Theme = Theme(),
        rocket_speed: float = _ROCKET_SPEED,
        life_time: int = _LIFE_TIME,
        blast_radius: float = _BLAST_RADIUS,
        max_blast_damage: float = _MAX_BLAST_DAMAGE,
        precision: float = _PRECISSION,
        aggressivity: float = _AGGRESSIVITY,
        max_velocity: float = _MAX_VELOCITY,
    ):
        _rocket_launcher = get_rocket(
            is_enemy=True,
            damage=_DAMAGE,
            rocket_speed=rocket_speed,
            life_time=life_time,
            blast_radius=blast_radius,
            max_blast_damage=max_blast_damage,
            size=_SIZE,
        )

        super().__init__(
            health=health,
            size=size,
            name=name,
            position=position,
            theme=theme,
            engine=engine,
            min_distance_from_player=_IDEAL_DISTANCE_FROM_PLAYER,
            min_distance_from_other_enemies=_IDEAL_DISTANCE_FROM_ENEMIES,
            max_velocity=max_velocity,
            precision=precision,
            aggressivity=aggressivity,
            projectile_generator=_rocket_launcher,
        )
        self._last_known_direction = self.velocity
