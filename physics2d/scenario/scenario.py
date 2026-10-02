from dataclasses import dataclass
from typing import TYPE_CHECKING, Literal

from model.base import PointF
from physics2d.constants import DEFAULT_GRAVITY_ACCELERATION
from physics2d.entities.crosshair import Crosshair
from physics2d.entities.enemy import Enemy
from physics2d.entities.equipment.projectile import Projectile
from physics2d.entities.model.shared import BackgroundGenerator
from physics2d.entities.player_blob import PlayerBlob
from physics2d.entities.three_dee_enemy import ThreeDeeEnemy
from physics2d.model.shared import RenderInfo
from physics2d.scenario.background import Background
from physics2d.shape.base import Shape
from physics2d.shape.particle.base import Particle
from utils import random_offset

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


@dataclass
class GetProjectilesInRangeRes:
    projectile: Projectile
    distance: float


type Layer = Literal["fg", "bg", "solid"]


class Scenario:
    name: str

    background: Background

    fg_shapes: list[Shape]
    bg_shapes: list[Shape]
    solid_shapes: list[Shape]
    # absolutely positioned:
    overlay_shapes: list[Shape]

    projectiles: list[Projectile]
    enemy_projectiles: list[Projectile]

    # TODO: add _debug_pieces, for angle lines, etc

    player: PlayerBlob
    crosshair: Crosshair

    enemies: list[Enemy]
    three_dee_enemies: list[ThreeDeeEnemy]

    gravity_acceleration: float

    # Global scenario counter
    _game_tick: int

    def __init__(
        self,
        name: str,
        background_gen: BackgroundGenerator,
        enemies: list[Enemy],
        engine: "Physics2D",
        player: PlayerBlob,
        player_initial_position: PointF,
        fg_shapes: list[Shape] = [],
        bg_shapes: list[Shape] = [],
        solid_shapes: list[Shape] = [],
        overlay_shapes: list[Shape] = [],
        three_dee_enemies: list[ThreeDeeEnemy] = [],
    ):
        self.name = name
        self.engine = engine
        self.enemies = enemies
        self.fg_shapes = fg_shapes
        self.bg_shapes = bg_shapes
        self.solid_shapes = solid_shapes
        self.three_dee_enemies = three_dee_enemies
        self.overlay_shapes = overlay_shapes

        for p in self.solid_shapes:
            p.is_collideable = True

        self.gravity_acceleration = DEFAULT_GRAVITY_ACCELERATION

        self._init_player(player, player_initial_position)

        self.crosshair = Crosshair(engine)

        self.projectiles = []
        self.enemy_projectiles = []

        self.background = background_gen(engine)

    def do_your_thing(self) -> None:
        self.player.do_your_thing()
        self.crosshair.do_your_thing()

        for entity in (
            self.fg_shapes
            + self.bg_shapes
            + self.solid_shapes
            + self.overlay_shapes
            + self.projectiles
            + self.enemy_projectiles
            + self.enemies
            + self.three_dee_enemies
        ):
            entity.do_your_thing()

        self._particle_lifetime_cleanup()
        self._game_tick += 1

    def _init_player(
        self,
        player: PlayerBlob,
        player_initial_position: PointF,
    ) -> None:
        self.player = player
        _delta = (player_initial_position - self.player.position).as_vector()
        self.player._move_by(_delta)
        self.engine.screen_corner += _delta
        self._game_tick = 0

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
        _remove_dead_particles(self.overlay_shapes)

        for p in self.projectiles + self.enemy_projectiles:
            if p.life_time is not None and p.life_time <= 0:
                p.hit()

    def now(self) -> int:
        """Get the current game tick"""
        return self._game_tick

    def compute_render_info(self) -> None:
        # The background slides its own shapes around for parallax. Doing that
        # here, before anything is drawn, keeps drawing a pure read so its
        # shapes can go through stage A with everything else.
        self.background.update()

        jobs = self._get_render_jobs()

        # Stage A: resolve every entity's pixels. Each entity only looks at
        # itself, so this is the part that can be spread over several threads.
        all_render_info = self.engine.compute_render_info_batch([entity for entity, _ in jobs])

        # Stage B: scatter them into the buffer, strictly in job order. The
        # buffer stacks pixels front-to-back per cell and _compute_subpixel_color
        # walks them in that order, so this half has to stay serial.
        for (_, absolute_positioning), render_info in zip(jobs, all_render_info):
            self.handle_render_info(render_info, absolute_positioning)

    # TODO: unify, we need a common class
    def _get_render_jobs(
        self,
    ) -> list[tuple[Shape | Projectile | Enemy | ThreeDeeEnemy, bool]]:
        """What to render this frame, paired with its positioning, in draw order.

        Anything the camera can't see is dropped here, so it never reaches the
        pool in stage A.
        """

        # Foreground gets differentiated treatment. TODO: this is a hack. Do properly
        _render_in_front_of_player: list[Shape] = []
        _render_behind_player: list[Shape] = []

        for shape in self.fg_shapes:
            if shape.render_behind_player:
                _render_behind_player.append(shape)
            else:
                _render_in_front_of_player.append(shape)

        absolutely_positioned = [self.crosshair, *self.overlay_shapes]
        relatively_positioned = [
            *_render_behind_player,
            self.player,
            *_render_in_front_of_player,
            *self.solid_shapes,
            *self.projectiles,
            *self.enemy_projectiles,
            *self.enemies,
            *self.three_dee_enemies,
            *self.bg_shapes,
        ]

        # Two rectangles: world-positioned things are tested against the camera
        # viewport, screen-positioned ones against the screen itself.
        viewport = self.engine.get_viewport()
        screen = self.engine.get_screen_rect()

        return [
            *[(entity, True) for entity in absolutely_positioned],
            *[
                (entity, False)
                for entity in relatively_positioned
                if self.engine.is_worth_rendering(entity, viewport)
            ],
            # Last, so it ends up behind everything else.
            *[
                (shape, True)
                for shape in self.background.get_shapes()
                if self.engine.is_worth_rendering(shape, screen)
            ],
        ]

    def handle_render_info(
        self,
        render_info: list[RenderInfo],
        absolute_positioning=False,
    ) -> None:
        for info in render_info:
            self.engine.add_pixel_info_to_buffer(info, absolute_positioning)

    def get_distance_to_player(
        self,
        subject: "PhysicsEntity",
        calc_distance_to_border: bool = True,
    ) -> float:
        return abs(self.player.position - subject.position) - (
            self.player.radius + subject.radius if calc_distance_to_border else 0
        )

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
        ]
        return possible_victims

    def get_projectiles_in_range(
        self,
        max_range: float,
        subject: "PhysicsEntity",
        calc_distance_to_border: bool = False,
        size_above: float = 0,
    ) -> list[GetProjectilesInRangeRes]:
        subject_is_enemy = isinstance(subject, Enemy) or (
            isinstance(subject, Projectile) and subject.is_enemy
        )
        center = subject.center if subject else self.player.center
        possible_victims = [
            GetProjectilesInRangeRes(proj, distance)
            # TODO: do we need it sorted?
            for proj, distance in sorted(
                [
                    (
                        e,
                        abs((center) - (e.center)) - (e.radius if calc_distance_to_border else 0),
                    )
                    for e in (self.projectiles if subject_is_enemy else self.enemy_projectiles)
                ],
                key=lambda v: (-v[0].size, v[1]),
            )
            if distance < max_range and proj is not subject and proj.size > size_above
        ]
        return possible_victims

    def add_to_fg_or_bg_randomly(self, entity: "PhysicsEntity") -> None:
        if random_offset() > 0:
            self.fg_shapes.append(entity)
        else:
            self.bg_shapes.append(entity)
