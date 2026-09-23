from typing import TYPE_CHECKING

from model.base import VectorF
from model.theme import RGB
from physics2d.shape.model.shared import TransitionType
from physics2d.shape.particle.circular_particle import CircularParticle

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
    homing_targets_projectiles: bool
    target_projectiles_above_size: float
    initial_velocity: VectorF

    _explosion_generator: "ParticleGenerator"
    _trail_generator: "ParticleGeneratorWithTarget | None"

    explode_on_life_time_over: bool
    is_enemy: bool
    exploded: bool

    def __init__(
        self,
        owner: "PhysicsEntity",
        size: float,
        damage: float,
        engine: "Physics2D",
        initial_color: RGB,
        explosion_generator: "ParticleGenerator",
        is_enemy: bool = False,
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
        homing_targets_projectiles: bool = True,
        homing_kick_in_time: float = 0,
        target_projectiles_above_size: float = 0.7,
        offset_from_origin: VectorF = VectorF(0, 0),
    ):
        super().__init__(
            origin=owner,
            engine=engine,
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
            offset_from_origin=offset_from_origin,
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
        self.offset_from_origin = offset_from_origin
        self.is_enemy = is_enemy
        self.homing_targets_projectiles = homing_targets_projectiles
        self.target_projectiles_above_size = target_projectiles_above_size
        self.exploded = False

    def _apply_movement(self) -> None:
        from physics2d.entities.enemy import Enemy

        if self.target:
            if (isinstance(self.target, Enemy) and self.target.health <= 0) or (
                isinstance(self.target, Projectile) and self.target.exploded
            ):
                self.target = None
                return
            to_target = (
                self.homing_factor
                * (self.target.position - self.position).as_vector().unit_vector()
            )
            vel_contrib = (1 / self.homing_factor) * self.velocity
            self.velocity = (vel_contrib + to_target).as_vector()
        elif (
            self.target_acquire_threshold is not None
            and self._original_life_time is not None
            and self.life_time is not None
            and (self._original_life_time - self.life_time) >= self.homing_kick_in_time
        ):
            # Check for enemies nearby
            possible_victims = self._engine.scenario.get_enemies_in_range(
                self.target_acquire_threshold,
                self,
                calc_distance_to_border=True,
            )
            if len(possible_victims) > 0:
                self.target = possible_victims[0].enemy

            if not self.target and self.homing_targets_projectiles:
                projectiles_nearby = self._engine.scenario.get_projectiles_in_range(
                    max_range=self.target_acquire_threshold,
                    subject=self,
                    calc_distance_to_border=True,
                    # TODO: this doesn't work!
                    size_above=self.target_projectiles_above_size,
                )
                if len(projectiles_nearby) > 0:
                    self.target = projectiles_nearby[0].projectile

        self._apply_collisions()
        self._generate_trail()
        super()._apply_movement()

    def _generate_trail(self) -> None:
        if self._trail_generator:
            self._trail_generator(self._engine, self, self.target)

    def _apply_collisions(self) -> None:
        # TODO: fix enemies being pushed back by bullet impacts

        if self.is_enemy:
            if self.would_collide_with(self._engine.player):
                self._engine.player.receive_damage(self.damage)
                return self.hit()

            for proj in self._engine.scenario.projectiles:
                if self.would_collide_with(proj):
                    proj.hit()
                    return self.hit()

        else:
            for enemy in self._engine.scenario.enemies:
                if self.would_collide_with(enemy):
                    enemy.receive_damage(self.damage)
                    return self.hit()

            for proj in self._engine.scenario.enemy_projectiles:
                if self.would_collide_with(proj):
                    proj.hit()
                    return self.hit()

    def hit(self) -> None:
        self._explosion_generator(self._engine, self)
        self.exploded = True

        if not self.is_enemy:
            self._engine.scenario.projectiles = [
                p for p in self._engine.scenario.projectiles if p is not self
            ]
        else:
            self._engine.scenario.enemy_projectiles = [
                p for p in self._engine.scenario.enemy_projectiles if p is not self
            ]
