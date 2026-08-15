from factories.theme import DoubleLines
from model.shared import Vector3
from three_d_renderer.entities.base3d import Entity3D

_DEFAULT_LINE_TYPE = DoubleLines


class Level3D:
    # TODO: refactor the shit out of this
    entities: list[Entity3D]

    def __init__(
        self,
        entities: list[Entity3D],
        # player_starting_position: Coord3 = (0, 0, 0),
        player_starting_position: Vector3 = [0, 0, 0],
    ):
        self.entities = entities
        self.player_starting_position = player_starting_position
