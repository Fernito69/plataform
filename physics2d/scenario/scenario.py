from dataclasses import dataclass
from typing import TYPE_CHECKING

from physics2d.constants import DEFAULT_GRAVITY_ACCELERATION
from physics2d.entities.base import PhyEntity
from physics2d.entities.player_blob import PlayerBlob
from physics2d.model.shared import RenderInfo
from physics2d.scenario.piece import ScenarioPiece

if TYPE_CHECKING:
    from physics2d.physics2d import Physics2D


# TODO: use this for "pieces"
# pieces in same layer collide with each other
@dataclass
class PieceHierarchy:
    layer_index: int
    pieces: list[ScenarioPiece]


class Scenario:
    # TODO: refactor this
    fg_pieces: list[ScenarioPiece]
    bg_pieces: list[ScenarioPiece]
    solid_pieces: list[ScenarioPiece]

    entities: list[PhyEntity]
    gravity_acceleration: float
    player: PlayerBlob

    def __init__(
        self,
        entities: list[PhyEntity],
        engine: "Physics2D",
        player: PlayerBlob,
        fg_pieces: list[ScenarioPiece] = [],
        bg_pieces: list[ScenarioPiece] = [],
        solid_pieces: list[ScenarioPiece] = [],
    ):
        self.entities = entities
        self.fg_pieces = fg_pieces
        self.bg_pieces = bg_pieces
        self.solid_pieces = solid_pieces
        self.engine = engine
        self.gravity_acceleration = DEFAULT_GRAVITY_ACCELERATION
        self.player = player

    def act(self) -> None:
        self.player.do_your_thing(self.gravity_acceleration)

        for piece in self.fg_pieces + self.bg_pieces + self.solid_pieces:
            piece.do_your_thing(self.gravity_acceleration)

    def render(self) -> None:
        # TODO: unify
        def _handle_pieces(pieces: list[ScenarioPiece]):
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
