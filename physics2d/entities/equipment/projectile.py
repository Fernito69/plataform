from typing import TYPE_CHECKING

from model.base import PointF, VectorF
from model.theme import RGB
from physics2d.shapes.model.shared import TransitionType
from physics2d.shapes.particle import CircularParticle

if TYPE_CHECKING:
    from physics2d.entities.base import PhysicsEntity
    from physics2d.entities.model.shared import ParticleGenerator, ParticleGeneratorWithTarget
    from physics2d.physics2d import Physics2D


class Projectile(CircularParticle):
    damage: float
    owner: "PhysicsEntity"

    target: "PhysicsEntity | None"
    target_acquire_threshold: float | None
    homing_factor: float
    homing_kick_in_time: float
    initial_velocity: VectorF

    _explosion_generator: "ParticleGenerator"
    _trail_generator: "ParticleGeneratorWithTarget | None"

    explode_on_life_time_over: bool

    def __init__(
        self,
        owner: "PhysicsEntity",
        origin: PointF,  # TODO: DEPRECATE
        size: float,
        damage: float,
        initial_color: RGB,
        explosion_generator: "ParticleGenerator",
        particle_generator: "ParticleGenerator | None" = None,
        trail_generator: "ParticleGeneratorWithTarget | None" = None,
        initial_velocity: VectorF = VectorF(0, 0),
        gravity: float | None = None,
        ending_color: RGB | None = None,
        life_time: int | None = None,
        size_change_type: TransitionType = TransitionType.NONE,
        ending_color_fade_type: TransitionType = TransitionType.LINEAR_DECREASE,
        floating_multi: float = 0,
        density: float = 1,
        explode_on_life_time_over: bool = False,
        target: "PhysicsEntity | None" = None,
        target_acquire_threshold: float | None = None,
        homing_factor: float = 1,
        homing_kick_in_time: float = 0,
    ):
        super().__init__(
            # origin=origin,
            origin=owner,
            size=size,
            initial_color=initial_color,
            initial_velocity=initial_velocity,
            gravity=gravity,
            ending_color=ending_color,
            life_time=life_time,
            size_change_type=size_change_type,
            ending_color_fade_type=ending_color_fade_type,
            floating_multi=floating_multi,
            density=density,
            particle_generator=particle_generator,
        )
        self.damage = damage
        self.owner = owner
        self.name = "Projectile"
        self.is_collideable = True
        self._explosion_generator = explosion_generator
        self._trail_generator = trail_generator
        self._particle_generator = particle_generator
        self.explode_on_life_time_over = explode_on_life_time_over
        self.target = target
        self.target_acquire_threshold = target_acquire_threshold
        self.homing_factor = homing_factor
        self.homing_kick_in_time = homing_kick_in_time
        self.initial_velocity = initial_velocity

    def hit(self, engine: "Physics2D") -> None:
        self._explosion_generator(engine.scenario, self)
        engine.scenario.projectiles.remove(self)
