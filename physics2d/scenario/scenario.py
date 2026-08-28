from dataclasses import dataclass
from typing import TYPE_CHECKING

from physics2d.constants import DEFAULT_GRAVITY_ACCELERATION
from physics2d.entities.base import Entity
from physics2d.model.base import RenderInfo
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
    pieces: list[ScenarioPiece]
    entities: list[Entity]
    gravity_acceleration: float

    def __init__(self, entities: list[Entity], pieces: list[ScenarioPiece], engine: "Physics2D"):
        self.entities = entities
        self.pieces = pieces
        self.engine = engine
        self.gravity_acceleration = DEFAULT_GRAVITY_ACCELERATION

    def act(self) -> None:
        for e in self.pieces:
            e.apply_movement()
            e.apply_gravity(self.gravity_acceleration)

    def render(self) -> None:
        for e in self.entities:
            _ = e.return_render_info()
            # TODO: do something

        for pieces in self.pieces:
            self.handle_render_info(pieces.return_render_info())

    def handle_render_info(self, render_info: list[RenderInfo]) -> None:
        for info in render_info:
            self.engine.add_pixel_info_to_buffer(info)
