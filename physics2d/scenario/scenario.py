from dataclasses import dataclass
from typing import TYPE_CHECKING, Literal

from physics2d.constants import DEFAULT_GRAVITY_ACCELERATION
from physics2d.entities.crosshair import Crosshair
from physics2d.entities.enemy import Enemy
from physics2d.entities.equipment.projectile import Projectile
from physics2d.entities.player_blob import PlayerBlob
from physics2d.entities.three_dee_enemy import ThreeDeeEnemy
from physics2d.model.shared import RenderInfo
from physics2d.shape.base import Shape
from physics2d.shape.particle.base import Particle

if TYPE_CHECKING:
    from physics2d.entities.base import PhysicsEntity
    from physics2d.entities.equipment.projectile import Projectile
    from physics2d.physics2d import Physics2D


# TODO: use this for "pieces"
# pieces in same layer collide with each other
@dataclass
class PieceHierarchy:
    layer_index: int
    pieces: list[Shape]


@dataclass
class GetEnemiesInRangeRes:
    enemy: Enemy
    distance: float


type Layer = Literal["fg", "bg", "solid"]


class Scenario:
    name: str

    fg_shapes: list[Shape]
    bg_shapes: list[Shape]
    solid_shapes: list[Shape]

    # TODO: project them in the screen! abstract the projecting logic into a function in utils and use it both in 3d renderer and here
    three_dee_enemies: list[ThreeDeeEnemy]

    projectiles: list[Projectile]

    # TODO: add _debug_pieces, for angle lines, etc

    enemies: list[Enemy]
    gravity_acceleration: float
    player: PlayerBlob
    crosshair: Crosshair

    # Global scenario counter
    _game_tick: int

    def __init__(
        self,
        name: str,
        enemies: list[Enemy],
        engine: "Physics2D",
        player: PlayerBlob,
        fg_shapes: list[Shape] = [],
        bg_shapes: list[Shape] = [],
        solid_shapes: list[Shape] = [],
        three_dee_enemies: list[ThreeDeeEnemy] = [],
    ):
        self.name = name
        self.engine = engine
        self.enemies = enemies
        self.fg_shapes = fg_shapes
        self.bg_shapes = bg_shapes
        self.solid_shapes = solid_shapes
        self.three_dee_enemies = three_dee_enemies

        for p in self.solid_shapes:
            p.is_collideable = True

        self.gravity_acceleration = DEFAULT_GRAVITY_ACCELERATION
        self.player = player
        self._game_tick = 0

        self.crosshair = Crosshair(engine)

        self.projectiles = []

    def act(self) -> None:
        self.player.do_your_thing()
        self.crosshair.do_your_thing()

        for entity in (
            self.fg_shapes
            + self.bg_shapes
            + self.solid_shapes
            + self.projectiles
            + self.enemies
            + self.three_dee_enemies
        ):
            entity.do_your_thing()

        self._particle_lifetime_cleanup()
        self._game_tick += 1

    def _particle_lifetime_cleanup(self) -> None:
        def _remove_dead_particles(arr: list[Shape]) -> list[Shape] | None:
            filtered = [
                p
                for p in arr
                if not isinstance(p, Particle) or p.life_time is None or p.life_time > 0
            ]

            if len(filtered) < len(arr):
                arr[:] = filtered

        _remove_dead_particles(self.bg_shapes)
        _remove_dead_particles(self.fg_shapes)
        _remove_dead_particles(self.solid_shapes)

        for p in self.projectiles:
            if p.life_time is not None and p.life_time <= 0:
                p.hit()
                if p in self.projectiles:
                    self.projectiles.remove(p)

    def now(self) -> int:
        """Get the current game tick"""
        return self._game_tick

    def render(self) -> None:
        self._render_crosshair()

        # TODO: unify, we need a common class
        def _handle(pieces: list[Shape] | list[Projectile] | list[Enemy] | list[ThreeDeeEnemy]):
            for p in pieces:
                self.handle_render_info(p.get_render_info())

        # Foreground gets differentiated treatment
        _handle_in_front_of_player: list[Shape] = []
        _render_behind_player: list[Shape] = []
        for shape in self.fg_shapes:
            if shape.render_behind_player:
                _render_behind_player.append(shape)
            else:
                _handle_in_front_of_player.append(shape)

        _handle(_render_behind_player)
        self.handle_render_info(self.player.get_render_info())
        _handle(_handle_in_front_of_player)

        _handle(self.solid_shapes)
        _handle(self.projectiles)
        _handle(self.enemies)
        _handle(self.three_dee_enemies)

        # TODO: do something
        for e in self.enemies:
            _ = e.get_render_info()

        _handle(self.bg_shapes)

    def handle_render_info(self, render_info: list[RenderInfo]) -> None:
        for info in render_info:
            self.engine.add_pixel_info_to_buffer(info)

    def _render_crosshair(self) -> None:
        for info in self.crosshair.get_render_info():
            self.engine.add_pixel_info_to_buffer(info, absolute_positioning=True)

    def get_enemies_in_range(
        self,
        max_range: float,
        subject: "PhysicsEntity | None" = None,
        calc_distance_to_border: bool = False,
    ) -> list[GetEnemiesInRangeRes]:
        possible_victims = [
            GetEnemiesInRangeRes(enemy, distance)
            # TODO: do we need it sorted?
            for enemy, distance in sorted(
                [
                    (
                        e,
                        abs((subject.center if subject else self.player.center) - (e.center))
                        - (e.radius if calc_distance_to_border else 0),
                    )
                    for e in self.enemies
                ],
                key=lambda v: v[1],
            )
            if distance < max_range
            # / 2  # TODO: this /2 is a hack, investigate why radius is treated as diameter¿?¿?¿?¿?
        ]
        return possible_victims
