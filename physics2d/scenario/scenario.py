from physics2d.entities.base import Entity
from physics2d.scenario.piece import ScenarioPiece


class Scenario:
    pieces: ScenarioPiece
    entities: list[Entity]

    def __init__(self, entities: list[Entity], pieces: ScenarioPiece):
        self.entities = entities
        self.pieces = pieces
