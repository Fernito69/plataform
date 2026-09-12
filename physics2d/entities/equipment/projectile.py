from typing import TYPE_CHECKING

from model.base import PointF, VectorF
from model.theme import RGB
from physics2d.shapes.model.shared import TransitionType
from physics2d.shapes.particle import CircularParticle

if TYPE_CHECKING:
    from physics2d.entities.enemy import Enemy
    from physics2d.entities.equipment.model.shared import ParticleGenerator
    from physics2d.entities.player_blob import PlayerBlob
    from physics2d.physics2d import Physics2D


class Projectile(CircularParticle):
    damage: float
    owner: "PlayerBlob | Enemy"
    _explosion_generator: "ParticleGenerator"

    def __init__(
        self,
        owner: "PlayerBlob | Enemy",
        origin: PointF,
        size: float,
        damage: float,
        initial_color: RGB,
        explosion_generator: "ParticleGenerator",
        initial_velocity: VectorF = VectorF(0, 0),
        gravity: float | None = None,
        ending_color: RGB | None = None,
        life_time: int | None = None,
        size_change_type: TransitionType = TransitionType.NONE,
        ending_color_fade_type: TransitionType = TransitionType.LINEAR_DECREASE,
        floating_multi: float = 0,
    ):
        super().__init__(
            origin,
            size,
            initial_color,
            initial_velocity,
            gravity,
            ending_color,
            life_time,
            size_change_type,
            ending_color_fade_type,
            floating_multi,
        )
        self.damage = damage
        self.owner = owner
        self.name = "Projectile"
        self.is_collideable = True
        self._explosion_generator = explosion_generator

    def hit(self, engine: "Physics2D") -> None:
        self._explosion_generator(engine.scenario, self)
        engine.scenario.projectiles.remove(self)
