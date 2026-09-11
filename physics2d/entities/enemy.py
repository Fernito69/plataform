from model.base import PointF, VectorF
from model.theme import Theme
from physics2d.entities.base import PhysicsEntity
from physics2d.shapes.shape import Shape


class Enemy(PhysicsEntity):
    extra_shapes: list[Shape]
    health: int

    def __init__(
        self,
        size: float,
        health: int,
        density: float = 1,
        name: str = "PhysicsEntity",
        position: PointF = PointF(0, 0),
        velocity: VectorF = VectorF(0, 0),
        theme: Theme = Theme(),
        angle: float = 0,
        affected_by_gravity: bool = False,
        initial_velocity: VectorF = VectorF(0, 0),
        initial_angular_velocity: float = 0,
        own_gravity: float | None = None,
        secondary_theme: Theme | None = None,
        floating_multi: float = 0,
    ):
        super().__init__(
            density=density,
            floating_multi=floating_multi,
            size=size,
            name=name,
            position=position,
            velocity=velocity,
            theme=theme,
            angle=angle,
            affected_by_gravity=affected_by_gravity,
            initial_angular_velocity=initial_angular_velocity,
            initial_velocity=initial_velocity,
            own_gravity=own_gravity,
            secondary_theme=secondary_theme,
            is_collideable=True,
        )
        self.extra_shapes = []
        self.health = health
