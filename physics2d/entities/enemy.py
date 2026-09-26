import math
from random import random
from typing import TYPE_CHECKING

from model.base import PointF, VectorF
from model.theme import RGB, Theme
from physics2d.entities.base import PhysicsEntity
from physics2d.entities.model.shared import ParticleGenerator
from physics2d.entities.model.spawner import Spawner
from physics2d.shape.factories.explosion import enemy_explosion, get_smoke_generator
from physics2d.shape.model.shared import TransitionType
from physics2d.shape.particle.circular_particle import CircularParticle
from utils import random_offset

if TYPE_CHECKING:
    from physics2d.physics2d import Physics2D
    from physics2d.shape.base import Shape


class Enemy(PhysicsEntity):
    _engine: "Physics2D"
    health: float | None

    _initial_health: float | None
    _initial_theme: Theme

    _projectile_generator: ParticleGenerator | None
    # The closer to 0, the more precise
    _precision: float
    # from 0 to 1
    _aggressivity: float

    _spawner_on_death: Spawner | None

    _color_cycling_factor: float

    def __init__(
        self,
        engine: "Physics2D",
        size: float,
        health: float | None,
        density: float = 1,
        name: str = "Enemy",
        position: PointF = PointF(0, 0),
        theme: Theme = Theme(),
        angle: float = 0,
        affected_by_gravity: bool = False,
        initial_velocity: VectorF = VectorF(0, 0),
        initial_angular_velocity: float = 0,
        own_gravity: float | None = None,
        secondary_theme: Theme | None = None,
        floating_multi: float = 0,
        extra_shapes: list["PhysicsEntity | Shape"] = [],
        projectile_generator: ParticleGenerator | None = None,
        particle_generator: ParticleGenerator | None = None,
        precision: float = 0,
        aggressivity: float = 0,
        spawner_on_death: Spawner | None = None,
        color_cycling_factor: float = 57,
    ):
        super().__init__(
            density=density,
            floating_multi=floating_multi,
            size=size,
            name=name,
            position=position,
            theme=theme,
            angle=angle,
            affected_by_gravity=affected_by_gravity,
            initial_angular_velocity=initial_angular_velocity,
            initial_velocity=initial_velocity,
            own_gravity=own_gravity,
            secondary_theme=secondary_theme,
            is_collideable=True,
            extra_shapes=extra_shapes,
            engine=engine,
            particle_generator=particle_generator,
        )
        self._engine = engine
        self.health = health
        self._initial_health = health
        self._initial_theme = Theme(color=theme.color)
        self.secondary_theme = secondary_theme
        self.theme = theme
        self.name = name
        self.extra_shapes = extra_shapes
        self._projectile_generator = projectile_generator
        self._precision = precision
        self._aggressivity = aggressivity
        self._last_known_direction = initial_velocity
        self._spawner_on_death = spawner_on_death
        self._color_cycling_factor = color_cycling_factor

    def receive_damage(self, amount: float) -> None:
        if self.health is None:
            return

        self.health -= amount

        if not self._initial_theme.color:
            return

        _damage_color = RGB(80, 0, 0, 1)

        _factor = self.get_health_ratio()
        _new_color = (
            self.secondary_theme.color
            if self.secondary_theme and self.secondary_theme.color
            else _damage_color
        ).get_gradient(
            self._initial_theme.color,
            _factor,
        )

        self.theme.color = _new_color

    def get_health_ratio(self) -> float:
        return (
            (self.health / self._initial_health)
            if self.health is not None and self._initial_health is not None
            else 1
        )

    def _cycle_color(self) -> None:
        if not self._initial_theme.color or not self.secondary_theme:
            return

        _color_1 = self._initial_theme.color
        _color_2 = self.secondary_theme.color or RGB()
        if _color_1 == _color_2:
            return

        color = _color_1.get_gradient(
            _color_2,
            abs(math.sin(self._engine.scenario.now() / self._color_cycling_factor)),
        )
        self.theme.color = color

    def _cycle_opacity(self) -> None:
        if not self.theme.color or (
            self._initial_theme.color and self._initial_theme.color.opacity == 1
        ):
            return

        self.theme.color = RGB(
            self.theme.color.r,
            self.theme.color.g,
            self.theme.color.b,
            opacity=abs(
                math.sin(self._engine.scenario.now() / 50),
            ),
        )

    def _spawn_on_death(self) -> None:
        if self._spawner_on_death:
            self._spawner_on_death(self._engine, self)

    def die(self, _death_explosion_size: int | None = None) -> None:
        self._explode(_death_explosion_size)
        self._spawn_on_death()

        # kill "satellites"
        for satellites in self.extra_shapes:
            if not isinstance(satellites, Enemy):
                return
            satellites.die()

        self._engine.scenario.enemies = [e for e in self._engine.scenario.enemies if e is not self]

    def _explode(self, _death_explosion_size: int | None = None) -> None:
        enemy_explosion(self._engine, self, _death_explosion_size or self.radius * 2)

    def get_aiming_direction(self) -> VectorF:
        direction = (self._engine.player.position - self.position).as_vector().unit_vector()
        return (
            direction
            + VectorF.random_offset_vector(0, self._precision).rotate(direction.get_angle())
        ).as_vector()

    def _apply_collisions(self) -> None:
        ...
        # TODO: figure this out
        # _pushback_factor = 1

        # if self.would_collide_with(self._engine.player):
        #     self.velocity = (_pushback_factor * self.velocity).as_vector()

        # for enemy in self._engine.scenario.enemies:
        #     if self.would_collide_with(enemy):
        #         self.velocity = (_pushback_factor * self.velocity).as_vector()
        #         enemy.velocity = (enemy.velocity + _pushback_factor * self.velocity).as_vector()

    def do_your_thing(self) -> None:
        self._apply_movement()
        self._apply_gravity()
        self._handle_current_damage()
        self._attack_player()
        self._generate_particles()
        self._cycle_opacity()
        self._cycle_color()

        if self.health is not None and self.health <= 0:
            # die :(
            self.die()

    def _attack_player(self) -> None:
        if self._projectile_generator and 0.5 - self._aggressivity < random_offset():
            self._projectile_generator(self._engine, self)

    def _handle_current_damage(self) -> None:
        _factor = self.get_health_ratio()
        _offset = 0.25

        # TODO: this is sus, do better
        if (1 - _offset) - _factor > (self._engine.scenario.now() * (self.radius / 20)) % 1:
            _fire_color = RGB(
                255 - random() * (40 * _factor),
                255 - random() * 220 * (1 - _factor),
                (1 - random()) * 20,
            ).get_gradient(
                RGB(
                    140,
                    140,
                    140,
                ),
                _factor + _offset / 2,
            )
            _explosion_size = (2.5 - random()) * ((math.log((1 + self.volume / 1500), 2)) + 0.5)
            _fire = CircularParticle(
                origin=self.center + VectorF.random_offset_vector(self.radius * 1.8),
                initial_velocity=self.velocity,
                size=_explosion_size,
                size_change_type=TransitionType.EXPONENTIAL_DECREASE,
                initial_color=_fire_color,
                ending_color=RGB(30, 30, 30),  # smokelike
                life_time=15,
                gravity=-0.07,
                particle_generator=get_smoke_generator(
                    floating_multi=0.2,
                    gravity=-0.04,
                    life_time=30,
                    initial_velocity=VectorF(random_offset() * 0.15, 0),
                    size_factor=0.8,
                ),
                engine=self._engine,
            )
            self._engine.scenario.fg_shapes.append(_fire)
