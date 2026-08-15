import math
from typing import TYPE_CHECKING, Any, Optional

from constants import EMPTY_SPACE
from model.shared import Coord3, Vector3
from model.theme import Theme
from utils import add_triplet, colored

if TYPE_CHECKING:
    from three_d_renderer.scenario.level_3d import Level3D


# TODO: rename methods properly
# TODO: reuse the Theme types as animation types for _char frames and reuse the method to make level architecture for the change of  indices
class Entity3D:
    # _curr_level: Optional["Level3D"] = None
    position: Coord3 = [0, 0, 0]
    falling_velocity: float = 0
    # TODO: rotation_matrix missing?

    # theme: Theme

    def __init__(
        self,
        objVertexes: list[Any],
        level: Optional["Level3D"] = None,
        theme: Theme | None = None,
        position=[0, 0, 0],
        size=1,
        angle=[0, 0, 0],
        movMatrix=[0, 0, 0],
        rotMatrix=[0, 0, 0],
    ):
        # x and y coordinates
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
        self.objVertexes = objVertexes

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

    def apply_rotations(self):
        vertexes = self.objVertexes

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
            vertexes[i][0] = (
                (orig[i][0] - x) * math.cos(aX) + (orig[i][1] - y) * math.sin(aX) + x
            )
            vertexes[i][1] = (
                -(orig[i][0] - x) * math.sin(aX) + (orig[i][1] - y) * math.cos(aX) + y
            )

        # XZ
        orig = []
        for i in range(len(vertexes)):
            orig.append(vertexes[i][:])

        for i in range(len(vertexes)):
            vertexes[i][0] = (
                (orig[i][0] - x) * math.cos(aY) + (orig[i][2] - z) * math.sin(aY) + x
            )
            vertexes[i][2] = (
                -(orig[i][0] - x) * math.sin(aY) + (orig[i][2] - z) * math.cos(aY) + z
            )

        # YZ
        orig = []
        for i in range(len(vertexes)):
            orig.append(vertexes[i][:])

        for i in range(len(vertexes)):
            vertexes[i][1] = (
                (orig[i][1] - y) * math.cos(aZ) + (orig[i][2] - z) * math.sin(aZ) + y
            )
            vertexes[i][2] = (
                -(orig[i][1] - y) * math.sin(aZ) + (orig[i][2] - z) * math.cos(aZ) + z
            )

        self.objVertexes = vertexes

    def calc_vertexes(self):
        pass


class LivingEntity3D(Entity3D):
    health: int

    def __init__(self, health: int, objVertexes: list[Any]):
        Entity3D.__init__(self, objVertexes=objVertexes)
        self.health = health


################


class Cube(Entity3D):
    def __init__(self, position, size, angle, movMatrix=[0, 0, 0], rotMatrix=[0, 0, 0]):
        Entity3D.__init__(
            self, position, size, angle, movMatrix=[0, 0, 0], rotMatrix=[0, 0, 0]
        )
        self.position = position
        self.size = size
        self.angle = angle  # XY, XZ, YZ
        self.movMatrix = movMatrix
        self.rotMatrix = rotMatrix

    def calc_vertexes(self):
        vertexes = []
        x = self.position[0]
        y = self.position[1]
        z = self.position[2]
        s = self.size

        vertexes.append([x + s / 2, y + s / 2, z + s / 2])
        vertexes.append([x + s / 2, y - s / 2, z + s / 2])
        vertexes.append([x - s / 2, y + s / 2, z + s / 2])
        vertexes.append([x - s / 2, y - s / 2, z + s / 2])
        vertexes.append([x + s / 2, y + s / 2, z - s / 2])
        vertexes.append([x + s / 2, y - s / 2, z - s / 2])
        vertexes.append([x - s / 2, y + s / 2, z - s / 2])
        vertexes.append([x - s / 2, y - s / 2, z - s / 2])

        # "voxels" for the edges
        for i in range(s):
            vertexes.append([x + s / 2 - i, y + s / 2, z + s / 2])
            vertexes.append([x + s / 2, y + s / 2 - i, z + s / 2])
            vertexes.append([x + s / 2, y + s / 2, z + s / 2 - i])

            vertexes.append([x - s / 2, y + s / 2 - i, z + s / 2])
            vertexes.append([x - s / 2, y + s / 2, z + s / 2 - i])

            vertexes.append([x + s / 2 - i, y - s / 2, z + s / 2])
            vertexes.append([x + s / 2, y - s / 2, z + s / 2 - i])

            vertexes.append([x + s / 2 - i, y + s / 2, z - s / 2])
            vertexes.append([x + s / 2, y + s / 2 - i, z - s / 2])

            vertexes.append([x + s / 2 - i, y + s / 2, z - s / 2])
            vertexes.append([x + s / 2, y + s / 2 - i, z - s / 2])

            vertexes.append([x + s / 2 - i, y - s / 2, z - s / 2])
            vertexes.append([x - s / 2, y + s / 2 - i, z - s / 2])
            vertexes.append([x - s / 2, y - s / 2, z + s / 2 - i])

        self.objVertexes = vertexes
        self.apply_rotations()


