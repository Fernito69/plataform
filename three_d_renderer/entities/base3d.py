import math
from abc import abstractmethod
from typing import TYPE_CHECKING, Optional

from factories.theme import White
from model.base import Point3, Vector3
from model.theme import EMPTY_SPACE, RGB, Theme
from utils import add_triplet, colored

if TYPE_CHECKING:
    from three_d_renderer.scenario.level_3d import Level3D

# TODO: move


# TODO: rename methods properly
# TODO: reuse the Theme types as animation types for _char frames and reuse the method to make level architecture for the change of  indices


class Entity3D:
    # _curr_level: Optional["Level3D"] = None
    position: Point3 = [0, 0, 0]
    falling_velocity: float = 0
    # TODO: rotation_matrix missing?
    # TODO: should be objVertexes: list[tuple[Point3, Point3]]
    vertices: list[Point3]
    movMatrix: Point3
    rotMatrix: Point3
    rotate: bool

    # How vertices in the entity interconnect between them
    # works by index, e.g.: (0, 1) <- vertex 0 connects with 1
    vertex_connections: list[tuple[int, int]]

    theme: Theme

    name: str | None

    def __init__(
        self,
        vertices: list[Point3],
        level: Optional["Level3D"] = None,
        theme: Theme | None = None,
        position: Point3 = [0, 0, 0],
        size: float = 1,
        angle: Point3 = [0, 0, 0],
        movMatrix: Point3 = [0, 0, 0],
        rotMatrix: Point3 = [0, 0, 0],
        color: RGB = White(),
        name: str | None = None,
    ):
        # x and y coordinates
        # TODO: should we keep previous state to calculate instant velocity?
        self._curr_level = level
        self._char_frames = [EMPTY_SPACE]
        self._default_char_frames = [EMPTY_SPACE]
        self._curr_char_frame_index = 0
        self.position = position
        self.size = size
        self.angle = angle
        self.movMatrix = movMatrix
        self.rotMatrix = rotMatrix
        self.vertices = vertices
        self.name = name
        self.rotate = rotMatrix is not None

        # For now only color
        # self.theme = theme or Theme()
        self.theme = Theme(color=color)

    def is_lazy(self) -> bool:
        # TODO: we are bypassing this, check why the optimization is not working
        return False and self.movMatrix == [0, 0, 0] and self.rotMatrix == [0, 0, 0]

    @abstractmethod
    def get_diameter(cls) -> float:
        pass

    @abstractmethod
    def calc_main_vertexes(self, apply: bool = False) -> list[Point3]:
        pass

    @abstractmethod
    def calc_legacy_voxels(self, apply: bool = False) -> list[Point3]:
        pass

    def _apply_gravity(self) -> None:
        raise NotImplementedError("No gravity support yet")

    def get_char(self) -> str:
        return colored(
            self._char_frames[self._curr_char_frame_index],
            self.theme.color,
            self.theme.bg_color,
        )

    def do_your_thing(self) -> None:
        # This method should be overwritten by the inheriting classes
        pass

    # TODO: this should calculate player collision before moving ()
    def _move_by(self, vector: Vector3) -> None:
        self.position = list(add_triplet(self.position, vector))

    def is_same_position(self, entity: "Entity3D") -> bool:
        return all(a == b for a, b in zip(self.position, entity.position))

    def movement(self):
        self.position[0] += self.movMatrix[0]
        self.position[1] += self.movMatrix[1]
        self.position[2] += self.movMatrix[2]

        if self.rotate:
            self.angle[0] -= self.rotMatrix[0]
            self.angle[1] -= self.rotMatrix[1]
            self.angle[2] -= self.rotMatrix[2]

    def apply_rotations(self):
        vertexes = self.vertices

        x = self.position[0]
        y = self.position[1]
        z = self.position[2]

        aX = math.radians(self.angle[0])
        aY = math.radians(self.angle[1])
        aZ = math.radians(self.angle[2])

        # XY
        orig = []
        for i in range(len(vertexes)):
            orig.append(vertexes[i][:])

        for i in range(len(vertexes)):
            vertexes[i][0] = (orig[i][0] - x) * math.cos(aX) + (orig[i][1] - y) * math.sin(aX) + x
            vertexes[i][1] = -(orig[i][0] - x) * math.sin(aX) + (orig[i][1] - y) * math.cos(aX) + y

        # XZ
        orig = []
        for i in range(len(vertexes)):
            orig.append(vertexes[i][:])

        for i in range(len(vertexes)):
            vertexes[i][0] = (orig[i][0] - x) * math.cos(aY) + (orig[i][2] - z) * math.sin(aY) + x
            vertexes[i][2] = -(orig[i][0] - x) * math.sin(aY) + (orig[i][2] - z) * math.cos(aY) + z

        # YZ
        orig = []
        for i in range(len(vertexes)):
            orig.append(vertexes[i][:])

        for i in range(len(vertexes)):
            vertexes[i][1] = (orig[i][1] - y) * math.cos(aZ) + (orig[i][2] - z) * math.sin(aZ) + y
            vertexes[i][2] = -(orig[i][1] - y) * math.sin(aZ) + (orig[i][2] - z) * math.cos(aZ) + z

        self.vertices = vertexes


class LivingEntity3D(Entity3D):
    health: int

    def __init__(
        self,
        health: int,
        vertices: list[Point3],
        level: Optional["Level3D"] = None,
        theme: Theme | None = None,
        position=[0, 0, 0],
        size=1,
        angle=[0, 0, 0],
        movMatrix=[0, 0, 0],
        rotMatrix=[0, 0, 0],
        color: RGB = White(),
        name: str | None = None,
    ):
        Entity3D.__init__(
            self,
            vertices=vertices,
            level=level,
            theme=theme,
            position=position,
            size=size,
            angle=angle,
            movMatrix=movMatrix,
            rotMatrix=rotMatrix,
            color=color,
            name=name,
        )
        self.health = health
