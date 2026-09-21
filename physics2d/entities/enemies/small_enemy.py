from typing import TYPE_CHECKING

from model.base import PointF
from model.theme import RGB, Theme
from physics2d.entities.enemy import Enemy
from physics2d.entities.model.shared import ParticleGenerator
from physics2d.shape.factories.projectile import get_bullet
from utils import random_offset

if TYPE_CHECKING:
    from physics2d.physics2d import Physics2D

_IDEAL_DISTANCE_FROM_PLAYER = 60
_MAX_VELOCITY = 4


class SmallEnemy(Enemy):
    _projectile_generator: ParticleGenerator

    def __init__(
        self,
        engine: "Physics2D",
        size: float,
        health: float,
        name: str = "SmallEnemy",
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
            projectile_generator=get_bullet(
                is_enemy=True, initial_color=RGB(255, 150, 150), speed=6
            ),
            precision=0.3,
            aggressivity=0.05,
        )
        self._last_known_direction = self.velocity

    def _apply_movement(self) -> None:
        if self.would_collide_with(self._engine.player):
            self.velocity = (3 * self.velocity).as_vector()

        for enemy in self._engine.scenario.enemies:
            if self.would_collide_with(enemy):
                self.velocity = (3 * self.velocity).as_vector()

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
                0.8 - distance_from_player / _IDEAL_DISTANCE_FROM_PLAYER,
                _MAX_VELOCITY,
            )
            self.velocity = player_direction.as_vector().unit_vector(velocity_magnitude)
