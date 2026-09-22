from functools import reduce
from typing import TYPE_CHECKING

from model.base import PointF
from model.theme import Theme
from physics2d.entities.enemy import Enemy
from physics2d.entities.model.shared import ParticleGenerator
from physics2d.shape.factories.projectile import get_rocket
from utils import random_offset

if TYPE_CHECKING:
    from physics2d.physics2d import Physics2D

_IDEAL_DISTANCE_FROM_PLAYER = 60
_IDEAL_DISTANCE_FROM_ENEMIES = 20
_MAX_VELOCITY = 4

_DAMAGE = 100
_ROCKET_SPEED = 8
_LIFE_TIME = 100
_BLAST_RADIUS = 20
_MAX_BLAST_DAMAGE = 100
_SIZE = 1.2


class RocketEnemy(Enemy):
    _projectile_generator: ParticleGenerator

    def __init__(
        self,
        engine: "Physics2D",
        size: float,
        health: float,
        name: str = "RocketEnemy",
        position: PointF = PointF(0, 0),
        theme: Theme = Theme(),
    ):
        super().__init__(
            health=health,
            size=size,
            name=name,
            position=position,
            theme=theme,
            engine=engine,
            projectile_generator=get_rocket(
                is_enemy=True,
                damage=_DAMAGE,
                rocket_speed=_ROCKET_SPEED,
                life_time=_LIFE_TIME,
                blast_radius=_BLAST_RADIUS,
                max_blast_damage=_MAX_BLAST_DAMAGE,
                size=_SIZE,
            ),
            precision=0.3,
            aggressivity=0.05,
        )
        self._last_known_direction = self.velocity

    # TODO: Maybe make a basic shooting enemy class with all these methods below
    def _apply_movement(self) -> None:
        if self.would_collide_with(self._engine.player):
            self.velocity = (3 * self.velocity).as_vector()

        enemies_in_range = self._engine.scenario.get_enemies_in_range(
            _IDEAL_DISTANCE_FROM_ENEMIES,
            self,
            calc_distance_to_border=True,
        )
        if len(enemies_in_range) > 0:
            # go in the opposite direction of the center of gravity of them all
            center_of_gravity = reduce(
                lambda acc, res: acc + res.enemy.position,
                enemies_in_range,
                PointF(0, 0),
            ) * (1 / len(enemies_in_range))
            self.velocity = (
                self.velocity + (self.position - center_of_gravity).as_vector().unit_vector()
            ).as_vector()

        for enemy in self._engine.scenario.enemies:
            if self.would_collide_with(enemy):
                self.velocity = (2 * self.velocity).as_vector()

        self._move_by(self.velocity)

    def do_your_thing(self) -> None:
        super().do_your_thing()

        # enemy AI
        self._approach_player()
        self._attack_player()

    def _attack_player(self) -> None:
        if 0.5 - self._aggressivity < random_offset():
            self._projectile_generator(self._engine, self)

    def _approach_player(self) -> None:
        player = self._engine.player
        player_direction = self.position - player.position
        if (distance_from_player := abs(player_direction)) > _IDEAL_DISTANCE_FROM_PLAYER:
            velocity_magnitude = min(
                1 - distance_from_player / _IDEAL_DISTANCE_FROM_PLAYER,
                _MAX_VELOCITY,
            )
            self.velocity = player_direction.as_vector().unit_vector(velocity_magnitude)
