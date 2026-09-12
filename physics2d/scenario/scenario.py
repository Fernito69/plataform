from dataclasses import dataclass
from typing import TYPE_CHECKING

from physics2d.constants import DEFAULT_GRAVITY_ACCELERATION
from physics2d.entities.enemy import Enemy
from physics2d.entities.equipment.projectile import Projectile
from physics2d.entities.player_blob import PlayerBlob
from physics2d.model.shared import RenderInfo
from physics2d.shapes.particle import Particle
from physics2d.shapes.shape import Shape

if TYPE_CHECKING:
    from physics2d.physics2d import Physics2D


# TODO: use this for "pieces"
# pieces in same layer collide with each other
@dataclass
class PieceHierarchy:
    layer_index: int
    pieces: list[Shape]


class Scenario:
    # TODO: refactor this
    fg_pieces: list[Shape]
    bg_pieces: list[Shape]
    solid_pieces: list[Shape]

    projectiles: list[Projectile]

    # TODO: add _debug_pieces, for angle lines, etc

    enemies: list[Enemy]
    gravity_acceleration: float
    player: PlayerBlob

    # Global scenario counter
    _game_tick: int

    def __init__(
        self,
        enemies: list[Enemy],
        engine: "Physics2D",
        player: PlayerBlob,
        fg_pieces: list[Shape] = [],
        bg_pieces: list[Shape] = [],
        solid_pieces: list[Shape] = [],
    ):
        self.enemies = enemies
        self.fg_pieces = fg_pieces
        self.bg_pieces = bg_pieces
        self.solid_pieces = solid_pieces
        for p in self.solid_pieces:
            p.is_collideable = True
        self.engine = engine

        self.gravity_acceleration = DEFAULT_GRAVITY_ACCELERATION
        self.player = player
        self._game_tick = 0

        self.projectiles = []

    def act(self) -> None:
        self.player.do_your_thing()

        for entity in (
            self.fg_pieces + self.bg_pieces + self.solid_pieces + self.projectiles + self.enemies
        ):
            entity.do_your_thing(self.engine)

        self._particle_lifetime_cleanup()
        self._game_tick += 1

    def _particle_lifetime_cleanup(self) -> None:
        # TODO: unify this
        filtered = [
            p
            for p in self.fg_pieces
            if not isinstance(p, Particle) or p.life_time is None or p.life_time > 0
        ]
        if len(filtered) < len(self.fg_pieces):
            self.fg_pieces = filtered

        filtered = [
            p
            for p in self.bg_pieces
            if not isinstance(p, Particle) or p.life_time is None or p.life_time > 0
        ]
        if len(filtered) < len(self.bg_pieces):
            self.bg_pieces = filtered

        filtered = [
            p
            for p in self.solid_pieces
            if not isinstance(p, Particle) or p.life_time is None or p.life_time > 0
        ]
        if len(filtered) < len(self.solid_pieces):
            self.solid_pieces = filtered

    def now(self) -> int:
        """Get the current game tick"""
        return self._game_tick

    def render(self) -> None:
        # TODO: unify, we need a common class
        def _handle(pieces: list[Shape] | list[Projectile] | list[Enemy]):
            for p in pieces:
                self.handle_render_info(p.get_render_info())

        # Foreground gets differentiated treatment
        _handle_in_front_of_player: list[Shape] = []
        _render_behind_player: list[Shape] = []
        for shape in self.fg_pieces:
            if shape.render_behind_player:
                _render_behind_player.append(shape)
            else:
                _handle_in_front_of_player.append(shape)

        _handle(_render_behind_player)
        self.handle_render_info(self.player.get_render_info())
        _handle(_handle_in_front_of_player)

        _handle(self.solid_pieces)
        _handle(self.projectiles)
        _handle(self.enemies)

        # TODO: do something
        for e in self.enemies:
            _ = e.get_render_info()

        _handle(self.bg_pieces)

    def handle_render_info(self, render_info: list[RenderInfo]) -> None:
        for info in render_info:
            self.engine.add_pixel_info_to_buffer(info)