################


class Tetra(Entity3D):
    def __init__(self, position, size, angle, movMatrix=[0, 0, 0], rotMatrix=[0, 0, 0]):
        Entity3D.__init__(
            self, position, size, angle, movMatrix=[0, 0, 0], rotMatrix=[0, 0, 0]
        )
        self.position = position
        self.size = size
        self.angle = angle  # XY, XZ, YZ
        self.movMatrix = movMatrix
        self.rotMatrix = rotMatrix

    def calc_vertexes(self):
        vertexes = []
        x = self.position[0]
        y = self.position[1]
        z = self.position[2]
        r = 0.707
        s = self.size

        vertexes.append([x + s, y, z - r * s])
        vertexes.append([x - s, y, z - r * s])
        vertexes.append([x, y + s, z + r * s])
        vertexes.append([x, y - s, z + r * s])

        for t in range(s * 2):
            vertexes.append([(x - s + t), (y), (z - r * s)])  # 1 - 2
            vertexes.append(
                [(x + s - t / 2), (y + t / 2), (z - r * s + r * t)]
            )  # 1 - 3
            vertexes.append(
                [(x + s - t / 2), (y - t / 2), (z - r * s + r * t)]
            )  # 1 - 4
            vertexes.append(
                [(x - s + t / 2), (y + t / 2), (z - r * s + r * t)]
            )  # 2 - 3
            vertexes.append(
                [(x - s + t / 2), (y - t / 2), (z - r * s + r * t)]
            )  # 2 - 4
            vertexes.append([(x), (y - s + t), (z + r * s)])  # 3 - 4

        self.objVertexes = vertexes
        self.apply_rotations()


################


