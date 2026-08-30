import math
from abc import abstractmethod
from typing import TYPE_CHECKING, Optional

from factories.theme import White
from model.base import Point3F, Vector3F
from model.theme import EMPTY_SPACE, RGB, Theme
from utils import add_triplet, colored, subtract_triplet

if TYPE_CHECKING:
    from three_d_renderer.scenario.level_3d import Level3D

# TODO: reuse the Theme types as animation types for _char frames and reuse the method to make level architecture for the change of  indices


class Entity3D:
    _position: Point3F = (0, 0, 0)
    falling_velocity: float = 0
    vertices: list[Point3F]
    mov_vector: Vector3F
    rot_vector: Vector3F
    rotate: bool

    # How vertices in the entity interconnect between them
    # works by index, e.g.: (0, 1) <- vertex 0 connects with 1
    vertex_connections: list[tuple[int, int]]

    theme: Theme

    name: str | None

    def __init__(
        self,
        vertices: list[Point3F],
        level: Optional["Level3D"] = None,
        theme: Theme | None = None,
        position: Point3F = (0, 0, 0),
        size: float = 1,
        angle: Point3F = (0, 0, 0),
        mov_vector: Vector3F = (0, 0, 0),
        rot_vector: Vector3F = (0, 0, 0),
        color: RGB = White(),
        name: str | None = None,
    ):
        # x and y coordinates
        # TODO: should we keep previous state to calculate instant velocity?
        self._curr_level = level
        self._char_frames = [EMPTY_SPACE]
        self._default_char_frames = [EMPTY_SPACE]
        self._curr_char_frame_index = 0
        self._position = position
        self.size = size
        self.angle = angle
        self.mov_vector = mov_vector
        self.rot_vector = rot_vector
        self.vertices = vertices
        self.name = name
        self.rotate = rot_vector is not None

        # For now only color
        # self.theme = theme or Theme()
        self.theme = Theme(color=color)

    def is_lazy(self) -> bool:
        # TODO: we are bypassing this, check why the optimization is not working
        return False and self.mov_vector == (0, 0, 0) and self.rot_vector == (0, 0, 0)

    @abstractmethod
    def do_your_thing(cls) -> None:
        # This method should be overwritten by the inheriting classes
        pass

    @abstractmethod
    def get_diameter(cls) -> float:
        pass

    @abstractmethod
    def calc_main_vertices(self, apply: bool = False) -> list[Point3F]:
        pass

    @abstractmethod
    def calc_legacy_voxels(self, apply: bool = False) -> list[Point3F]:
        pass

    def _apply_gravity(self) -> None:
        raise NotImplementedError("No gravity support yet")

    def get_char(self) -> str:
        return colored(
            self._char_frames[self._curr_char_frame_index],
            self.theme.color,
            self.theme.bg_color,
        )

    # TODO: this should calculate player collision before moving ()
    def move_by(self, vector: Vector3F) -> None:
        self._position = add_triplet(self._position, vector)

    def move_to(self, new_position: Vector3F) -> None:
        self._position = new_position

    def is_same_position(self, entity: "Entity3D") -> bool:
        return all(a == b for a, b in zip(self._position, entity._position))

    def movement(self):
        self._position = add_triplet(self._position, self.mov_vector)

        if self.rotate:
            self.angle = subtract_triplet(self.angle, self.rot_vector)

        self.apply_rotations()

    def apply_rotations(self):
        vertexes = self.vertices

        x, y, z = self._position

        a_x = math.radians(self.angle[0])
        a_y = math.radians(self.angle[1])
        a_z = math.radians(self.angle[2])

        # XY
        # TODO: find out, wtf is this step for?
        orig = []
        for i in range(len(vertexes)):
            orig.append(vertexes[i][:])

        for i in range(len(vertexes)):
            new_x = (orig[i][0] - x) * math.cos(a_x) + (orig[i][1] - y) * math.sin(a_x) + x
            new_y = -(orig[i][0] - x) * math.sin(a_x) + (orig[i][1] - y) * math.cos(a_x) + y
            vertexes[i] = (new_x, new_y, vertexes[i][2])

        # XZ
        orig = []
        for i in range(len(vertexes)):
            orig.append(vertexes[i][:])

        for i in range(len(vertexes)):
            new_x = (orig[i][0] - x) * math.cos(a_y) + (orig[i][2] - z) * math.sin(a_y) + x
            new_z = -(orig[i][0] - x) * math.sin(a_y) + (orig[i][2] - z) * math.cos(a_y) + z
            vertexes[i] = (new_x, vertexes[i][1], new_z)

        # YZ
        orig = []
        for i in range(len(vertexes)):
            orig.append(vertexes[i][:])

        for i in range(len(vertexes)):
            new_y = (orig[i][1] - y) * math.cos(a_z) + (orig[i][2] - z) * math.sin(a_z) + y
            new_z = -(orig[i][1] - y) * math.sin(a_z) + (orig[i][2] - z) * math.cos(a_z) + z
            vertexes[i] = (vertexes[i][0], new_y, new_z)

        self.vertices = vertexes


class LivingEntity3D(Entity3D):
    health: int

    def __init__(
        self,
        health: int,
        vertices: list[Point3F],
        level: Optional["Level3D"] = None,
        theme: Theme | None = None,
        position=(0, 0, 0),
        size=1,
        angle=(0, 0, 0),
        mov_vector=(0, 0, 0),
        rot_vector=(0, 0, 0),
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
            mov_vector=mov_vector,
            rot_vector=rot_vector,
            color=color,
            name=name,
        )
        self.health = health
