from typing import TYPE_CHECKING

from model.base import PointF, VectorF
from model.theme import RGB, Theme
from physics2d.entities.base import PhysicsEntity
from physics2d.entities.model.shared import ParticleGenerator
from physics2d.entities.model.spawner import Spawner
from physics2d.shape.model.shared import TransitionType
from physics2d.shape.particle.circular_particle import CircularParticle
from utils import random_offset

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

    _spawn_effect_size: float

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
        spawn_effect_size: float = 10,
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
        self._spawn_effect_size = spawn_effect_size

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
        # For now we assume it's always in bg_shapes
        self._engine.scenario.bg_shapes.remove(self)

    def _spawn_effect(self) -> None:
        teleport_in_particles(
            self._engine,
            self,
            self._spawn_effect_size,
        )

    def _die_effect(self) -> None:
        # TODO: do its own thing
        self._spawn_effect()


#####################################################################################################################################


def teleport_in_particles(
    engine: "Physics2D",
    source: "PhysicsEntity",
    size: float = 10,
) -> None:
    pieces: list[Shape] = []

    _initial_color = RGB(80, 255, 80)

    shockwave = CircularParticle(
        engine=engine,
        origin=source.center,
        size=size,
        size_change_type=TransitionType.EXPONENTIAL_DECREASE,
        initial_color=_initial_color,
        ending_color=_initial_color.copy(opacity=0),
        ending_color_fade_type=TransitionType.LINEAR_DECREASE,
        life_time=15,
    )
    pieces.append(shockwave)

    shockwave = CircularParticle(
        engine=engine,
        origin=source.center,
        size=0,
        final_radius=size,
        size_change_type=TransitionType.LINEAR_INCREASE,
        initial_color=RGB(255, 255, 255),
        ending_color=RGB(255, 255, 255, opacity=0),
        ending_color_fade_type=TransitionType.LINEAR_DECREASE,
        life_time=15,
    )
    pieces.append(shockwave)

    for _ in range(15):
        # little particles doing particle stuff
        sonic_challa = CircularParticle(
            origin=(source.center - source.velocity)
            - VectorF(x=random_offset(), y=random_offset()),
            initial_velocity=(
                -0.4
                * VectorF(
                    x=source.velocity.x + random_offset(), y=source.velocity.y + random_offset()
                )
            ).as_vector(),
            size=4,
            size_change_type=TransitionType.EXPONENTIAL_DECREASE,
            initial_color=_initial_color,
            ending_color=_initial_color.copy(opacity=0),
            ending_color_fade_type=TransitionType.LINEAR_DECREASE,
            life_time=25,
            floating_multi=5,
            engine=engine,
        )
        pieces.append(sonic_challa)

    engine.scenario.bg_shapes[0:0] = pieces
