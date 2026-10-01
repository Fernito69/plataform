from typing import TYPE_CHECKING

from model.base import PointF, VectorF
from model.theme import RGB, Theme
from physics2d.entities.base import PhysicsEntity
from physics2d.entities.model.shared import ParticleGenerator
from physics2d.entities.model.spawner import Spawner

if TYPE_CHECKING:
    from physics2d.physics2d import Physics2D
    from physics2d.shape.base import Shape


# TODO: this should inherit from Enemy?
# TODO: implement pulsate method for circunference (like line) and make spawner entity pulsate!
class SpawnerEntity(PhysicsEntity):
    _spawner: Spawner
    _spawn_interval: int
    _total_num_spawns: int | None
    _initial_delay: int

    _curr_num_spawns: int = 0
    _life_time_elapsed: int = 0

    def __init__(
        self,
        engine: "Physics2D",
        spawner: Spawner,
        spawn_interval: int,
        position: PointF,
        initial_delay: int = 0,
        total_num_spawns: int | None = None,
        name: str = "SpawnerEntity",
        size: float = 5,
        theme: Theme = Theme(color=RGB(255, 0, 0)),
        secondary_theme: Theme = Theme(color=RGB(0, 200, 0)),
        color_gradient_exponent: float = 0,
        affected_by_gravity: bool = False,
        initial_velocity: VectorF = VectorF(0, 0),
        initial_angular_velocity: float = 0,
        own_gravity: float | None = None,
        floating_multi: float = 0,
        extra_shapes: list["PhysicsEntity | Shape"] = [],
        particle_generator: ParticleGenerator | None = None,
    ):
        super().__init__(
            density=1,
            size=size,
            engine=engine,
            name=name,
            position=position,
            theme=theme,
            angle=0,
            affected_by_gravity=affected_by_gravity,
            initial_velocity=initial_velocity,
            initial_angular_velocity=initial_angular_velocity,
            own_gravity=own_gravity,
            secondary_theme=secondary_theme,
            floating_multi=floating_multi,
            is_collideable=False,
            extra_shapes=extra_shapes,
            particle_generator=particle_generator,
            color_gradient_exponent=color_gradient_exponent,
        )
        self._total_num_spawns = total_num_spawns
        self._spawn_interval = spawn_interval
        self._spawner = spawner
        self._initial_delay = initial_delay

    def do_your_thing(self) -> None:
        elapsed = self._life_time_elapsed - self._initial_delay

        self._handle_color(elapsed)

        if (
            elapsed >= 0
            and elapsed % self._spawn_interval == 0
            and (
                not self._total_num_spawns
                or (self._total_num_spawns and self._curr_num_spawns < self._total_num_spawns)
            )
        ):
            self._spawner(self._engine, self)
            self._spawn_effect()
            self._curr_num_spawns += 1
        elif self._total_num_spawns and self._curr_num_spawns >= self._total_num_spawns:
            self._die()

        self._life_time_elapsed += 1

    def _handle_color(self, elapsed: int) -> None:
        _elapsed: float = (
            elapsed % self._spawn_interval
            if elapsed >= 0
            else (self._life_time_elapsed / self._initial_delay)
        )
        self._color_gradient_exponent = (_elapsed / (self._spawn_interval)) * 2

    def _die(self) -> None:
        self._die_effect()
        # For now we assume it's always in solid_shapes
        self._engine.scenario.solid_shapes.remove(self)

    def _spawn_effect(self) -> None:
        _size = 25

        _COLOR = RGB(127, 255, 127, 1)
        _COLOR_2 = RGB(180, 255, 90, 1)
        _COLOR_3 = RGB(200, 255, 60, 1)
        _mini_effect_color = RGB(220, 255, 127, 1)

        # TODO: it needs its own effect, this is not a rocket!
        # rocket_explosion(
        #     engine=self._engine,
        #     rocket=self,
        #     damage=100,
        #     blast_radius=_size,
        #     blast_damage_at_ground_zero=0,
        #     main_color=_COLOR,
        #     secondary_color=_COLOR_2,
        #     tertiary_color=_COLOR_3,
        #     little_explosions_color=_mini_effect_color,
        #     with_smoke=False,
        #     throw_sparks=True,
        #     bfg_sparks=True,
        # )

    def _die_effect(self) -> None:
        # TODO: do its own thing
        self._spawn_effect()