class Ico(Entity3D):
    def __init__(self, position, size, angle, movMatrix=[0, 0, 0], rotMatrix=[0, 0, 0]):
        Entity3D.__init__(
            self, position, size, angle, movMatrix=[0, 0, 0], rotMatrix=[0, 0, 0]
        )
        self.position = position
        self.size = size
        self.angle = angle  # XY, XZ, YZ
        self.movMatrix = movMatrix
        self.rotMatrix = rotMatrix

    def calc_vertexes(self):
        vertexes = []
        x = self.position[0]
        y = self.position[1]
        z = self.position[2]
        s = self.size
        phi = 1.618

        vertexes.append([x, y + s, z + phi * s, "1"])  # vertex 1
        vertexes.append([x, y - s, z + phi * s, "2"])  # vertex 2
        vertexes.append([x, y + s, z - phi * s, "3"])  # vertex 3
        vertexes.append([x, y - s, z - phi * s, "4"])  # vertex 4

        vertexes.append([x + s, y + phi * s, z, "5"])  # vertex 5
        vertexes.append([x + s, y - phi * s, z, "6"])  # vertex 6
        vertexes.append([x - s, y + phi * s, z, "7"])  # vertex 7
        vertexes.append([x - s, y - phi * s, z, "8"])  # vertex 8

        vertexes.append([x + phi * s, y, z + s, "9"])  # vertex 9
        vertexes.append([x + phi * s, y, z - s, "X"])  # vertex 10
        vertexes.append([x - phi * s, y, z + s, "J"])  # vertex 11
        vertexes.append([x - phi * s, y, z - s, "Q"])  # vertex 12

        # edges of icosahedron
        for t in range(s):
            vertexes.append([(x), (y + s - 2 * t), (z + phi * s), "."])  # vertex 1 - 2
            vertexes.append(
                [(x + t), (y + s - t * (1 - phi)), (z + phi * s - phi * t), "."]
            )  # vertex 1 - 5
            vertexes.append(
                [(x - t), (y + s - t * (1 - phi)), (z + phi * s - phi * t), "."]
            )  # vertex 1 - 7
            vertexes.append(
                [(x + phi * t), (y + s - t), (z + phi * s - t * (phi - 1)), "."]
            )  # vertex 1 - 9
            vertexes.append(
                [(x - phi * t), (y + s - t), (z + phi * s - t * (phi - 1)), "."]
            )  # vertex 1 - 11

            vertexes.append(
                [(x + phi * t), (y - s + t), (z + phi * s - t * (phi - 1)), "."]
            )  # vertex 2 - 9
            vertexes.append(
                [(x + t), (y - s + t * (1 - phi)), (z + phi * s - phi * t), "."]
            )  # vertex 2 - 6
            vertexes.append(
                [(x - t), (y - s + t * (1 - phi)), (z + phi * s - phi * t), "."]
            )  # vertex 2 - 8
            vertexes.append(
                [(x - phi * t), (y - s + t), (z + phi * s - t * (phi - 1)), "."]
            )  # vertex 2 - 11

            vertexes.append(
                [(x + t), (y + s - t * (1 - phi)), (z - phi * s + phi * t), "."]
            )  # vertex 3 - 5
            vertexes.append([(x), (y + s - 2 * t), (z - phi * s), "."])  # vertex 3 - 4
            vertexes.append(
                [(x - t), (y + s - t * (1 - phi)), (z - phi * s + phi * t), "."]
            )  # vertex 3 - 7
            vertexes.append(
                [(x + phi * t), (y + s - t), (z - phi * s + t * (phi - 1)), "."]
            )  # vertex 3 - 10
            vertexes.append(
                [(x - phi * t), (y + s - t), (z - phi * s + t * (phi - 1)), "."]
            )  # vertex 3 - 12

            vertexes.append(
                [(x + t), (y - s + t * (1 - phi)), (z - phi * s + phi * t), "."]
            )  # vertex 4 - 6
            vertexes.append(
                [(x - t), (y - s + t * (1 - phi)), (z - phi * s + phi * t), "."]
            )  # vertex 4 - 8
            vertexes.append(
                [(x + phi * t), (y - s + t), (z - phi * s + t * (phi - 1)), "."]
            )  # vertex 4 - 10
            vertexes.append(
                [(x - phi * t), (y - s + t), (z - phi * s + t * (phi - 1)), "."]
            )  # vertex 4 - 12

            vertexes.append([(x + s - 2 * t), (y + phi * s), (z), "."])  # vertex 5 - 7
            vertexes.append(
                [(x + s - t * (1 - phi)), (y + phi * s - phi * t), (z + t), "."]
            )  # vertex 5 - 9
            vertexes.append(
                [(x + s - t * (1 - phi)), (y + phi * s - phi * t), (z - t), "."]
            )  # vertex 5 - 10

            vertexes.append([(x + s - 2 * t), (y - phi * s), (z), "."])  # vertex 6 - 8
            vertexes.append(
                [(x + s - t * (1 - phi)), (y - phi * s + phi * t), (z + t), "."]
            )  # vertex 6 - 9
            vertexes.append(
                [(x + s - t * (1 - phi)), (y - phi * s + phi * t), (z - t), "."]
            )  # vertex 6 - 10

            vertexes.append(
                [(x - s + t * (1 - phi)), (y + phi * s - phi * t), (z + t), "."]
            )  # vertex 7 - 11
            vertexes.append(
                [(x - s + t * (1 - phi)), (y + phi * s - phi * t), (z - t), "."]
            )  # vertex 7 - 12

            vertexes.append(
                [(x - s + t * (1 - phi)), (y - phi * s + phi * t), (z + t), "."]
            )  # vertex 8 - 11
            vertexes.append(
                [(x - s + t * (1 - phi)), (y - phi * s + phi * t), (z - t), "."]
            )  # vertex 8 - 12

            vertexes.append([(x + phi * s), (y), (z + s - 2 * t), "."])  # vertex 9 - 10

            vertexes.append(
                [(x - phi * s), (y), (z + s - 2 * t), "."]
            )  # vertex 11 - 12

        self.objVertexes = vertexes
        self.apply_rotations()


