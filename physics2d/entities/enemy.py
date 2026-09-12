from model.base import PointF, VectorF
from model.theme import RGB, Theme
from physics2d.entities.base import PhysicsEntity
from physics2d.shapes.factories.explosion import explosion
from physics2d.shapes.shape import Shape


class Enemy(PhysicsEntity):
    extra_shapes: list[Shape]
    health: float
    _initial_health: float

    def __init__(
        self,
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
        )
        self.extra_shapes = []
        self.health = health
        self._initial_health = health
        self.name = name

    def receive_damage(self, amount: float) -> None:
        self.health -= amount

        if not self.theme.color:
            return

        _factor = self.health / self._initial_health
        _new_color = self.theme.color.with_intensity(_factor) + (
            self.secondary_theme.color
            if self.secondary_theme and self.secondary_theme.color
            else RGB(112, 77, 16, 1)  # horrible brown
        )
        self.theme.color = _new_color

    def _die(self, engine, _death_explosion_size: int | None = None) -> None:
        explosion(engine.scenario, self, _death_explosion_size or self.radius * 2)

    # TODO: type this shit
    def do_your_thing(self, engine) -> None:
        super().do_your_thing(engine)

        for projectile in engine.scenario.projectiles:
            # we don't differentiate between friend or
            if self.would_collide_with(projectile, engine):
                self.receive_damage(projectile.damage)
                projectile.hit(engine)

        if self.health <= 0:
            # die :(
            self._die(engine)
            engine.scenario.enemies = [e for e in engine.scenario.enemies if e is not self]
