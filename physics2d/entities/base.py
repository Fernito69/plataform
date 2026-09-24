from abc import abstractmethod
from typing import TYPE_CHECKING

from model.base import PointF, VectorF
from model.theme import Theme
from physics2d.constants import DEFAULT_GRAVITY_ACCELERATION
from physics2d.entities.model.shared import ParticleGenerator
from physics2d.model.shared import RenderInfo
from physics2d.shape.base import Shape
from physics2d.shape.circunference import Circunference

if TYPE_CHECKING:
    from physics2d.entities.enemy import Enemy
    from physics2d.physics2d import Physics2D


class PhysicsEntity(Circunference):
    position: PointF
    velocity: VectorF
    extra_shapes: list["PhysicsEntity | Enemy"]

    name: str | None

    _particle_generator: ParticleGenerator | None

    def __init__(
        self,
        density: float,
        size: float,
        engine: "Physics2D",
        name: str = "PhysicsEntity",
        position: PointF = PointF(0, 0),
        theme: Theme = Theme(),
        angle: float = 0,
        affected_by_gravity: bool = False,
        initial_velocity: VectorF = VectorF(0, 0),
        initial_angular_velocity: float = 0,
        own_gravity: float | None = None,
        secondary_theme: Theme | None = None,
        floating_multi: float = 0,
        is_collideable: bool = True,
        extra_shapes: list["PhysicsEntity"] = [],
        particle_generator: ParticleGenerator | None = None,
    ):
        super().__init__(
            center=position,
            radius=size / 2,
            density=density,
            theme=theme,
            angle=angle,
            secondary_theme=secondary_theme,
            own_gravity=own_gravity,
            initial_angular_velocity=initial_angular_velocity,
            affected_by_gravity=affected_by_gravity,
            floating_multi=floating_multi,
            initial_velocity=initial_velocity,
            is_collideable=is_collideable,
            engine=engine,
        )
        self._engine = engine
        self.position = position
        self.extra_shapes = extra_shapes

        self.density = density
        self.name = name
        self.size = size
        self._particle_generator = particle_generator

        # volume depends on the type of entity

    def get_render_info(self) -> list[RenderInfo]:
        info = super().get_render_info()
        for shape in self.extra_shapes:
            info.extend(shape.get_render_info())
        return info

    def _apply_movement(self) -> None:
        self._generate_particles()
        super()._apply_movement()

    def _apply_gravity(self, gravity_accel: float = DEFAULT_GRAVITY_ACCELERATION) -> None:
        if not self._affected_by_gravity and not self._own_gravity_accel:
            return

        for shape in self.extra_shapes:
            shape._apply_gravity(self._own_gravity_accel or gravity_accel)

        return super()._apply_gravity(self._own_gravity_accel or gravity_accel)

    def _generate_particles(self) -> None:
        if self._particle_generator:
            self._particle_generator(self._engine, self)

    def is_same_position(self, shape: "Shape") -> bool:
        # TODO implement
        raise

    def _move_by(self, vector: VectorF) -> None:
        self.center += vector
        self.position += vector

    @abstractmethod
    def get_aiming_direction(self) -> VectorF: ...