################


class Dodeca(Entity3D):
    def __init__(self, position, size, angle, movMatrix=[0, 0, 0], rotMatrix=[0, 0, 0]):
        Entity3D.__init__(
            self, position, size, angle, movMatrix=[0, 0, 0], rotMatrix=[0, 0, 0]
        )
        self.position = position
        self.size = size
        self.angle = angle  # XY, XZ, YZ
        self.movMatrix = movMatrix
        self.rotMatrix = rotMatrix

    def calc_vertexes(self):
        vertexes = []
        x = self.position[0]
        y = self.position[1]
        z = self.position[2]
        s = self.size
        phi = 1.618
        iphi = 0.618

        vertexes.append([x + s, y + s, z + s, "1"])  # vertex 1
        vertexes.append([x + s, y - s, z + s, "2"])  # vertex 2
        vertexes.append([x + s, y + s, z - s, "3"])  # vertex 3
        vertexes.append([x + s, y - s, z - s, "4"])  # vertex 4
        vertexes.append([x - s, y + s, z + s, "5"])  # vertex 5
        vertexes.append([x - s, y - s, z + s, "6"])  # vertex 6
        vertexes.append([x - s, y + s, z - s, "7"])  # vertex 7
        vertexes.append([x - s, y - s, z - s, "8"])  # vertex 8

        vertexes.append([x, y + phi * s, z + iphi * s, "9"])  # vertex 9
        vertexes.append([x, y - phi * s, z + iphi * s, "A"])  # vertex 10
        vertexes.append([x, y + phi * s, z - iphi * s, "B"])  # vertex 11
        vertexes.append([x, y - phi * s, z - iphi * s, "C"])  # vertex 12

        vertexes.append([x + iphi * s, y, z + phi * s, "D"])  # vertex 13
        vertexes.append([x + iphi * s, y, z - phi * s, "E"])  # vertex 14
        vertexes.append([x - iphi * s, y, z + phi * s, "F"])  # vertex 15
        vertexes.append([x - iphi * s, y, z - phi * s, "G"])  # vertex 16

        vertexes.append([x + phi * s, y + iphi * s, z, "H"])  # vertex 17
        vertexes.append([x + phi * s, y - iphi * s, z, "I"])  # vertex 18
        vertexes.append([x - phi * s, y + iphi * s, z, "J"])  # vertex 19
        vertexes.append([x - phi * s, y - iphi * s, z, "K"])  # vertex 20

        # edges of dodecahedron
        for t in range(s):
            vertexes.append(
                [(x + s - t), (y + s - t * (1 - phi)), (z + s - t * (1 - iphi)), "."]
            )  # vertex 1 - 9
            vertexes.append(
                [(x + s - t * (1 - iphi)), (y + s - t), (z + s - t * (1 - phi)), "."]
            )  # vertex 1 - 13
            vertexes.append(
                [(x + s - t * (1 - phi)), (y + s - t * (1 - iphi)), (z + s - t), "."]
            )  # vertex 1 - 17

            vertexes.append(
                [(x + s - t), (y - s + t * (1 - phi)), (z + s - t * (1 - iphi)), "."]
            )  # vertex 2 - 10
            vertexes.append(
                [(x + s - t * (1 - iphi)), (y - s + t), (z + s - t * (1 - phi)), "."]
            )  # vertex 2 - 13
            vertexes.append(
                [(x + s - t * (1 - phi)), (y - s + t * (1 - iphi)), (z + s - t), "."]
            )  # vertex 2 - 18 3HBE

            vertexes.append(
                [(x + s - t), (y + s - t * (1 - phi)), (z - s + t * (1 - iphi)), "."]
            )  # vertex 3 - 11
            vertexes.append(
                [(x + s - t * (1 - iphi)), (y + s - t), (z - s + t * (1 - phi)), "."]
            )  # vertex 3 - 14
            vertexes.append(
                [(x + s - t * (1 - phi)), (y + s - t * (1 - iphi)), (z - s + t), "."]
            )  # vertex 3 - 17 4CEI

            vertexes.append(
                [(x + s - t), (y - s + t * (1 - phi)), (z - s + t * (1 - iphi)), "."]
            )  # vertex 4 - 12
            vertexes.append(
                [(x + s - t * (1 - iphi)), (y - s + t), (z - s + t * (1 - phi)), "."]
            )  # vertex 4 - 14
            vertexes.append(
                [(x + s - t * (1 - phi)), (y - s + t * (1 - iphi)), (z - s + t), "."]
            )  # vertex 4 - 18 59FJ

            vertexes.append(
                [(x - s + t), (y + s - t * (1 - phi)), (z + s - t * (1 - iphi)), "."]
            )  # vertex 5 - 9
            vertexes.append(
                [(x - s + t * (1 - iphi)), (y + s - t), (z + s - t * (1 - phi)), "."]
            )  # vertex 5 - 15
            vertexes.append(
                [(x - s + t * (1 - phi)), (y + s - t * (1 - iphi)), (z + s - t), "."]
            )  # vertex 5 - 19 6AFK

            vertexes.append(
                [(x - s + t), (y - s + t * (1 - phi)), (z + s - t * (1 - iphi)), "."]
            )  # vertex 6 - 10
            vertexes.append(
                [(x - s + t * (1 - iphi)), (y - s + t), (z + s - t * (1 - phi)), "."]
            )  # vertex 6 - 15
            vertexes.append(
                [(x - s + t * (1 - phi)), (y - s + t * (1 - iphi)), (z + s - t), "."]
            )  # vertex 6 - 20 7BGJ

            vertexes.append(
                [(x - s + t), (y + s - t * (1 - phi)), (z - s + t * (1 - iphi)), "."]
            )  # vertex 7 - 11
            vertexes.append(
                [(x - s + t * (1 - iphi)), (y + s - t), (z - s + t * (1 - phi)), "."]
            )  # vertex 7 - 16
            vertexes.append(
                [(x - s + t * (1 - phi)), (y + s - t * (1 - iphi)), (z - s + t), "."]
            )  # vertex 7 - 19 8CGK

            vertexes.append(
                [(x - s + t), (y - s + t * (1 - phi)), (z - s + t * (1 - iphi)), "."]
            )  # vertex 8 - 12
            vertexes.append(
                [(x - s + t * (1 - iphi)), (y - s + t), (z - s + t * (1 - phi)), "."]
            )  # vertex 8 - 16
            vertexes.append(
                [(x - s + t * (1 - phi)), (y - s + t * (1 - iphi)), (z - s + t), "."]
            )  # vertex 8 - 20

            vertexes.append(
                [(x), (y + phi * s), (z + iphi * s - 2 * iphi * t), "."]
            )  # vertex 9 - 11
            vertexes.append(
                [(x), (y - phi * s), (z + iphi * s - 2 * iphi * t), "."]
            )  # vertex 10 - 12
            vertexes.append(
                [(x + iphi * s - 2 * iphi * t), (y), (z - phi * s), "."]
            )  # vertex 13 - 15
            vertexes.append(
                [(x + iphi * s - 2 * iphi * t), (y), (z + phi * s), "."]
            )  # vertex 14 - 16
            vertexes.append(
                [(x + phi * s), (y + iphi * s - 2 * iphi * t), (z), "."]
            )  # vertex 17 - 18
            vertexes.append(
                [(x - phi * s), (y + iphi * s - 2 * iphi * t), (z), "."]
            )  # vertex 19 - 20

        self.objVertexes = vertexes
        self.apply_rotations()
