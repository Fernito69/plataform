from model.base import Vector3
from three_d_renderer.entities.base3d import Entity3D


# TODO: refactor the shit out of this
class Level3D:
    entities: list[Entity3D]

    def __init__(
        self,
        entities: list[Entity3D],
        # player_starting_position: Coord3 = (0, 0, 0),
        player_starting_position: Vector3 = [0, 0, 0],
    ):
        self.entities = entities
        self.player_starting_position = player_starting_position
