import math
from random import random
from typing import TYPE_CHECKING

from model.base import PointF, VectorF
from model.theme import RGB, Theme
from physics2d.entities.base import PhysicsEntity
from physics2d.shape.base import Shape
from physics2d.shape.factories.explosion import enemy_explosion, get_smoke_generator
from physics2d.shape.model.shared import TransitionType
from physics2d.shape.particle.circular_particle import CircularParticle
from utils import random_offset

if TYPE_CHECKING:
    from physics2d.physics2d import Physics2D


class Enemy(PhysicsEntity):
    # TODO: make a physics entity prop
    engine: "Physics2D"
    health: float

    _initial_health: float
    _initial_theme: Theme

    def __init__(
        self,
        engine: "Physics2D",
        size: float,
        health: float,
        density: float = 1,
        name: str = "Enemy",
        position: PointF = PointF(0, 0),
        # velocity: VectorF = VectorF(0, 0),
        theme: Theme = Theme(),
        angle: float = 0,
        affected_by_gravity: bool = False,
        initial_velocity: VectorF = VectorF(0, 0),
        initial_angular_velocity: float = 0,
        own_gravity: float | None = None,
        secondary_theme: Theme | None = None,
        floating_multi: float = 0,
        extra_shapes: list[Shape] = [],
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
        )
        self.engine = engine
        self.health = health
        self._initial_health = health
        self._initial_theme = Theme(color=theme.color)
        self.name = name
        self.extra_shapes = extra_shapes

    def receive_damage(self, amount: float) -> None:
        self.health -= amount

        if not self._initial_theme.color:
            return

        # _blinking_freq = 5
        _damage_color = (
            RGB(80, 0, 0, 1)
            # if math.floor(self.engine.scenario.now() / _blinking_freq) % 2 == 0
            # else RGB(180, 100, 100, 1)
        )

        _factor = self.get_health_ratio()
        _new_color = self._initial_theme.color.with_intensity(_factor) + (
            self.secondary_theme.color
            if self.secondary_theme and self.secondary_theme.color
            else _damage_color
        ).with_intensity(1 - _factor)

        self.theme.color = _new_color

    def get_health_ratio(self) -> float:
        return self.health / self._initial_health

    def die(self, engine, _death_explosion_size: int | None = None) -> None:
        enemy_explosion(engine.scenario, self, _death_explosion_size or self.radius * 2)
        engine.scenario.enemies = [e for e in engine.scenario.enemies if e is not self]

    def do_your_thing(self, engine: "Physics2D") -> None:
        super().do_your_thing(engine)

        self._handle_current_damage()

        for projectile in engine.scenario.projectiles:
            # we don't differentiate between friend or
            if self.would_collide_with(projectile, engine):
                self.receive_damage(projectile.damage)
                projectile.hit(engine)

        if self.health <= 0:
            # die :(
            self.die(engine)

    def _handle_current_damage(self) -> None:
        _factor = self.get_health_ratio()
        _offset = 0.25

        # TODO: this is sus, do better
        if (1 - _offset) - _factor > (self.engine.scenario.now() * (self.radius / 20)) % 1:
            _fire_color = RGB(
                255 - random() * 110,
                255 - random() * 110,
                (1 - random()) * 20,
            ).with_intensity(1 - _factor - _offset / 2) + RGB(
                140,
                140,
                140,
            ).with_intensity(_factor + _offset / 2)

            _explosion_size = (2.5 - random()) * ((math.log((1 + self.volume / 1500), 2)) + 0.5)
            _fire = CircularParticle(
                origin=self.center + VectorF.random_offset_vector(self.radius * 1.8),
                initial_velocity=self.velocity,
                size=_explosion_size,
                size_change_type=TransitionType.EXPONENTIAL_DECREASE,
                initial_color=_fire_color,
                ending_color=RGB(30, 30, 30, intensity=1),  # smokelike
                life_time=15,
                gravity=-0.07,
                particle_generator=get_smoke_generator(
                    floating_multi=0.2,
                    gravity=-0.04,
                    life_time=20,
                    initial_velocity=VectorF(random_offset() * 0.25, 0),
                ),
            )
            self.engine.scenario.fg_shapes.append(_fire)
