import math
from abc import abstractmethod
from typing import TYPE_CHECKING, Any, Optional

from constants import EMPTY_SPACE
from factories.theme import White
from model.base import Point3, Vector3
from model.theme import RGB, Theme
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

    # How vertices in the entity interconnect between them
    # works by index, e.g.: (0, 1) <- vertex 0 connects with 1
    vertex_connections: list[tuple[int, int]]

    theme: Theme

    def __init__(
        self,
        vertices: list[Point3],
        level: Optional["Level3D"] = None,
        theme: Theme | None = None,
        position=[0, 0, 0],
        size=1,
        angle=[0, 0, 0],
        movMatrix=[0, 0, 0],
        rotMatrix=[0, 0, 0],
        color: RGB = White(),
    ):
        # x and y coordinates
        # TODO: should we keep previous state to calculate instant velocity?
        self._curr_level = level
        self._char_frames = [EMPTY_SPACE]
        self._default_char_frames = [EMPTY_SPACE]
        self._curr_char_frame_index = 0
        self.theme = theme or Theme()

        # LEGACY SHIET
        self.position = position
        self.size = size
        self.angle = angle
        self.movMatrix = movMatrix
        self.rotMatrix = rotMatrix
        self.vertices = vertices

        # For now only color
        self.theme = Theme(color=color)

    def is_lazy(self) -> bool:
        # TODO: we are bypassing this, check why the optimization is not working
        return False and self.movMatrix == [0, 0, 0] and self.rotMatrix == [0, 0, 0]

    @abstractmethod
    def get_diameter(cls) -> float:
        pass

    @abstractmethod
    def calc_v2_vertexes(self, apply: bool = False) -> list[Point3]:
        pass

    def _apply_gravity(self) -> None:
        pass
        # y_dist = self.y_distance().distance
        # y_coor = self.y_distance().y_at_target

        # if y_coor is None:
        #     return

        # # moves entity down because of gravity
        # if self.position[1] < y_coor - 1 and y_dist > 0:
        #     # TODO: check if we only need math.floor in the second part
        #     # TODO: I don't understand this code, wtf is the if condition?
        #     new_y = (
        #         y_coor - 1
        #         if self.position[1] + self.falling_velocity >= y_coor
        #         else self.position[1] + math.floor(self.falling_velocity)
        #     )

        #     self.position = (self.position[0], new_y)
        # else:
        #     self.falling_velocity = 0

        # if y_dist > 0:
        #     self.falling_velocity += GRAVITY_ACCELERATION

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
        #     round(a[0]) == round(b[0])
        #     and round(a[1]) == round(b[1])
        #     and round(a[2]) == round(b[2])
        # )

    def movement(self):
        self.position[0] += self.movMatrix[0]
        self.position[1] += self.movMatrix[1]
        self.position[2] += self.movMatrix[2]

        self.angle[0] -= self.rotMatrix[0]
        self.angle[1] -= self.rotMatrix[1]
        self.angle[2] -= self.rotMatrix[2]

    def get_render_v2_obj(self) -> Any:
        ordered_vertexes = sorted(self.vertices)

        for v in ordered_vertexes:
            pass

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

    # TODO!!!: voxels/"objVertexes" are stupid! we should trace a line from the projected point "a" to "b" and draw through the screen, averaging the colors of both halves of the pixel depending on the float
    # TODO: theoretically, with a (hopefully cheaper) second pass (once all background entities were rendered), we can achieve very pretty effects... or maybe we don't even need a second pass! e.g: if both color and bg are different, apply where it should go!!!!!
    # for the above we need the locations with decimals, befores rounding
    def calc_vertexes(self):
        pass


class LivingEntity3D(Entity3D):
    health: int

    def __init__(self, health: int, vertices: list[Any]):
        Entity3D.__init__(self, vertices=vertices)
        self.health = health
