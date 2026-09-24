from typing import TYPE_CHECKING

from model.base import PointF, VectorF
from model.theme import RGB, Theme
from physics2d.entities.base import PhysicsEntity
from physics2d.entities.enemy import Enemy
from physics2d.entities.model.shared import ParticleGenerator
from physics2d.entities.model.spawner import Spawn
from physics2d.shape.factories.explosion import rocket_explosion

if TYPE_CHECKING:
    from physics2d.physics2d import Physics2D


class Spawner(PhysicsEntity):
    _enemy_spawn: Spawn[Enemy] | None
    # TODO: coming soon!
    _item_spawn: Spawn | None

    _life_time: int

    def __init__(
        self,
        size: float,
        engine: "Physics2D",
        enemy_spawn: Spawn[Enemy],
        spawn_interval: int,
        total_num_spawns: int | None = None,
        name: str = "Spawner",
        position: PointF = PointF(0, 0),
        theme: Theme = Theme(),
        affected_by_gravity: bool = False,
        initial_velocity: VectorF = VectorF(0, 0),
        initial_angular_velocity: float = 0,
        own_gravity: float | None = None,
        secondary_theme: Theme | None = None,
        floating_multi: float = 0,
        extra_shapes: list[PhysicsEntity] = [],
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
        )
        self._life_time = 0
        self._enemy_spawn = enemy_spawn
        self._total_num_spawns = total_num_spawns
        self._spawn_interval = spawn_interval

    def do_your_thing(self) -> None:
        es = self._enemy_spawn

        if es:
            if self._life_time % es.spawn_interval == 0 and (
                not es.total_num_spawns
                or (es.total_num_spawns and es.curr_num_spawns < es.total_num_spawns)
            ):
                self._spawn_effect()
                es.curr_num_spawns += 1
                es.entity_factory(self._engine, self)
            elif es.total_num_spawns and es.curr_num_spawns >= es.total_num_spawns:
                self._die()

        # TODO: do items

        self._life_time += 1

    def _die(self) -> None:
        self._spawn_effect()
        # For now we assume it's always in solid_shapes
        self._engine.scenario.solid_shapes.remove(self)

    def _spawn_effect(self) -> None:
        _size = 25

        _COLOR = RGB(127, 255, 127, 1)
        _COLOR_2 = RGB(180, 255, 90, 1)
        _COLOR_3 = RGB(200, 255, 60, 1)
        _mini_effect_color = RGB(220, 255, 127, 1)

        # TODO: it needs its own effect
        rocket_explosion(
            engine=self._engine,
            # TOOD: fix
            rocket=self,
            damage=100,
            blast_radius=_size,
            blast_damage_at_ground_zero=0,
            main_color=_COLOR,
            secondary_color=_COLOR_2,
            tertiary_color=_COLOR_3,
            little_explosions_color=_mini_effect_color,
            with_smoke=False,
            throw_sparks=True,
            bfg_sparks=True,
        )
