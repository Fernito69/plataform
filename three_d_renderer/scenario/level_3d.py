from model.base import VectorF
from three_d_renderer.entities.base3d import Entity3D


# TODO: refactor the shit out of this
class Level3D:
    entities: list[Entity3D]
    rotation: bool

    def __init__(
        self,
        entities: list[Entity3D],
        player_starting_position: VectorF = VectorF(0, 0, 0),
    ):
        self.entities = entities
        self.player_starting_position = player_starting_position
        self.rotation = any(e.rotate for e in entities)

    def toggle_rotation(self) -> None:
        self.rotation = not self.rotation
        for e in self.entities:
            e.rotate = self.rotation
