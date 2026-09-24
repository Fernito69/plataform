import math
from typing import TYPE_CHECKING

from constants import PI
from model.base import PointF, VectorF
from model.theme import RGB, Theme
from physics2d.entities.base import PhysicsEntity
from physics2d.entities.enemies.stalking_enemy import StalkingEnemy
from physics2d.entities.enemy import Enemy
from physics2d.shape.factories.projectile import get_rocket
from physics2d.shape.model.shared import TransitionType
from physics2d.shape.particle.circular_particle import CircularParticle
from utils import random_offset

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

_NUM_SATELLITES = 3
_ROCKET_LAUNCHER_SATELLITE_RADIUS = 4
_SATELLITE_ANGULAR_SPEED = 3


class SuperRocketEnemy(StalkingEnemy):
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
            projectile_generator=None,
        )
        self._last_known_direction = self.velocity

        _rocket_launcher = get_rocket(
            is_enemy=True,
            damage=_DAMAGE,
            rocket_speed=rocket_speed,
            life_time=life_time,
            blast_radius=blast_radius,
            max_blast_damage=max_blast_damage,
            size=_SIZE,
        )
        self._particle_generator = main_thruster

        satellites: list[Enemy | PhysicsEntity] = [
            Enemy(
                projectile_generator=_rocket_launcher,
                engine=engine,
                position=PointF(
                    position.x + size + _ROCKET_LAUNCHER_SATELLITE_RADIUS,
                    position.y,
                ).rotate(((num / _NUM_SATELLITES) * (2 * PI)), position),
                size=_ROCKET_LAUNCHER_SATELLITE_RADIUS,
                theme=Theme(color=theme.color.with_intensity(0.7) if theme.color else None),
                density=1,
                health=None,
                precision=precision,
                aggressivity=aggressivity,
                particle_generator=satellite_thrusters,
            )
            for num in range(_NUM_SATELLITES)
        ]
        self.extra_shapes = satellites

    def _apply_movement(self) -> None:
        super()._apply_movement()

        # move satellites:
        for enemy in self.extra_shapes:
            if not isinstance(enemy, Enemy):
                return
            # TODO: these should happen in a parent class
            enemy._move_by(self.velocity)
            enemy._generate_particles()
            enemy._attack_player()
            enemy._apply_collisions()
            enemy.center = enemy.center.rotate(math.radians(_SATELLITE_ANGULAR_SPEED), self.center)
            enemy.position = enemy.center


def satellite_thrusters(engine: "Physics2D", source: "PhysicsEntity") -> None:
    pieces = []

    _particle_density = 3
    for i in range(_particle_density):
        # little particles doing particle stuff
        _particle = CircularParticle(
            origin=(
                source.center
                - (i + 1 / _particle_density) * source.velocity
                - source.get_last_known_direction() * 2
            )
            + source.size * VectorF.random_offset_vector(),
            initial_velocity=(
                +0.2 * VectorF.random_offset_vector() - source.get_last_known_direction()
            ).as_vector(),
            size=0.7 + random_offset(),
            size_change_type=TransitionType.LINEAR_DECREASE,
            initial_color=RGB(255, 0, 255),
            ending_color=RGB(0, 0, 80, 1),
            ending_color_fade_type=TransitionType.LINEAR_DECREASE,
            life_time=15,
            gravity=-0.07,
            floating_multi=0.01,
            engine=engine,
        )
        pieces.append(_particle)

    engine.scenario.bg_shapes[0:0] = pieces


def main_thruster(engine: "Physics2D", source: "PhysicsEntity") -> None:
    pieces = []

    _particle_density = 3
    for i in range(_particle_density):
        # little particles doing particle stuff
        _particle = CircularParticle(
            origin=(source.center) + source.size * VectorF.random_offset_vector(),
            initial_velocity=(+0.2 * VectorF.random_offset_vector()).as_vector(),
            size=2,
            size_change_type=TransitionType.LINEAR_DECREASE,
            initial_color=RGB(255, 0, 255),
            ending_color=RGB(0, 0, 80, 1),
            ending_color_fade_type=TransitionType.LINEAR_DECREASE,
            life_time=15,
            gravity=-0.07,
            floating_multi=1,
            engine=engine,
        )
        pieces.append(_particle)

    engine.scenario.bg_shapes[0:0] = pieces
