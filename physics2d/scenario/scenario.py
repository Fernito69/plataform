from dataclasses import dataclass
from typing import TYPE_CHECKING

from physics2d.constants import DEFAULT_GRAVITY_ACCELERATION
from physics2d.entities.base import PhyEntity
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

    # TODO: add _debug_pieces, for angle lines, etc

    entities: list[PhyEntity]
    gravity_acceleration: float
    player: PlayerBlob

    # Global scenario counter
    _game_tick: int

    def __init__(
        self,
        entities: list[PhyEntity],
        engine: "Physics2D",
        player: PlayerBlob,
        fg_pieces: list[Shape] = [],
        bg_pieces: list[Shape] = [],
        solid_pieces: list[Shape] = [],
    ):
        self.entities = entities
        self.fg_pieces = fg_pieces
        self.bg_pieces = bg_pieces
        self.solid_pieces = solid_pieces
        for p in self.solid_pieces:
            p.is_collideable = True
        self.engine = engine
        self.gravity_acceleration = DEFAULT_GRAVITY_ACCELERATION
        self.player = player
        self._game_tick = 0

    def act(self) -> None:
        self.player.do_your_thing()

        for piece in self.fg_pieces + self.bg_pieces + self.solid_pieces:
            piece.do_your_thing(self.engine)

        self._lifetime_cleanup()
        self._game_tick += 1

    def _lifetime_cleanup(self) -> None:
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
        # TODO: unify
        def _handle_pieces(pieces: list[Shape]):
            for p in pieces:
                self.handle_render_info(p.get_render_info())

        _handle_pieces(self.fg_pieces)

        self.handle_render_info(self.player.get_render_info())
        _handle_pieces(self.solid_pieces)

        # TODO: do something
        for e in self.entities:
            _ = e.get_render_info()

        _handle_pieces(self.bg_pieces)

    def handle_render_info(self, render_info: list[RenderInfo]) -> None:
        for info in render_info:
            self.engine.add_pixel_info_to_buffer(info)
