from functools import reduce
from typing import TYPE_CHECKING

from model.base import PointF, VectorF
from model.theme import Theme
from physics2d.entities.enemy import Enemy
from physics2d.entities.model.shared import ParticleGenerator

if TYPE_CHECKING:
    from physics2d.physics2d import Physics2D


class StalkingEnemy(Enemy):
    """Always tries to keep the same distance from the player"""

    _projectile_generator: ParticleGenerator | None
    _max_velocity: float
    _min_distance_from_player: float
    _min_distance_from_other_enemies: float

    def __init__(
        self,
        projectile_generator: ParticleGenerator | None,
        engine: "Physics2D",
        size: float,
        health: float,
        precision: float = 0,
        aggressivity: float = 0.05,
        name: str = "ShootingEnemy",
        position: PointF = PointF(0, 0),
        theme: Theme = Theme(),
        max_velocity: float = 4,
        min_distance_from_player: float = 60,
        min_distance_from_other_enemies: float = 20,
        stretch_vector: VectorF = VectorF(1, 1),
    ):
        super().__init__(
            health=health,
            size=size,
            name=name,
            position=position,
            theme=theme,
            engine=engine,
            projectile_generator=projectile_generator,
            precision=precision,
            aggressivity=aggressivity,
            stretch_vector=stretch_vector,
        )
        self._last_known_direction = self.velocity
        self._max_velocity = max_velocity
        self._min_distance_from_other_enemies = min_distance_from_other_enemies
        self._min_distance_from_player = min_distance_from_player

    def _apply_movement(self) -> None:
        self._apply_collisions()

        enemies_in_range = self._engine.scenario.get_enemies_in_range(
            self._min_distance_from_other_enemies,
            self,
            calc_distance_to_border=True,
        )

        if len(enemies_in_range) > 0:
            # go in the opposite direction of the center of gravity of other enemies
            center_of_gravity = reduce(
                lambda acc, res: acc + res.enemy.position,
                enemies_in_range,
                PointF(0, 0),
            ) * (1 / len(enemies_in_range))
            self.velocity = (
                self.velocity + (self.position - center_of_gravity).as_vector().unit_vector()
            ).as_vector()

        self._move_by(self.velocity)

    def _apply_collisions(self) -> None:
        _pushback_factor = 3

        if self.would_collide_with(self._engine.player):
            self.velocity = (_pushback_factor * self.velocity).as_vector()

        for enemy in self._engine.scenario.enemies:
            if self.would_collide_with(enemy):
                self.velocity = (_pushback_factor * self.velocity).as_vector()

    def do_your_thing(self) -> None:
        super().do_your_thing()

        # enemy AI
        self._approach_player()

    def _approach_player(self) -> None:
        player = self._engine.player
        player_direction = self.position - player.position
        if (distance_from_player := abs(player_direction)) > self._min_distance_from_player:
            velocity_magnitude = min(
                1 - distance_from_player / self._min_distance_from_player,
                self._max_velocity,
            )
            self.velocity = player_direction.as_vector().unit_vector(velocity_magnitude)
